# seam-audit benchmark

Does the `seam-audit` skill make an agent's implementation better — and is it the skill,
or just *any* extra instruction?

## Design

**Suites.** Each suite under `suites/` has `fixture/`, `tasks/`, `hidden/` and `reference/`.

**Fixture.** `suites/basic/fixture/` is a small but realistic backend ("pixforge": credits, jobs,
quotas, i18n, inbound webhooks, a vendored provider SDK with its API doc). It has the
kind of seams `SKILL.md` talks about: a canonical charge/refund path with idempotency-key
conventions, a job state machine with conditional transitions, a provider SDK that returns
*valid variant shapes* (e.g. `rejected` echoes the input image), at-least-once / unordered
webhooks, an injected clock, a migrations directory that prod has already applied, and an
i18n layer with a locale-parity test.

**Tasks** (`suites/*/tasks/*/prompt.md`) are ordinary feature tickets; they never mention seams:

| task | what the agent builds | traps (hidden tests) |
|---|---|---|
| `upscale` | paid 2x upscale of a library image | pricing rules (pro discount), retries by `request_id`, `rejected` response that looks like success, filtered/error/429 refunds, ownership, schema change via a *new* migration, localized errors, no direct balance writes |
| `video_webhook` | Lumen webhook that completes video jobs | signature + replay window, duplicate delivery, out-of-order events, terminal states stay terminal, refund-once across the sweeper path, moderated "completed" with no video, unknown job |
| `free_quota` | 5 images/day for free users | atomic per-user per-kind quota, failed/insufficient/retried attempts don't count, UTC day via the app clock, localized message, pro unlimited |

**Grading.** After the agent finishes, `hidden/<task>/` tests are copied in and run
(the agent never sees them). Each hidden test is one trap; the score is the share passed.
`validate.py` checks the benchmark itself: the reference solutions in `reference/` pass
100%, and the untouched fixture passes only the 1–2 "don't break things" guards.
The visible suite (`tests/`, including the agent's own tests) is also run.

**Hard suite** (`suites/hard/`): the same codebase and tasks with the explanatory
comments stripped (conventions now live only in code, not docstrings) and subtler seams:
files live in our bucket under storage keys while Lumen output URLs expire after 24h
(stated only in the provider doc); webhook events can arrive before `start_video` records the
provider job id, so they must not be acknowledged; the upscale price is missing from the
price table, so it has to be added rather than hardcoded for pro discounts to apply.

**Conditions** (`harness.py`):

| condition | skill installed in `.claude/skills/` | prompt suffix |
|---|---|---|
| `baseline` | — | — |
| `skill` | `seam-audit` | "Before you start, use the `seam-audit` skill." |
| `placebo` | `careful-dev` (generic best practices, similar length) | "Before you start, use the `careful-dev` skill." |

`skill` vs `baseline` is the raw effect; `skill` vs `placebo` is the effect of *this*
skill's content over a generic instruction. Triggering is out of scope: the skill is
always invoked explicitly.

**Isolation.** Each run is `claude -p` in a fresh git copy of the fixture outside this
repo, with a clean `HOME`, only `Read/Edit/Write/Glob/Grep/Bash/Skill` tools, Bash
limited to read-only commands and pytest, no MCP servers and no account plugins.

**Process metrics** from the stream-json transcript: cost, turns, files read, skill
invocation, whether a seam table appeared, diff size.

## Run

```sh
python3 -m venv /tmp/bench-venv && /tmp/bench-venv/bin/pip install pytest
python3 bench/validate.py --suite basic --venv /tmp/bench-venv --workdir /tmp/seam-validate
python3 bench/run.py --suite basic --models haiku --reps 5 --workers 6 \
    --venv /tmp/bench-venv --workdir /tmp/seam-runs --out bench/results/pilot-haiku
python3 bench/report.py bench/results/pilot-haiku > bench/results/pilot-haiku/REPORT.md
```

`--models sonnet,opus`, `--effort medium`, `--conditions baseline,skill` etc. narrow or
widen a run; re-running skips runs that already have a `result.json`.

## Limits

- One small fixture: an agent can afford to read the whole repo, which helps every
  condition and compresses the differences a skill could make in a large codebase.
- Hidden tests encode one reasonable contract per trap; a defensible alternative design
  can fail a test (the tests accept the common alternatives, e.g. raising vs. returning
  an error for invalid input).
- Few repetitions per cell; treat small differences as noise.
