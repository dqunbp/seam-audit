#!/usr/bin/env python3
"""Analysis of the pre-registered v2 test (see results/v2-heldout-haiku/PREREGISTRATION.md).

    python3 bench/analyze_v2.py > bench/results/v2-heldout-haiku/ANALYSIS.md
"""
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

from analyze_confirm import SUBTLE

RESULTS = Path(__file__).resolve().parent / "results"
HELDOUT_DIR = RESULTS / "v2-heldout-haiku" / "stage-b"
DEV_DIRS = [RESULTS / "confirm-haiku", RESULTS / "v2-heldout-haiku" / "dev"]
HELDOUT = ["validate_memberships_in_order", "run_scheduled_exports", "assign_automatically"]
DEV = ["send_download_reminders", "send_expiry_warnings"]
PERMUTATIONS = 20_000


def load(dirs) -> list[dict]:
    runs = []
    for d in dirs:
        runs += [json.loads(p.read_text()) for p in sorted(Path(d).rglob("result.json"))] if Path(d).exists() else []
    return runs


def share(run: dict) -> float:
    return run["hidden_passed"] / run["hidden_total"]


def subtle(run: dict) -> int:
    names = SUBTLE[run["task"]]
    return sum(1 for key, ok in run["hidden"].items() if ok and key.split("::")[-1] in names)


def permutation_p(runs, a, b, metric, tasks) -> tuple[float, float, int, int]:
    """One-sided (a > b) test of the mean per-run metric, permuting labels within each task."""
    strata = {t: {a: [metric(r) for r in runs if r["task"] == t and r["condition"] == a],
                  b: [metric(r) for r in runs if r["task"] == t and r["condition"] == b]} for t in tasks}
    strata = {t: g for t, g in strata.items() if g[a] and g[b]}
    if not strata:
        return float("nan"), float("nan"), 0, 0

    def diff(groups):
        xs = [v for g in groups.values() for v in g[a]]
        ys = [v for g in groups.values() for v in g[b]]
        return statistics.mean(xs) - statistics.mean(ys)

    observed = diff(strata)
    rng = random.Random(0)
    extreme = 0
    for _ in range(PERMUTATIONS):
        shuffled = {}
        for t, g in strata.items():
            pool = g[a] + g[b]
            rng.shuffle(pool)
            shuffled[t] = {a: pool[:len(g[a])], b: pool[len(g[a]):]}
        extreme += diff(shuffled) >= observed - 1e-12
    n_a = sum(len(g[a]) for g in strata.values())
    n_b = sum(len(g[b]) for g in strata.values())
    return observed, (extreme + 1) / (PERMUTATIONS + 1), n_a, n_b


def table(runs, tasks, conditions, metric, fmt):
    print("| task | " + " | ".join(conditions) + " |")
    print("|---|" + "---|" * len(conditions))
    for t in tasks:
        cells = []
        for c in conditions:
            vals = [metric(r) for r in runs if r["task"] == t and r["condition"] == c]
            cells.append(f"{fmt(statistics.mean(vals))} (n={len(vals)})" if vals else "—")
        print(f"| {t} | " + " | ".join(cells) + " |")


def main():
    held = [r for r in load([HELDOUT_DIR]) if r["task"] in HELDOUT]
    dev = [r for r in load(DEV_DIRS) if r["task"] in DEV]
    held_tasks = [t for t in HELDOUT if any(r["task"] == t for r in held)]
    conds = ["baseline", "skill", "skill_v2", "placebo_long"]

    print("# seam-audit v2 vs v1 — analysis\n")
    print(f"Pre-registration: PREREGISTRATION.md. Held-out runs: {len(held)}; dev runs: {len(dev)}.\n")

    print("## Held-out: share of hidden tests passed (mean per run)\n")
    table(held, held_tasks, conds, share, lambda v: f"{v:.0%}")

    print("\n## Held-out tests (stratified permutation, one-sided)\n")
    print("| comparison | mean difference | p | n |")
    print("|---|---|---|---|")
    for a, b, label in (("skill_v2", "skill", "primary"), ("skill_v2", "placebo_long", "primary"),
                        ("skill_v2", "baseline", "secondary"), ("skill", "baseline", "secondary")):
        d, p, na, nb = permutation_p(held, a, b, share, held_tasks)
        print(f"| {a} > {b} ({label}) | {d:+.1%} | {p:.3f} | {na} vs {nb} |")

    print("\n## Dev control: pre-registered subtle traps passed per run\n")
    table(dev, DEV, ["baseline", "skill", "placebo", "skill_v2"], subtle, lambda v: f"{v:.2f}")
    d, p, na, nb = permutation_p(dev, "skill_v2", "skill", subtle, DEV)
    print(f"\nskill_v2 > skill on dev subtle traps: {d:+.2f} per run, p={p:.3f} ({na} vs {nb})\n")
    print("## Dev control: share of hidden tests passed\n")
    table(dev, DEV, ["baseline", "skill", "placebo", "skill_v2"], share, lambda v: f"{v:.0%}")

    print("\n## Cost and turns (mean per run, all runs of this analysis)\n")
    print("| condition | cost, $ | turns |")
    print("|---|---|---|")
    for c in conds + ["placebo"]:
        rs = [r for r in held + dev if r["condition"] == c]
        if rs:
            print(f"| {c} | {statistics.mean([r['cost_usd'] or 0 for r in rs]):.3f}"
                  f" | {statistics.mean([r['num_turns'] or 0 for r in rs]):.1f} |")

    print("\n## Held-out per-test passes\n")
    for t in held_tasks:
        names = sorted({k.split("::")[-1] for r in held if r["task"] == t for k in r["hidden"]})
        print(f"**{t}**\n")
        print("| test | " + " | ".join(conds) + " |")
        print("|---|" + "---|" * len(conds))
        for n in names:
            cells = []
            for c in conds:
                rs = [r for r in held if r["task"] == t and r["condition"] == c]
                ok = sum(1 for r in rs if any(k.endswith("::" + n) and v for k, v in r["hidden"].items()))
                cells.append(f"{ok}/{len(rs)}")
            print(f"| `{n}` | " + " | ".join(cells) + " |")
        print()


if __name__ == "__main__":
    main()
