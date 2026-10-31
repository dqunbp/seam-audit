# Confirmatory run — analysis

60 runs (pre-registration: PREREGISTRATION.md).

| task | condition | n | subtle passed | basic passed | all hidden |
|---|---|---|---|---|---|
| send_expiry_warnings | baseline | 10 | 0/30 (0%) | 60/60 (100%) | 60/90 (67%) |
| send_expiry_warnings | skill | 10 | 0/30 (0%) | 60/60 (100%) | 60/90 (67%) |
| send_expiry_warnings | placebo | 10 | 0/30 (0%) | 60/60 (100%) | 60/90 (67%) |
| send_download_reminders | baseline | 10 | 2/70 (3%) | 86/90 (96%) | 88/160 (55%) |
| send_download_reminders | skill | 10 | 12/70 (17%) | 89/90 (99%) | 101/160 (63%) |
| send_download_reminders | placebo | 10 | 6/70 (9%) | 83/90 (92%) | 89/160 (56%) |

## Tests (stratified permutation, per-run counts)

| comparison | metric | mean difference per run | p | alternative |
|---|---|---|---|---|
| skill − placebo | subtle passed | +0.30 | 0.238 | greater |
| skill − baseline | subtle passed | +0.50 | 0.062 | greater |
| placebo − baseline | subtle passed | +0.20 | 0.288 | greater |
| skill − baseline | basic passed | +0.15 | 0.455 | two-sided |
| skill − placebo | basic passed | +0.30 | 0.021 | two-sided |

## Per-trap passes

| task | trap | baseline | skill | placebo |
|---|---|---|---|---|
| send_expiry_warnings | `test_disabled` | 10/10 | 10/10 | 10/10 |
| send_expiry_warnings | `test_paid` | 10/10 | 10/10 | 10/10 |
| send_expiry_warnings | `test_prevent_reminder_mail` (subtle) | 0/10 | 0/10 | 0/10 |
| send_expiry_warnings | `test_prevent_reminder_mail_confirmed_but_not_all_paid` | 10/10 | 10/10 | 10/10 |
| send_expiry_warnings | `test_prevent_reminder_mail_failed_state` | 10/10 | 10/10 | 10/10 |
| send_expiry_warnings | `test_sent_days` | 10/10 | 10/10 | 10/10 |
| send_expiry_warnings | `test_sent_no_expiry` (subtle) | 0/10 | 0/10 | 0/10 |
| send_expiry_warnings | `test_sent_not_immediately_after_purchase` (subtle) | 0/10 | 0/10 | 0/10 |
| send_expiry_warnings | `test_sent_once` | 10/10 | 10/10 | 10/10 |
| send_download_reminders | `test_disabled` | 10/10 | 10/10 | 10/10 |
| send_download_reminders | `test_downloads_all_allowed_by_plugin` (subtle) | 1/10 | 4/10 | 3/10 |
| send_download_reminders | `test_downloads_disabled` | 9/10 | 10/10 | 10/10 |
| send_download_reminders | `test_downloads_disabled_by_plugin` (subtle) | 0/10 | 0/10 | 0/10 |
| send_download_reminders | `test_downloads_disabled_per_product` (subtle) | 0/10 | 0/10 | 0/10 |
| send_download_reminders | `test_downloads_partially_disabled_by_plugin` (subtle) | 1/10 | 4/10 | 3/10 |
| send_download_reminders | `test_not_sent_after_reminder_date` (subtle) | 0/10 | 2/10 | 0/10 |
| send_download_reminders | `test_not_sent_for_disabled_sales_channel` | 9/10 | 10/10 | 9/10 |
| send_download_reminders | `test_not_sent_too_early` | 10/10 | 10/10 | 10/10 |
| send_download_reminders | `test_not_sent_too_soon_after_purchase` (subtle) | 0/10 | 2/10 | 0/10 |
| send_download_reminders | `test_send_not_to_attendees_with_same_address` | 10/10 | 9/10 | 6/10 |
| send_download_reminders | `test_send_to_attendees` | 8/10 | 10/10 | 8/10 |
| send_download_reminders | `test_send_to_attendees_subevent_future` (subtle) | 0/10 | 0/10 | 0/10 |
| send_download_reminders | `test_send_to_attendees_subevent_past` | 10/10 | 10/10 | 10/10 |
| send_download_reminders | `test_sent_once` | 10/10 | 10/10 | 10/10 |
| send_download_reminders | `test_sent_paid_only` | 10/10 | 10/10 | 10/10 |
