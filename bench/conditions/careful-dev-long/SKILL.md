---
name: careful-dev
description: Use BEFORE writing code for any non-trivial feature, refactor, or change spanning more than one module. Triggers include "new feature", "design a feature", "implement feature", "before writing code", "large PR", "careful", "best practices". Run it FIRST, before the first line of implementation.
---

# Careful Development — engineering discipline for feature work

## Why this exists

Most defects that reach review are not exotic. They come from rushing: misreading the requirement, skipping edge cases, writing code that does not match the conventions of the codebase, leaving the tests for later and then writing too few of them. None of these need special techniques to avoid — they need a steady, deliberate working rhythm. This skill describes that rhythm so it is applied every time, not only when there is time to spare.

## When to apply

Apply it before starting any task that:
- adds a new feature or a new public function, **or**
- changes behaviour that other code depends on, **or**
- touches more than one file, **or**
- will be reviewed by someone else.

A one-line fix or a typo does not need the full routine, but the testing step still applies.

## Principles (hold them throughout)

1. **Understand the goal before the code.** Restate the requirement in your own words. If something is ambiguous, pick the most reasonable interpretation and write it down so it can be checked.
2. **Small, safe steps.** Make one change at a time and keep the code working between steps. Large rewrites hide mistakes.
3. **Fit in, don't stand out.** New code should look like it was written by the same team: same naming, same structure, same error style, same level of comments.
4. **Tests are part of the feature.** A feature without tests is not done. Tests describe the behaviour you promised, including what happens when things go wrong.
5. **Leave it cleaner.** Remove dead code you created, keep functions short, and don't leave TODOs without a reason.

## Procedure

### Step 1. Clarify the task

Write a short summary of what you are building:
- the inputs and outputs of the new code,
- what the user of the feature should see on success,
- what they should see when something fails,
- anything the task explicitly says must not change.

List open questions. For each one, write the assumption you will proceed with.

### Step 2. Plan the change

Look through the project to get oriented: the README, the directory layout, and the parts of the code most related to your task. Then sketch the plan:

- which files you will create or change,
- the functions or classes you will add, with their signatures,
- the order in which you will make the changes,
- how you will test each part.

Prefer the simplest design that meets the requirement. Avoid adding configuration, abstraction layers or generality that the task does not ask for. If the project already has a helper for something you need, use it instead of writing a new one.

### Step 3. Implement

Work through the plan step by step:

- Keep functions focused on a single job, and give them descriptive names.
- Validate inputs at the boundary of the feature, and fail with a clear error rather than continuing with bad data.
- Handle errors explicitly. Don't swallow exceptions silently; either handle them meaningfully or let them propagate.
- Keep user-facing messages clear and consistent with the rest of the application.
- Match the formatting and style of the surrounding code.

### Step 4. Test

Write tests alongside the code, not after:

| Kind of test | What it covers |
|---|---|
| happy path | the main scenario works end to end |
| edge cases | empty input, boundary values, unusual but valid input |
| error cases | invalid input, failures of things the feature calls |
| regression | behaviour that existed before still works |

Run the full test suite, not only the new tests. If something fails, fix the cause rather than adjusting the test to pass.

### Step 5. Review your own work

Before declaring the task done, read your diff from top to bottom as if you were the reviewer:

- Does the code do what the summary from Step 1 says?
- Is anything left over from experiments — debug prints, unused imports, commented-out code?
- Are names and messages clear to someone who has not seen the task?
- Would a new team member understand the change without asking you?

## Common pitfalls

These come up again and again in feature work. Keep them in mind while you implement:

- **Scope creep.** Fixing unrelated things in the same change makes the diff harder to review and riskier to ship. Note them and leave them for a separate change.
- **Copy-paste drift.** When you copy a block to start from, re-read every line of the copy. Leftover names, wrong constants and stale comments are easy to miss.
- **Magic values.** Numbers and strings that carry meaning deserve a named constant or a configuration entry, so the next person can find and change them.
- **Overly clever code.** A slightly longer but obvious solution beats a short one that needs a comment to explain. Optimise for the reader.
- **Inconsistent errors.** Use the same error types, codes and message style as the rest of the application, so callers can handle them uniformly.
- **Fragile tests.** Tests that depend on execution order, real time, or exact log output break for reasons unrelated to the code under test. Keep each test independent and deterministic.
- **Untested failure handling.** Error branches are the code that runs least often and breaks most painfully. If you wrote an `except` or an `if error`, a test should exercise it.
- **Silent behaviour changes.** If an existing function now behaves differently, say so explicitly in your summary, and check whether its existing tests still describe the intended behaviour.
- **Forgetting the documentation.** If the change affects how the feature is used or configured, update the README or the relevant docstrings in the same change.

## Working in an unfamiliar codebase

Most feature work happens in code you did not write. A few habits make that safer:

- **Learn how the project is built and tested first.** Find the commands for running the tests, the linter and the formatter, and run the tests once before changing anything, so you know which failures were already there.
- **Respect the existing structure.** Put new code where similar code already lives. If the project separates models, services and views, keep that separation; don't introduce a new layer for one feature.
- **Keep formatting changes out of feature changes.** Reformatting a file you only needed to touch in one place hides the real change in the diff.
- **Keep public interfaces stable.** If you must change a function signature that others call, update every call site in the same change and mention it in your summary.
- **Don't fight the framework.** Use the framework's own mechanisms for configuration, logging, translations and background work instead of building your own.

## Writing good tests

Good tests are short, focused and easy to read when they fail:

- **One behaviour per test.** A test that checks five things tells you less when it fails than five tests that each check one.
- **Arrange, act, assert.** Set up the data, perform the action, check the result — in that order, with a blank line between the parts.
- **Name tests after the behaviour.** `test_rejects_expired_coupon` says more than `test_coupon_3`.
- **Prefer real objects over mocks.** Mock only what is slow, external or non-deterministic. A test that mocks everything mostly tests the mocks.
- **Use the project's fixtures and factories.** They already encode how valid data looks; creating objects by hand drifts from them over time.
- **Make failures readable.** Assert on the specific value you care about, so the failure message points at the problem.

## Performance and data

Correct code can still be slow or wasteful. Keep an eye on the basics:

- **Avoid queries in loops.** Fetch related data in one query (joins, prefetching, bulk lookups) instead of once per item.
- **Write in bulk when you can.** Creating or updating many rows one at a time is slow; use the bulk operations your data layer offers.
- **Group related writes.** If several writes must succeed or fail together, run them in one transaction.
- **Don't load what you don't need.** Select only the fields you use when working with large tables.
- **Measure before optimising.** Only make code more complex for speed when you have seen that it is actually slow.

## Before you finish

Run through this list before declaring the task done:

1. The full relevant test suite passes, including tests you did not write.
2. The linter and formatter report nothing new.
3. Every new function has a clear name, and its docstring or comment explains anything that is not obvious.
4. No debug output, temporary files or commented-out code remains.
5. The summary of your change says what changed, why, and anything a reviewer should look at closely.

## Output

Before implementing, show: (1) the task summary with assumptions, (2) the plan of files and functions, (3) the list of tests you will write. Then implement, test, and finish with a short summary of what changed.
