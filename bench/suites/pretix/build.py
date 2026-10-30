#!/usr/bin/env python3
"""Build the pretix suite's per-task fixtures from a pretix checkout.

Each task removes one real service function from pretix, together with the
maintainers' tests for it. The removed tests become the hidden tests; the
original files are kept for grading and for the reference check.

    git clone https://github.com/pretix/pretix.git /tmp/pretix
    git -C /tmp/pretix checkout e6f8f178aff537bc32dc7359a5f561b8074a269b
    python3 bench/suites/pretix/build.py --pretix /tmp/pretix --out /tmp/pretix-fixtures

This writes /tmp/pretix-fixtures/<task>/ (the agent's starting repo) and
/tmp/pretix-fixtures/_original/ (untouched copies of the files a task edits),
and points bench/suites/pretix/fixtures at --out.
"""
import argparse
import ast
import json
import shutil
import subprocess
from pathlib import Path

SUITE = Path(__file__).resolve().parent
PINNED = "e6f8f178aff537bc32dc7359a5f561b8074a269b"
SERVICES = "src/pretix/base/services/orders.py"


def _span(node) -> tuple[int, int]:
    start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    return start, node.end_lineno


def remove_definitions(path: Path, names: list[str]) -> None:
    """Delete top-level functions/classes and class methods ("Class.method") from a module."""
    source = path.read_text()
    tree = ast.parse(source)
    spans = []
    for name in names:
        cls, _, meth = name.partition(".")
        found = None
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == cls:
                found = node
                if meth:
                    found = next(n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == meth)
        if found is None:
            raise SystemExit(f"{path}: {name} not found")
        spans.append(_span(found))
    lines = source.splitlines(keepends=True)
    for start, end in sorted(spans, reverse=True):
        del lines[start - 1:end]
    path.write_text(_squeeze_blank_lines("".join(lines)))


def remove_import_names(path: Path, module: str, names: set[str]) -> None:
    """Drop `names` from `from <module> import (...)` statements."""
    source = path.read_text()
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    for node in sorted(tree.body, key=lambda n: n.lineno, reverse=True):
        if isinstance(node, ast.ImportFrom) and node.module == module and any(a.name in names for a in node.names):
            kept = [a.name for a in node.names if a.name not in names]
            text = f"from {module} import (\n{_wrap(kept)})\n" if kept else ""
            lines[node.lineno - 1:node.end_lineno] = [text]
    path.write_text("".join(lines))


def _wrap(names: list[str], width: int = 79) -> str:
    """isort-style wrapped import body: 4-space indent, trailing commas."""
    out, line = [], "   "
    for name in names:
        if len(line) + len(name) + 2 > width:
            out.append(line + "\n")
            line = "   "
        line += f" {name},"
    return "".join(out) + line + "\n"


def _squeeze_blank_lines(text: str) -> str:
    out, blank = [], 0
    for line in text.splitlines(keepends=True):
        blank = blank + 1 if not line.strip() else 0
        if blank <= 2:
            out.append(line)
    return "".join(out)


def build_task(pretix: Path, out: Path, task: str, spec: dict) -> None:
    dest = out / task
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(pretix, dest, symlinks=True,
                    ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__", ".pytest_cache"))
    module = spec.get("module", SERVICES)
    remove_definitions(dest / module, [spec["function"]])
    dotted = module.removeprefix("src/").removesuffix(".py").replace("/", ".")
    for test_file, names in spec["remove_tests"].items():
        remove_definitions(dest / test_file, names)
        remove_import_names(dest / test_file, dotted, {spec["function"]})
    print(f"built {dest}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretix", type=Path, required=True, help="pretix git checkout")
    parser.add_argument("--out", type=Path, required=True, help="where to write fixtures (outside this repo)")
    args = parser.parse_args()
    head = subprocess.run(["git", "-C", str(args.pretix), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    if head != PINNED:
        raise SystemExit(f"pretix checkout is at {head}, expected {PINNED}")

    config = json.loads((SUITE / "suite.json").read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    original = args.out / "_original"
    for task, spec in config["tasks"].items():
        build_task(args.pretix, args.out, task, spec)
        for rel in [spec.get("module", SERVICES), *spec["remove_tests"]]:
            (original / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(args.pretix / rel, original / rel)

    link = SUITE / "fixtures"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(args.out.resolve(), target_is_directory=True)
    print(f"linked {link} -> {args.out}")


if __name__ == "__main__":
    main()
