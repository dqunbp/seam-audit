# Findings (Haiku, October 2026)

All runs: `claude -p` with the Haiku model at default effort, isolated as described in
README.md. Numbers are shares of hidden (maintainer or trap) tests passed. Details and
per-test tables are in each `results/*/REPORT.md` / `ANALYSIS.md`.

## 1. Synthetic fixture — ceiling

`suites/basic` and `suites/hard`: every condition scores ~100% (21 + 6 runs). The fixture is
small enough to read in full, so no instruction can add anything. Abandoned.

## 2. pretix, re-implement a removed function

| task | baseline | skill v1 | placebo | n per cell |
|---|---|---|---|---|
| extend_order | 100% | — | — | 1 |
| reactivate_order | 97% | 99% | 100% | 5 |
| expire_orders | 90% | 92% | 88% | 5 |
| send_expiry_warnings | 67% | 64% | 62% | 5 |
| send_download_reminders | 59% | 62% | 60% | 5 |
| cancel_order | 78% | 76% | 65% | 5 |

No overall effect. Exploratory per-trap reading suggested v1 catches "subtle" traps more often.

## 3. Pre-registered confirmation of the subtle-trap signal (`results/confirm-haiku`)

Fixed trap set, 10 fresh runs per cell. skill vs placebo +0.30 traps/run (p = 0.24),
skill vs baseline +0.50 (p = 0.06). Not confirmed. All of the difference is on
`send_download_reminders`; the expiry-warning traps are 0/30 in every condition.

## 4. v2 from failure analysis, tested on held-out tasks (`results/v2-heldout-haiku`)

v2 adds inbound seams (search the repo for what already expects the code) and "take
edge-case policy from the closest sibling". Placebo lengthened to match.

| | baseline | skill v1 | skill v2 | placebo (long) |
|---|---|---|---|---|
| held-out: validate_memberships_in_order | 17% | 20% | 38% | 15% |
| held-out: run_scheduled_exports | 85% | 85% | 65% | 85% |
| dev: send_expiry_warnings | 67% | 67% | 51% | 67% (short) |
| dev: send_download_reminders | 55% | 63% | 60% | 56% (short) |

Primary comparisons (held-out, pooled): v2 vs v1 −0.8 pp (p = 0.54), v2 vs long placebo
+1.8 pp (p = 0.44). **v2 does not generalize.** It finds more things nobody else finds (the
payment-provider hook, the 2-hour rule, the 5-failures rule) but copies policy from a sibling
that only looks similar (`expire_orders` → `send_expiry_warnings`) and breaks basic behaviour.

Caveat: the membership tests assert on exact error strings that survive in `locale/*.po`
after the function is removed; repo-wide search can recover them. That trap is an artifact of
the removed-feature method, not a real-world seam, and it is where v2's 38% comes from.

## Overall

On Haiku, across 300+ runs, neither version of the skill measurably improves the result over
no skill or over a generic instruction of the same length; both cost ~15–30% more turns.
The skill does change *what* the agent looks at — it finds rarer contracts — but on these
tasks that is offset by new mistakes. Untested: stronger models, other codebases, and tasks
that are new features rather than re-implementations.
