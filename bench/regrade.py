#!/usr/bin/env python3
"""Re-grade finished runs from their saved diff.patch, without re-running the agent.

Use it after fixing the grading itself (hidden tests, harness). Each run's diff is
applied to a fresh copy of its fixture and graded again; result.json is updated.

    python3 bench/regrade.py --venv /path/to/venv --workdir /tmp/seam-regrade \
        bench/results/pretix-probe-haiku/haiku/cancel_order/baseline/r1
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

from harness import agent_env, grade, prepare_repo, suite_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--venv", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("runs", type=Path, nargs="+", help="run directories containing result.json and diff.patch")
    args = parser.parse_args()
    env = agent_env(Path.home(), args.venv / "bin")
    for run in (r.resolve() for r in args.runs):
        result = json.loads((run / "result.json").read_text())
        suite = suite_dir(result.get("suite", "basic"))
        dest = args.workdir / result["run_id"]
        shutil.rmtree(dest, ignore_errors=True)
        dest.mkdir(parents=True)
        repo = prepare_repo(dest, "baseline", suite, result["task"])
        diff = (run / "diff.patch").read_text()
        if diff.strip():
            subprocess.run(["git", "apply", "--whitespace=nowarn", "-"], cwd=repo, input=diff, text=True, check=True)
        result.update(grade(repo, result["task"], run, env, suite))
        (run / "result.json").write_text(json.dumps(result, indent=2))
        shutil.rmtree(dest, ignore_errors=True)
        print(f"{result['run_id']}: hidden {result['hidden_passed']}/{result['hidden_total']}"
              f" visible_green={result['visible_green']}")


if __name__ == "__main__":
    main()
