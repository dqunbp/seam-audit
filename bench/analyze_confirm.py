#!/usr/bin/env python3
"""Analysis of the pre-registered confirmatory run (see results/confirm-haiku/PREREGISTRATION.md).

    python3 bench/analyze_confirm.py bench/results/confirm-haiku > bench/results/confirm-haiku/ANALYSIS.md
"""
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

SUBTLE = {
    "send_expiry_warnings": {
        "test_prevent_reminder_mail", "test_sent_no_expiry", "test_sent_not_immediately_after_purchase",
    },
    "send_download_reminders": {
        "test_downloads_all_allowed_by_plugin", "test_downloads_disabled_by_plugin",
        "test_downloads_disabled_per_product", "test_downloads_partially_disabled_by_plugin",
        "test_not_sent_after_reminder_date", "test_not_sent_too_soon_after_purchase",
        "test_send_to_attendees_subevent_future",
    },
}
CONDITIONS = ("baseline", "skill", "placebo")
PERMUTATIONS = 20_000


def counts(run: dict) -> tuple[int, int, int, int]:
    """(subtle passed, subtle total, basic passed, basic total) for one run."""
    subtle = SUBTLE[run["task"]]
    hidden = {key.split("::")[-1]: ok for key, ok in run["hidden"].items()}
    basic_total = run["hidden_total"] - len(subtle)
    subtle_passed = sum(1 for name in subtle if hidden.get(name))
    basic_passed = sum(1 for name, ok in hidden.items() if ok and name not in subtle)
    return subtle_passed, len(subtle), basic_passed, basic_total


def stratified_permutation_p(data, a: str, b: str, metric: int, alternative: str) -> tuple[float, float]:
    """Difference of means (a - b) of a per-run metric, permuting condition labels within each task."""
    strata = defaultdict(lambda: {a: [], b: []})
    for run in data:
        if run["condition"] in (a, b):
            strata[run["task"]][run["condition"]].append(counts(run)[metric])

    def diff(groups):
        xs = [v for g in groups.values() for v in g[a]]
        ys = [v for g in groups.values() for v in g[b]]
        return statistics.mean(xs) - statistics.mean(ys)

    observed = diff(strata)
    rng = random.Random(0)
    extreme = 0
    for _ in range(PERMUTATIONS):
        shuffled = {}
        for task, groups in strata.items():
            pool = groups[a] + groups[b]
            rng.shuffle(pool)
            shuffled[task] = {a: pool[:len(groups[a])], b: pool[len(groups[a]):]}
        d = diff(shuffled)
        if alternative == "greater":
            extreme += d >= observed - 1e-12
        else:
            extreme += abs(d) >= abs(observed) - 1e-12
    return observed, (extreme + 1) / (PERMUTATIONS + 1)


def main():
    root = Path(sys.argv[1])
    runs = [json.loads(p.read_text()) for p in sorted(root.rglob("result.json"))]
    runs = [r for r in runs if r["task"] in SUBTLE]
    print(f"# Confirmatory run — analysis\n\n{len(runs)} runs (pre-registration: PREREGISTRATION.md).\n")

    print("| task | condition | n | subtle passed | basic passed | all hidden |")
    print("|---|---|---|---|---|---|")
    for task in SUBTLE:
        for cond in CONDITIONS:
            rs = [r for r in runs if r["task"] == task and r["condition"] == cond]
            if not rs:
                continue
            c = [counts(r) for r in rs]
            sp, st, bp, bt = (sum(x[i] for x in c) for i in range(4))
            hp = sum(r["hidden_passed"] for r in rs)
            ht = sum(r["hidden_total"] for r in rs)
            print(f"| {task} | {cond} | {len(rs)} | {sp}/{st} ({sp / st:.0%}) | {bp}/{bt} ({bp / bt:.0%})"
                  f" | {hp}/{ht} ({hp / ht:.0%}) |")

    print("\n## Tests (stratified permutation, per-run counts)\n")
    print("| comparison | metric | mean difference per run | p | alternative |")
    print("|---|---|---|---|---|")
    for a, b in (("skill", "placebo"), ("skill", "baseline"), ("placebo", "baseline")):
        d, p = stratified_permutation_p(runs, a, b, 0, "greater")
        print(f"| {a} − {b} | subtle passed | {d:+.2f} | {p:.3f} | greater |")
    for a, b in (("skill", "baseline"), ("skill", "placebo")):
        d, p = stratified_permutation_p(runs, a, b, 2, "two-sided")
        print(f"| {a} − {b} | basic passed | {d:+.2f} | {p:.3f} | two-sided |")

    print("\n## Per-trap passes\n")
    print("| task | trap | " + " | ".join(CONDITIONS) + " |")
    print("|---|---|" + "---|" * len(CONDITIONS))
    for task, traps in SUBTLE.items():
        names = sorted({k.split("::")[-1] for r in runs if r["task"] == task for k in r["hidden"]})
        for name in names:
            cells = []
            for cond in CONDITIONS:
                rs = [r for r in runs if r["task"] == task and r["condition"] == cond]
                ok = sum(1 for r in rs if any(k.endswith("::" + name) and v for k, v in r["hidden"].items()))
                cells.append(f"{ok}/{len(rs)}")
            mark = " (subtle)" if name in traps else ""
            print(f"| {task} | `{name}`{mark} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
