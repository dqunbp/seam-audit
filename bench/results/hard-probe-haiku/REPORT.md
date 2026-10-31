# Seam-audit benchmark — hard-probe-haiku

6 runs. Score = share of hidden trap tests passed (mean ± sd over repetitions).

## haiku

| task | baseline |
|---|---|
| upscale | 100% ± 0% (n=2) |
| video_webhook | 100% ± 0% (n=2) |
| free_quota | 100% ± 0% (n=2) |
| **all** | **100%** |

| metric (mean per run) | baseline |
|---|---|
| visible suite green | 100% |
| cost, $ | 0.02 |
| turns | 22.0 |
| files read | 4.5 |
| diff lines | 205.2 |
| skill invoked | 0% |
| seam table in output | 0% |

### Per-trap pass rate

**upscale**

| trap | baseline |
|---|---|
| `happy_path_charges_4_and_saves_2x_image` | 2/2 |
| `job_records_source_image_id` | 2/2 |
| `output_is_copied_to_our_storage` | 2/2 |
| `migration_applies_to_already_migrated_database` | 2/2 |
| `pro_user_pays_discounted_price` | 2/2 |
| `retry_with_same_request_id_charges_once` | 2/2 |
| `retry_does_not_upscale_again` | 2/2 |
| `rejected_input_is_not_reported_as_success` | 2/2 |
| `rejected_input_costs_nothing` | 2/2 |
| `filtered_result_is_refunded` | 2/2 |
| `provider_error_is_refunded` | 2/2 |
| `rate_limit_is_refunded` | 2/2 |
| `cannot_upscale_another_users_image` | 2/2 |
| `missing_image_is_refused_without_charge` | 2/2 |
| `insufficient_credits_does_not_call_provider` | 2/2 |
| `error_messages_are_localized` | 2/2 |
| `locale_files_in_sync` | 2/2 |
| `no_direct_balance_writes` | 2/2 |

**video_webhook**

| trap | baseline |
|---|---|
| `completed_marks_job_succeeded` | 2/2 |
| `video_is_copied_to_our_storage` | 2/2 |
| `event_before_job_is_recorded_gets_retried` | 2/2 |
| `failed_marks_job_failed_and_refunds` | 2/2 |
| `progress_is_acknowledged_and_keeps_processing` | 2/2 |
| `wrong_signature_is_rejected` | 2/2 |
| `missing_signature_is_rejected` | 2/2 |
| `stale_signature_is_rejected` | 2/2 |
| `duplicate_failed_event_refunds_once` | 2/2 |
| `duplicate_completed_event_is_harmless` | 2/2 |
| `progress_after_completed_keeps_succeeded` | 2/2 |
| `failed_after_completed_does_not_refund` | 2/2 |
| `failed_after_sweeper_timeout_does_not_refund_twice` | 2/2 |
| `unknown_job_does_not_crash` | 2/2 |
| `moderated_completion_is_not_success` | 2/2 |
| `moderated_completion_is_refunded` | 2/2 |
| `no_direct_balance_writes` | 2/2 |

**free_quota**

| trap | baseline |
|---|---|
| `sixth_image_of_the_day_is_refused` | 2/2 |
| `refused_request_is_not_charged_and_not_sent_to_provider` | 2/2 |
| `limit_message_is_localized_and_names_the_limit` | 2/2 |
| `pro_users_are_unlimited` | 2/2 |
| `limit_is_per_user` | 2/2 |
| `failed_generations_do_not_count` | 2/2 |
| `insufficient_credits_attempt_does_not_count` | 2/2 |
| `retried_request_id_counts_once` | 2/2 |
| `videos_do_not_use_up_the_image_limit` | 2/2 |
| `limit_resets_at_utc_midnight` | 2/2 |
| `locale_files_in_sync` | 2/2 |
| `no_direct_balance_writes` | 2/2 |

