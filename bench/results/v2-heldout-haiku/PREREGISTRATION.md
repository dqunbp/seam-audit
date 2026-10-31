# seam-audit v2 vs v1 — pre-registration

Written and committed before any run of this batch. `bench/conditions/seam-audit-v2/SKILL.md`
is frozen at the commit that adds this file; it is not edited after any held-out run.

## Question

Does v2 (inbound seams + "take edge-case policy from the closest sibling", derived from v1
transcripts on the dev tasks) improve results **on tasks it was not designed from**, beyond
what a generic instruction of the same length does?

## Tasks

- **Held-out (primary):** `validate_memberships_in_order`, `run_scheduled_exports`,
  `assign_automatically` (suite `pretix`, `"split": "heldout"`). Chosen by test count and
  callers before the v1 failure analysis; no agent had run on them before this batch.
- **Dev (control):** `send_download_reminders`, `send_expiry_warnings` — the tasks v2 was
  designed from.

## Conditions

`baseline`, `skill` (v1), `skill_v2`, `placebo_long` (generic advice, 1572 words vs v2's 1603).
v1 and v2 are installed under the same name with the same prompt line.

## Stages

- **Stage A (screening):** 2 `baseline` runs per held-out task. A task goes to stage B only if
  baseline fails at least one hidden test in at least one of the two runs (a task at ceiling
  cannot show a difference). Stage A runs are not used in the analysis.
- **Stage B:** held-out tasks kept by stage A × 4 conditions × 8 new runs. Dev: `skill_v2` ×
  10 runs per dev task, compared with the `baseline` / `skill` / `placebo` runs of
  `../confirm-haiku` (same model, suite, prompts and harness).

## Metrics and tests

- **Primary:** share of hidden tests passed per run, held-out tasks pooled; stratified (by
  task) one-sided permutation test, α = 0.05, for `skill_v2 > skill` and
  `skill_v2 > placebo_long`.
- **Secondary:** `skill_v2 > baseline`, `skill > baseline` (held-out); on dev,
  `skill_v2 > skill` on the pre-registered subtle traps of `../confirm-haiku`.
- Cost and turns per run, reported.

## Reading the result

- Both primary comparisons significant → v2 generalizes beyond its dev tasks.
- Dev improves but held-out does not → v2 overfits the dev tasks.
- Neither improves → the diagnosis did not translate into a better skill.
