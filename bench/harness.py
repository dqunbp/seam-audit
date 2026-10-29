"""Benchmark plumbing: prepare an isolated repo, run an agent on it, grade the result."""
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

BENCH = Path(__file__).resolve().parent
ROOT = BENCH.parent
FIXTURE = BENCH / "fixture"
TASKS = ["upscale", "video_webhook", "free_quota"]

SKILLS = {
    "seam-audit": ROOT / "SKILL.md",
    "careful-dev": BENCH / "conditions" / "careful-dev" / "SKILL.md",
}

# condition -> (skill to install or None, line appended to the task prompt)
CONDITIONS = {
    "baseline": (None, ""),
    "skill": ("seam-audit", "Before you start, use the `seam-audit` skill."),
    "placebo": ("careful-dev", "Before you start, use the `careful-dev` skill."),
    "skill_auto": ("seam-audit", ""),  # installed but not mentioned: does it trigger by itself?
}

AGENT_TOOLS = "Read,Edit,Write,Glob,Grep,Bash,Skill"
AGENT_ALLOWED = [
    "Read", "Edit", "Write", "Glob", "Grep", "Skill",
    "Bash(python -m pytest:*)", "Bash(python3 -m pytest:*)", "Bash(pytest:*)",
    "Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(tail:*)", "Bash(wc:*)",
    "Bash(grep:*)", "Bash(find:*)", "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)",
]
# Account-synced plugins and MCP connectors must not leak into benchmark runs.
AGENT_SETTINGS = {"enabledPlugins": {"productivity@synced": False, "small-business@synced": False}}


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.name=bench", "-c", "user.email=bench@localhost", *args],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout


def prepare_repo(dest: Path, condition: str) -> Path:
    """Copy the fixture to dest/repo as a fresh git repo and install the condition's skill."""
    repo = dest / "repo"
    shutil.copytree(FIXTURE, repo, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "pixforge 0.7.0")
    (repo / ".git" / "info" / "exclude").write_text(".claude/\ntests_hidden/\n__pycache__/\n.pytest_cache/\n")
    skill, _ = CONDITIONS[condition]
    if skill:
        target = repo / ".claude" / "skills" / skill
        target.mkdir(parents=True)
        shutil.copy(SKILLS[skill], target / "SKILL.md")
    return repo


def task_prompt(task: str, condition: str) -> str:
    prompt = (BENCH / "tasks" / task / "prompt.md").read_text().strip()
    _, suffix = CONDITIONS[condition]
    return f"{prompt}\n\n{suffix}" if suffix else prompt


def agent_env(home: Path, venv_bin: Path) -> dict:
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["PATH"] = f"{venv_bin}{os.pathsep}{env['PATH']}"
    env.pop("VIRTUAL_ENV", None)
    return env


def run_agent(repo: Path, prompt: str, model: str, transcript: Path, env: dict,
              effort: str | None = None, budget_usd: float = 5.0, timeout_s: int = 1800) -> int:
    cmd = [
        "claude", "-p", prompt,
        "--model", model,
        "--output-format", "stream-json", "--verbose",
        "--tools", AGENT_TOOLS,
        "--permission-mode", "acceptEdits",
        "--allowedTools", *AGENT_ALLOWED,
        "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
        "--settings", json.dumps(AGENT_SETTINGS),
        "--max-budget-usd", str(budget_usd),
    ]
    if effort:
        cmd += ["--effort", effort]
    with transcript.open("w") as out:
        try:
            proc = subprocess.run(cmd, cwd=repo, env=env, stdout=out, stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL, timeout=timeout_s)
            return proc.returncode
        except subprocess.TimeoutExpired:
            return -1


# --- grading -------------------------------------------------------------------

def _junit(path: Path) -> dict[str, bool]:
    if not path.exists():
        return {}
    results = {}
    for case in ET.parse(path).getroot().iter("testcase"):
        failed = any(child.tag in ("failure", "error", "skipped") for child in case)
        results[case.get("name")] = not failed
    return results


def _pytest(repo: Path, target: str, junit: Path, env: dict) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["python", "-m", "pytest", target, "-q", "-p", "no:cacheprovider", "-o", "addopts=",
             f"--junitxml={junit}"],
            cwd=repo, env=env, capture_output=True, text=True, timeout=300,
        )
        return proc.returncode, proc.stdout[-4000:]
    except subprocess.TimeoutExpired:
        return -1, "timeout"


def install_hidden_tests(repo: Path, task: str) -> None:
    hidden = repo / "tests_hidden"
    if hidden.exists():
        shutil.rmtree(hidden)
    hidden.mkdir()
    (hidden / "__init__.py").write_text("")
    shutil.copy(BENCH / "hidden" / "conftest.py", hidden / "conftest.py")
    for test in (BENCH / "hidden" / task).glob("test_*.py"):
        shutil.copy(test, hidden / test.name)
    shutil.copytree(FIXTURE / "pixforge" / "migrations", hidden / "orig_migrations")


def grade(repo: Path, task: str, out_dir: Path, env: dict) -> dict:
    install_hidden_tests(repo, task)
    hidden_rc, hidden_log = _pytest(repo, "tests_hidden", out_dir / "hidden.xml", env)
    shutil.rmtree(repo / "tests_hidden")
    visible_rc, visible_log = _pytest(repo, "tests", out_dir / "visible.xml", env)
    hidden = _junit(out_dir / "hidden.xml")
    visible = _junit(out_dir / "visible.xml")
    (out_dir / "pytest_hidden.log").write_text(hidden_log)
    (out_dir / "pytest_visible.log").write_text(visible_log)
    _git(repo, "add", "-A")
    diff = _git(repo, "diff", "--cached", "HEAD")
    (out_dir / "diff.patch").write_text(diff)
    return {
        "hidden": hidden,
        "hidden_passed": sum(hidden.values()),
        "hidden_total": len(hidden),
        "visible_green": visible_rc == 0,
        "visible_passed": sum(visible.values()),
        "visible_total": len(visible),
        "diff_lines": sum(1 for line in diff.splitlines() if line[:1] in "+-" and line[:3] not in ("+++", "---")),
    }


# --- transcript metrics ------------------------------------------------------------

SEAM_TABLE = re.compile(r"\|\s*Seam\s*\|.*\|\s*Evidence", re.IGNORECASE)


def transcript_metrics(transcript: Path, repo: Path) -> dict:
    tools: dict[str, int] = {}
    files_read: set[str] = set()
    skills: list[str] = []
    bash: list[str] = []
    text_parts: list[str] = []
    result: dict = {}
    for line in transcript.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "result":
            result = event
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content", []):
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            if block.get("type") != "tool_use":
                continue
            name, args = block.get("name"), block.get("input", {})
            tools[name] = tools.get(name, 0) + 1
            if name == "Read" and args.get("file_path"):
                path = Path(args["file_path"])
                try:
                    files_read.add(str(path.resolve().relative_to(repo.resolve())))
                except ValueError:
                    files_read.add(str(path))
            elif name == "Skill":
                skills.append(args.get("skill") or args.get("command") or json.dumps(args))
            elif name == "Bash":
                bash.append(args.get("command", ""))
    text = "\n".join(text_parts)
    return {
        "cost_usd": result.get("total_cost_usd"),
        "num_turns": result.get("num_turns"),
        "duration_s": round((result.get("duration_ms") or 0) / 1000, 1),
        "result_subtype": result.get("subtype"),
        "is_error": result.get("is_error"),
        "tools": tools,
        "files_read": sorted(files_read),
        "skills_invoked": skills,
        "bash_commands": bash,
        "seam_table": bool(SEAM_TABLE.search(text)),
        "output_chars": len(text),
    }
