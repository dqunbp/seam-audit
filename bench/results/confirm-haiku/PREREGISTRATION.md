# Confirmatory run — pre-registration

Written and committed before any run of this batch. The exploratory grid
(`../pretix-probe-haiku`) suggested that the skill catches the subtle traps more
often than baseline and placebo, but loses on basic behaviour; the trap set there
was chosen after seeing baseline fail, which favours the other conditions. This
batch tests that observation on fresh runs with the trap set fixed in advance.

## Setup

- Suite `pretix`, model `haiku` (default effort), tasks `send_download_reminders`
  and `send_expiry_warnings`.
- Conditions `baseline`, `skill`, `placebo`; 10 new runs each per task (60 runs).
  No run from the exploratory grid is reused.

## Subtle traps (fixed)

`send_expiry_warnings`: `test_prevent_reminder_mail`, `test_sent_no_expiry`,
`test_sent_not_immediately_after_purchase`.

`send_download_reminders`: `test_downloads_all_allowed_by_plugin`,
`test_downloads_disabled_by_plugin`, `test_downloads_disabled_per_product`,
`test_downloads_partially_disabled_by_plugin`, `test_not_sent_after_reminder_date`,
`test_not_sent_too_soon_after_purchase`, `test_send_to_attendees_subevent_future`.

All other hidden tests of the two tasks are the **basic** set.

## Metrics and tests

- **Primary:** subtle traps passed per run (0–3 or 0–7), pooled over both tasks;
  compared `skill` vs `placebo` and `skill` vs `baseline` with a one-sided
  permutation test on the per-run counts (stratified by task), α = 0.05.
- **Secondary:** basic tests passed per run, same comparison, two-sided.
- **Overall:** share of all hidden tests passed, reported for completeness.

## Reading the result

- Subtle: skill > placebo significant → the skill's content (not just "an extra
  instruction") helps find hidden contracts.
- Subtle not significant → the exploratory signal was noise/selection.
- Basic: skill < baseline significant → the skill costs basic correctness.
