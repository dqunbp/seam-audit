---
name: seam-audit
description: Use BEFORE writing code for any non-trivial feature, refactor, or change spanning more than one module — especially anything touching money/billing/quotas, background job lifecycle, shared builders/helpers, external SDKs/APIs, schema migrations, or user-facing strings. Triggers include "new feature", "design a feature", "implement feature", "before writing code", "large PR", "seam audit", "check the seams". Run it FIRST, before the first line of implementation.
---

# Seam Audit — review the design before writing the code

## Why this exists

Observation from analyzing large PRs: the bugs that surface in review almost never live in the new "core" of a feature. They sit at the **seams** — where new code meets (a) existing subsystems and their invariants, and (b) external dependencies and their contracts. Real examples: credits deducted bypassing the canonical path; "the provider didn't raise" treated as success; a video URL sent through a photo-only API; an SDK returning a valid variant shape that the code judged as an empty response; a test fixture drifting from prod service wiring; `create()` inserting columns from a not-yet-applied migration; a hardcoded user-facing string instead of the i18n layer.

Review catches these because the real code is in front of the reviewer; at design time contracts are imagined, and the generative mode fills in *how the neighbor probably looks*, walking the happy path. This skill puts the source of truth in front of you BEFORE the first line — read the real neighbor instead of imagining it.

## When to apply

Run it BEFORE the first line of implementation when the task:
- spans more than one module or subsystem, **or**
- touches money/billing, quota counters, or background job lifecycle, **or**
- adds/changes a shared builder, interface, model, fixture, or migration, **or**
- integrates a new external dependency or a new path alongside an existing one, **or**
- adds/changes user-facing strings in a project with an i18n layer.

A small local edit inside a single module does not need it.

## Stance (hold it throughout, not just during the audit)

1. **Don't rely on what you haven't seen.** Before you call a function, parse a response, or repeat logic you didn't write in this session — **open and read the source.** Don't infer the shape from the name. Look at the real neighbor, not the one in your head.
2. **Review your own design before coding.** Ask: *what objection would I raise against this design in review?* Find the seams yourself — while the code isn't written yet, it's free.
3. **Every assumption — stated and evidenced.** For everything the feature relies on: *what I rely on → the assumption I'm making → what backs it.* An assumption with no evidence is your future bug report. Close it now.
4. **Ask about the boundary, not the center.** For each contract think not "what do I think it returns on good input," but "what does it return on empty/error/unusual input — and am I duplicating a path that already exists nearby."

## Procedure

### Step 1. Enumerate the seams

List everything the new code will talk to. A seam is any point where you rely on someone else's contract. Typical places seams hide (this is where to look, not what exactly to check):

- **Money / billing / quotas** — does a canonical path already exist (a charge/deduct function, a grant helper, a webhook flow), and are you going through it rather than around it.
- **External dependency** — the real shape of the response from the SDK / API / external service (including the empty, rejected, variant, and error responses).
- **An existing path nearby** — if a mock/retry/admin/batch variant of the same action exists, your new path should reuse the canonical one, not copy it.
- **Shared builder / helper** — every place it is rebuilt or re-invoked, not just the bit you're adding.
- **Interface / model / type** — do all implementations implement the full interface; aren't you passing an untyped bag of fields where a typed model is expected.
- **Fixtures / fakes** — are they in sync with prod wiring; does the fake record the field you added.
- **Temporal seams — time, ordering, repeats** — what happens when an event arrives twice (duplicate webhook, retry), out of order (callback before the commit), concurrently (two workers grab the same job), or never (timeout with no answer). Idempotency is a contract like a signature: read whether the existing path guarantees it, don't assume it.
- **Schema migrations** — are all columns/fields the code touches actually applied together with that code, in the right order.
- **User-facing strings** — through the project's i18n layer if it has one, all locales, no hardcoded literals in code.

The project's agent instructions file (CLAUDE.md, AGENTS.md, CONVENTIONS.md, …) often names the canonical paths and invariants — treat those as the project-specific seam map. Don't stop at this list — it covers the typical spots, not all of them. Find the seams specific to your feature.

### Step 2. For each seam — assumption → evidence

Don't imagine the contract — **go read it** (open the real file, or the dependency's official docs). Fill the table:

| Seam | Assumption | Evidence (what you read) | Enforcement | Risk if the assumption is wrong |
|---|---|---|---|---|
| `charge_credits(user, amount)` | deducts exactly once, idempotent | read the function + its call sites | by-construction (unique constraint) | double charge / free usage |
| external API response | payload in `response.items[0].data` | read the docs + one real response | runtime guard (validate + raise) | result lost on the success path |

**Enforcement** is one of three levels: **by-construction** (a type, validator, or DB constraint makes violation impossible), **runtime guard** (checked, fails loudly), **convention** (holds only by discipline). Convention is a red flag: if an assumption can be lifted to by-construction cheaply (a schema that rejects unknown fields, a NOT NULL / unique constraint, an enum instead of a string), make that part of the design — don't document what you can enforce.

If there's no evidence, that's the future bug. Either get the evidence, or mark it a risk and design a guard for it.

### Step 3. Write out the unhappy path — and the recovery

For each external/existing contract, explicitly list: empty response, error, unusual shape, duplicate/late/concurrent delivery, failure of a secondary write (dedup/audit inside an error handler — don't swallow it silently). These are the future crashes and lost work.

Listing the failure is half the job. For each one, write what the system **does** and who sees it, one line each:

```
failure → reaction (retry / fail the job / degrade / alert) → observability (log, metric, admin channel)
```

Recovery is designed together with the feature, not bolted on after the incident. Bake both into the design before coding.

## Output

Before implementing, show: (1) the seam table with evidence, (2) the unhappy-path list, (3) an explicit answer to where the new code runs parallel to existing code and why you aren't reusing the canonical path. Only then write code.

## After the code — a quick self-check

Before declaring the feature done, reread your own diff with a reviewer's eye against this same table: is every assumption from Step 2 honored in the code? Is every unhappy path handled? This is the final cross-check, not a replacement for the audit at the start.
