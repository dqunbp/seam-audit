#!/usr/bin/env python3
"""Sanity-check the benchmark itself, without any agent.

For each task: the reference solution must pass every hidden test and keep the
visible suite green; the untouched fixture shows which hidden tests pass for free.

    python3 bench/validate.py --suite basic --venv /path/to/venv-with-pytest --workdir /tmp/seam-validate
"""
import argparse
import shutil
from pathlib import Path

from harness import TASKS, agent_env, grade, prepare_repo, suite_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="basic")
    parser.add_argument("--venv", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    args = parser.parse_args()
    suite = suite_dir(args.suite)
    env = agent_env(Path.home(), args.venv / "bin")
    ok = True
    for task in TASKS:
        for variant in ("untouched", "reference"):
            dest = args.workdir / task / variant
            shutil.rmtree(dest, ignore_errors=True)
            dest.mkdir(parents=True)
            repo = prepare_repo(dest, "baseline", suite)
            if variant == "reference":
                shutil.copytree(suite / "reference" / task, repo, dirs_exist_ok=True)
            g = grade(repo, task, dest, env, suite)
            failing = [name for name, passed in g["hidden"].items() if not passed]
            passing = [name for name, passed in g["hidden"].items() if passed]
            print(f"{task:14} {variant:9} hidden {g['hidden_passed']}/{g['hidden_total']}"
                  f"  visible_green={g['visible_green']}")
            if variant == "reference":
                if failing or not g["visible_green"] or not g["hidden_total"]:
                    ok = False
                    print("   FAILING:", failing)
            else:
                print("   passes for free:", passing)
    print("OK" if ok else "VALIDATION FAILED")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
