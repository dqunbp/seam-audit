---
name: seam-audit
description: Use BEFORE writing the code for any non-trivial feature, refactor, or change that touches more than one module — especially features over ~800 lines or anything touching money/billing/credits, background job lifecycle, shared builders/helpers, external dependencies (SDKs, APIs, LLM clients), migrations, or user-facing strings. The skill front-loads the contract/seam checking that normally only happens during code review, so the bugs that usually surface in review (broken contracts at the seams between new code and existing systems or external dependencies) are caught at design time instead. Triggers include "new feature", "design a feature", "implement feature", "before writing code", "large PR", "seam audit", "check the seams", "feature-dev". Run it FIRST, before the first line of implementation. Output is a seam-audit table (seam → assumption → evidence) plus the unhappy-path list, then implementation proceeds.
---

# Seam Audit — review the design before writing the code

## Why this exists

Observation from analyzing large PRs: the bugs that surface in review almost never live in the new "core" of a feature. They sit at the **seams** — where new code meets (a) existing subsystems and their invariants, and (b) external dependencies and their contracts. Real examples: credits deducted bypassing the canonical path; "the provider didn't raise" treated as success; a video URL sent through a photo-only API; an SDK returning a valid variant shape that the code judged as an empty response; a test fixture drifting from prod service wiring; `create()` inserting columns from a not-yet-applied migration; a hardcoded user-facing string instead of the i18n layer.

**Why this gets caught in review but not at design time:** in review the real code is in front of you — the neighbor's actual signature, the actual payload, the actual existing path. The reviewer is in "verify against reality" mode. At design time those contracts aren't in front of you — they're imagined, and the generative mode fills in *how the neighbor probably looks*, walking the happy path.

**What this skill does:** it forces you to put the source of truth in front of you BEFORE writing a line — read the real neighbor instead of imagining it. This moves the reviewer's free advantage one step earlier.

This is not a new observation. Margaret Hamilton's error analysis of the Apollo flight software found that ~73% of errors were **interface errors** — modules disagreeing about data, timing, or control at their boundaries — which led to her "Development Before the Fact" paradigm: prevent interface errors at definition time instead of finding them in test. This skill is the informal, evidence-driven version of that idea.

## When to apply

Run it BEFORE the first line of implementation when the task is:
- larger than ~800 lines, **or**
- touching money/billing/credits, quota counters, or background job lifecycle, **or**
- adding/changing a shared builder, protocol, model, fixture, or migration, **or**
- integrating a new external dependency or a new path alongside an existing one.

A small local edit inside a single module does not need it.

## Stance (hold it throughout, not just during the audit)

1. **Don't rely on what you haven't seen.** Before you call a function, parse a response, or repeat logic you didn't write in this session — **open and read the source.** Don't infer the shape from the name. Look at the real neighbor, not the one in your head.
2. **Review your own design before coding.** Ask: *what objection would I raise against this design in review?* Find the seams yourself — while the code isn't written yet, it's free.
3. **Every assumption — stated and evidenced.** For everything the feature relies on: *what I rely on → the assumption I'm making → what backs it.* An assumption with no evidence is your future bug report. Close it now.
4. **Ask about the boundary, not the center.** For each contract think not "what do I think it returns on good input," but "what does it return on empty/error/unusual input — and am I duplicating a path that already exists nearby."

## Procedure

### Step 1. Enumerate the seams

List everything the new code will talk to. A seam is any point where you rely on someone else's contract. Typical places seams hide (this is where to look, not what exactly to check):

- **Money / billing / quotas** — does a canonical path already exist (deduction RPC, grant helper, webhook flow), and are you going through it rather than around it.
- **External dependency** — the real shape of the response from the SDK / API / LLM client (including the empty, blocked, variant, and error responses).
- **An existing path nearby** — if a mock/retry/admin/batch variant of the same action exists, your new path should reuse the canonical one, not copy it.
- **Shared builder / helper** — every place it is rebuilt or re-invoked, not just the bit you're adding.
- **Protocol / model / type** — do all implementations implement the full protocol; aren't you passing a raw dict where a typed model is expected.
- **Fixtures / fakes** — are they in sync with prod wiring; does the fake record the field you added.
- **Temporal seams — time, ordering, repeats** — what happens when an event arrives twice (duplicate webhook, retry), out of order (callback before the commit), concurrently (two workers grab the same job), or never (timeout with no answer). Idempotency is a contract like a signature: read whether the existing path guarantees it, don't assume it.
- **Migrations** — are all columns the code touches in the same migration as that code.
- **User-facing strings** — through the project's i18n layer, all locales, no hardcoded literals in code.

The project's CLAUDE.md often names the canonical paths and invariants ("Key Patterns", "Non-Obvious Mechanics" and similar sections) — treat those as the project-specific seam map. Don't stop at this list — it covers the typical spots, not all of them. Find the seams specific to your feature.

### Step 2. For each seam — assumption → evidence

Don't imagine the contract — **go read it** (Read/Grep on the real file, or the dependency's docs via context7). Fill the table:

| Seam | Assumption | Evidence (what you read) | Enforcement | Risk if the assumption is wrong |
|---|---|---|---|---|
| `complete_with_deduction(...)` | deducts exactly 1 credit, idempotent | read the RPC + the call site | by-construction (RPC guard) | double charge / free generation |
| LLM router response | image bytes in `choices[0].message.content` | read the docs + the router module | runtime guard (validate + raise) | image lost on the success path |

**Enforcement** is one of three levels: **by-construction** (a type, validator, or DB constraint makes violation impossible), **runtime guard** (checked, fails loudly), **convention** (holds only by discipline). Convention is a red flag: if an assumption can be lifted to by-construction cheaply (a typed model with `extra="forbid"`, NOT NULL, an enum instead of a string), make that part of the design — don't document what you can enforce.

If there's no evidence, that's the future bug. Either get the evidence, or mark it a risk and design a guard for it.

### Step 3. Write out the unhappy path — and the recovery

For each external/existing contract, explicitly list: empty response, error, unusual shape, duplicate/late/concurrent delivery, failure of a secondary write (dedup/audit inside an `except` — don't swallow it silently). These are the future crashes and lost work.

Listing the failure is half the job. For each one, write what the system **does** and who sees it, one line each:

```
failure → reaction (retry / fail the job / degrade / alert) → observability (log, metric, admin channel)
```

Recovery is designed together with the feature, not bolted on after the incident. Bake both into the design before coding.

## Output

Before implementing, show: (1) the seam table with evidence, (2) the unhappy-path list, (3) an explicit answer to where the new code runs parallel to existing code and why you aren't reusing the canonical path. Only then write code.

## After the code — a quick self-check

Before declaring the feature done, reread your own diff with a reviewer's eye against this same table: is every assumption from Step 2 honored in the code? Is every unhappy path handled? This is the final cross-check, not a replacement for the audit at the start.
