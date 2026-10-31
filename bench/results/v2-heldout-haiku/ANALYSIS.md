# seam-audit v2 vs v1 — analysis

Pre-registration: PREREGISTRATION.md. Held-out runs: 64; dev runs: 80.

## Held-out: share of hidden tests passed (mean per run)

| task | baseline | skill | skill_v2 | placebo_long |
|---|---|---|---|---|
| validate_memberships_in_order | 17% (n=8) | 20% (n=8) | 38% (n=8) | 15% (n=8) |
| run_scheduled_exports | 85% (n=8) | 85% (n=8) | 65% (n=8) | 85% (n=8) |

## Held-out tests (stratified permutation, one-sided)

| comparison | mean difference | p | n |
|---|---|---|---|
| skill_v2 > skill (primary) | -0.8% | 0.537 | 16 vs 16 |
| skill_v2 > placebo_long (primary) | +1.8% | 0.435 | 16 vs 16 |
| skill_v2 > baseline (secondary) | +0.8% | 0.474 | 16 vs 16 |
| skill > baseline (secondary) | +1.6% | 0.411 | 16 vs 16 |

## Dev control: pre-registered subtle traps passed per run

| task | baseline | skill | placebo | skill_v2 |
|---|---|---|---|---|
| send_download_reminders | 0.20 (n=10) | 1.20 (n=10) | 0.60 (n=10) | 0.80 (n=10) |
| send_expiry_warnings | 0.00 (n=10) | 0.00 (n=10) | 0.00 (n=10) | 0.80 (n=10) |

skill_v2 > skill on dev subtle traps: +0.20 per run, p=0.381 (20 vs 20)

## Dev control: share of hidden tests passed

| task | baseline | skill | placebo | skill_v2 |
|---|---|---|---|---|
| send_download_reminders | 55% (n=10) | 63% (n=10) | 56% (n=10) | 60% (n=10) |
| send_expiry_warnings | 67% (n=10) | 67% (n=10) | 67% (n=10) | 51% (n=10) |

## Cost and turns (mean per run, all runs of this analysis)

| condition | cost, $ | turns |
|---|---|---|
| baseline | 0.036 | 29.6 |
| skill | 0.041 | 34.9 |
| skill_v2 | 0.040 | 35.9 |
| placebo_long | 0.043 | 31.9 |
| placebo | 0.027 | 29.9 |

## Held-out per-test passes

**validate_memberships_in_order**

| test | baseline | skill | skill_v2 | placebo_long |
|---|---|---|---|---|
| `test_validate_membership_canceled` | 1/8 | 1/8 | 3/8 | 1/8 |
| `test_validate_membership_ensure_locking` | 3/8 | 2/8 | 1/8 | 2/8 |
| `test_validate_membership_max_usages` | 0/8 | 1/8 | 3/8 | 1/8 |
| `test_validate_membership_not_required` | 3/8 | 2/8 | 4/8 | 1/8 |
| `test_validate_membership_parallel` | 0/8 | 1/8 | 3/8 | 1/8 |
| `test_validate_membership_parallel_validity_dynamic` | 0/8 | 0/8 | 0/8 | 0/8 |
| `test_validate_membership_parallel_validity_fixed` | 1/8 | 1/8 | 3/8 | 1/8 |
| `test_validate_membership_required` | 4/8 | 7/8 | 7/8 | 3/8 |
| `test_validate_membership_test_mode` | 1/8 | 1/8 | 3/8 | 1/8 |
| `test_validate_membership_wrong_customer` | 1/8 | 1/8 | 3/8 | 1/8 |
| `test_validate_membership_wrong_date` | 1/8 | 1/8 | 3/8 | 1/8 |
| `test_validate_membership_wrong_type` | 1/8 | 1/8 | 3/8 | 1/8 |

**run_scheduled_exports**

| test | baseline | skill | skill_v2 | placebo_long |
|---|---|---|---|---|
| `test_event_fail_invalid_config` | 8/8 | 8/8 | 4/8 | 8/8 |
| `test_event_fail_user_inactive` | 8/8 | 8/8 | 4/8 | 8/8 |
| `test_event_fail_user_no_permission` | 8/8 | 8/8 | 4/8 | 8/8 |
| `test_event_not_run_when_failed_5_times` | 0/8 | 0/8 | 2/8 | 0/8 |
| `test_event_ok` | 8/8 | 8/8 | 8/8 | 8/8 |
| `test_event_run_sets_new_time` | 8/8 | 8/8 | 8/8 | 8/8 |
| `test_organizer_fail_invalid_config` | 8/8 | 8/8 | 4/8 | 8/8 |
| `test_organizer_fail_user_does_not_have_specific_permission` | 8/8 | 8/8 | 4/8 | 8/8 |
| `test_organizer_fail_user_inactive` | 8/8 | 8/8 | 4/8 | 8/8 |
| `test_organizer_limited_to_events` | 8/8 | 8/8 | 8/8 | 8/8 |
| `test_organizer_not_run_when_failed_5_times` | 0/8 | 0/8 | 2/8 | 0/8 |
| `test_organizer_ok` | 8/8 | 8/8 | 8/8 | 8/8 |
| `test_organizer_run_sets_new_time` | 8/8 | 8/8 | 8/8 | 8/8 |

