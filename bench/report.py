#!/usr/bin/env python3
"""Summarize result.json files into a Markdown report.

    python3 bench/report.py bench/results/pilot-haiku > bench/results/pilot-haiku/REPORT.md
"""
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from harness import CONDITIONS, TASKS


def mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else float("nan")


def sd(xs):
    xs = [x for x in xs if x is not None]
    return statistics.stdev(xs) if len(xs) > 1 else 0.0


def main():
    root = Path(sys.argv[1])
    runs = [json.loads(p.read_text()) for p in sorted(root.rglob("result.json"))]
    if not runs:
        raise SystemExit("no results")
    models = sorted({r["model"] for r in runs})
    conditions = [c for c in CONDITIONS if any(r["condition"] == c for r in runs)]
    tasks = [t for t in TASKS if any(r["task"] == t for r in runs)]
    cell = defaultdict(list)
    for r in runs:
        cell[(r["model"], r["task"], r["condition"])].append(r)

    print(f"# Seam-audit benchmark — {root.name}\n")
    print(f"{len(runs)} runs. Score = share of hidden trap tests passed (mean ± sd over repetitions).\n")

    for model in models:
        print(f"## {model}\n")
        print("| task | " + " | ".join(conditions) + " |")
        print("|---|" + "---|" * len(conditions))
        overall = defaultdict(list)
        for task in tasks:
            row = []
            for c in conditions:
                rs = cell[(model, task, c)]
                scores = [r["hidden_passed"] / r["hidden_total"] for r in rs if r["hidden_total"]]
                overall[c] += scores
                row.append(f"{mean(scores):.0%} ± {sd(scores):.0%} (n={len(scores)})" if scores else "—")
            print(f"| {task} | " + " | ".join(row) + " |")
        print("| **all** | " + " | ".join(f"**{mean(overall[c]):.0%}**" for c in conditions) + " |\n")

        print("| metric (mean per run) | " + " | ".join(conditions) + " |")
        print("|---|" + "---|" * len(conditions))
        metrics = {
            "visible suite green": lambda r: float(r["visible_green"]),
            "cost, $": lambda r: r.get("cost_usd"),
            "turns": lambda r: r.get("num_turns"),
            "files read": lambda r: len(r.get("files_read", [])),
            "diff lines": lambda r: r.get("diff_lines"),
            "skill invoked": lambda r: float(bool(r.get("skills_invoked"))),
            "seam table in output": lambda r: float(r.get("seam_table", False)),
        }
        for name, fn in metrics.items():
            vals = []
            for c in conditions:
                xs = [fn(r) for task in tasks for r in cell[(model, task, c)]]
                v = mean(xs)
                vals.append(f"{v:.0%}" if name in ("visible suite green", "skill invoked", "seam table in output")
                            else f"{v:.2f}" if name == "cost, $" else f"{v:.1f}")
            print(f"| {name} | " + " | ".join(vals) + " |")
        print()

        print("### Per-trap pass rate\n")
        for task in tasks:
            names = []
            for c in conditions:
                for r in cell[(model, task, c)]:
                    names += [n for n in r["hidden"] if n not in names]
            print(f"**{task}**\n")
            print("| trap | " + " | ".join(conditions) + " |")
            print("|---|" + "---|" * len(conditions))
            for n in names:
                row = []
                for c in conditions:
                    rs = cell[(model, task, c)]
                    passed = sum(1 for r in rs if r["hidden"].get(n))
                    row.append(f"{passed}/{len(rs)}")
                print(f"| `{n.removeprefix('test_')}` | " + " | ".join(row) + " |")
            print()


if __name__ == "__main__":
    main()
