# Seam-audit benchmark — basic-haiku-stopped

21 runs. Score = share of hidden trap tests passed (mean ± sd over repetitions).

## haiku

| task | baseline | skill | placebo |
|---|---|---|---|
| upscale | 100% ± 0% (n=3) | 100% ± 0% (n=2) | 100% ± 0% (n=3) |
| video_webhook | 100% ± 0% (n=3) | 100% ± 0% (n=2) | 100% ± 0% (n=2) |
| free_quota | 100% ± 0% (n=2) | 100% ± 0% (n=2) | 100% ± 0% (n=2) |
| **all** | **100%** | **100%** | **100%** |

| metric (mean per run) | baseline | skill | placebo |
|---|---|---|---|
| visible suite green | 100% | 100% | 100% |
| cost, $ | 0.02 | 0.02 | 0.02 |
| turns | 31.2 | 22.7 | 18.7 |
| files read | 14.0 | 3.7 | 0.3 |
| diff lines | 206.6 | 225.2 | 197.4 |
| skill invoked | 0% | 100% | 100% |
| seam table in output | 0% | 83% | 0% |

### Per-trap pass rate

**upscale**

| trap | baseline | skill | placebo |
|---|---|---|---|
| `happy_path_charges_4_and_saves_2x_image` | 3/3 | 2/2 | 3/3 |
| `job_records_source_image_id` | 3/3 | 2/2 | 3/3 |
| `migration_applies_to_already_migrated_database` | 3/3 | 2/2 | 3/3 |
| `pro_user_pays_discounted_price` | 3/3 | 2/2 | 3/3 |
| `retry_with_same_request_id_charges_once` | 3/3 | 2/2 | 3/3 |
| `retry_does_not_upscale_again` | 3/3 | 2/2 | 3/3 |
| `rejected_input_is_not_reported_as_success` | 3/3 | 2/2 | 3/3 |
| `rejected_input_costs_nothing` | 3/3 | 2/2 | 3/3 |
| `filtered_result_is_refunded` | 3/3 | 2/2 | 3/3 |
| `provider_error_is_refunded` | 3/3 | 2/2 | 3/3 |
| `rate_limit_is_refunded` | 3/3 | 2/2 | 3/3 |
| `cannot_upscale_another_users_image` | 3/3 | 2/2 | 3/3 |
| `missing_image_is_refused_without_charge` | 3/3 | 2/2 | 3/3 |
| `insufficient_credits_does_not_call_provider` | 3/3 | 2/2 | 3/3 |
| `error_messages_are_localized` | 3/3 | 2/2 | 3/3 |
| `locale_files_in_sync` | 3/3 | 2/2 | 3/3 |
| `no_direct_balance_writes` | 3/3 | 2/2 | 3/3 |

**video_webhook**

| trap | baseline | skill | placebo |
|---|---|---|---|
| `completed_marks_job_succeeded_with_url` | 3/3 | 2/2 | 2/2 |
| `failed_marks_job_failed_and_refunds` | 3/3 | 2/2 | 2/2 |
| `progress_is_acknowledged_and_keeps_processing` | 3/3 | 2/2 | 2/2 |
| `wrong_signature_is_rejected` | 3/3 | 2/2 | 2/2 |
| `missing_signature_is_rejected` | 3/3 | 2/2 | 2/2 |
| `stale_signature_is_rejected` | 3/3 | 2/2 | 2/2 |
| `duplicate_failed_event_refunds_once` | 3/3 | 2/2 | 2/2 |
| `duplicate_completed_event_is_harmless` | 3/3 | 2/2 | 2/2 |
| `progress_after_completed_keeps_succeeded` | 3/3 | 2/2 | 2/2 |
| `failed_after_completed_does_not_refund` | 3/3 | 2/2 | 2/2 |
| `failed_after_sweeper_timeout_does_not_refund_twice` | 3/3 | 2/2 | 2/2 |
| `unknown_job_does_not_crash` | 3/3 | 2/2 | 2/2 |
| `moderated_completion_is_not_success` | 3/3 | 2/2 | 2/2 |
| `moderated_completion_is_refunded` | 3/3 | 2/2 | 2/2 |
| `no_direct_balance_writes` | 3/3 | 2/2 | 2/2 |

**free_quota**

| trap | baseline | skill | placebo |
|---|---|---|---|
| `sixth_image_of_the_day_is_refused` | 2/2 | 2/2 | 2/2 |
| `refused_request_is_not_charged_and_not_sent_to_provider` | 2/2 | 2/2 | 2/2 |
| `limit_message_is_localized_and_names_the_limit` | 2/2 | 2/2 | 2/2 |
| `pro_users_are_unlimited` | 2/2 | 2/2 | 2/2 |
| `limit_is_per_user` | 2/2 | 2/2 | 2/2 |
| `failed_generations_do_not_count` | 2/2 | 2/2 | 2/2 |
| `insufficient_credits_attempt_does_not_count` | 2/2 | 2/2 | 2/2 |
| `retried_request_id_counts_once` | 2/2 | 2/2 | 2/2 |
| `videos_do_not_use_up_the_image_limit` | 2/2 | 2/2 | 2/2 |
| `limit_resets_at_utc_midnight` | 2/2 | 2/2 | 2/2 |
| `locale_files_in_sync` | 2/2 | 2/2 | 2/2 |
| `no_direct_balance_writes` | 2/2 | 2/2 | 2/2 |

