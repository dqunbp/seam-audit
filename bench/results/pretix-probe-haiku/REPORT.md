# Seam-audit benchmark — pretix-probe-haiku

76 runs. Score = share of hidden trap tests passed (mean ± sd over repetitions).

## haiku

| task | baseline | skill | placebo |
|---|---|---|---|
| cancel_order | 78% ± 4% (n=5) | 76% ± 9% (n=5) | 65% ± 12% (n=5) |
| expire_orders | 90% ± 6% (n=5) | 92% ± 7% (n=5) | 88% ± 0% (n=5) |
| extend_order | 100% ± 0% (n=1) | — | — |
| reactivate_order | 97% ± 4% (n=5) | 99% ± 3% (n=5) | 100% ± 0% (n=5) |
| send_download_reminders | 59% ± 6% (n=5) | 62% ± 10% (n=5) | 60% ± 6% (n=5) |
| send_expiry_warnings | 67% ± 0% (n=5) | 64% ± 12% (n=5) | 62% ± 10% (n=5) |
| **all** | **79%** | **79%** | **75%** |

| metric (mean per run) | baseline | skill | placebo |
|---|---|---|---|
| visible suite green | 88% | 88% | 80% |
| cost, $ | 0.11 | 0.11 | 0.07 |
| turns | 34.7 | 42.3 | 35.1 |
| files read | 1.5 | 4.3 | 3.1 |
| diff lines | 217.1 | 203.8 | 190.1 |
| skill invoked | 0% | 100% | 100% |
| seam table in output | 0% | 72% | 0% |

### Per-trap pass rate

**cancel_order**

| trap | baseline | skill | placebo |
|---|---|---|---|
| `base.test_orders.OrderCancelTests::test_auto_refund_impossible` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderCancelTests::test_auto_refund_impossible_issued_giftcard_used` | 5/5 | 5/5 | 3/5 |
| `base.test_orders.OrderCancelTests::test_auto_refund_possible` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderCancelTests::test_auto_refund_possible_giftcard` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderCancelTests::test_auto_refund_possible_issued_giftcard` | 5/5 | 5/5 | 3/5 |
| `base.test_orders.OrderCancelTests::test_cancel_canceled` | 5/5 | 5/5 | 4/5 |
| `base.test_orders.OrderCancelTests::test_cancel_mail_invoice_attached` | 0/5 | 0/5 | 0/5 |
| `base.test_orders.OrderCancelTests::test_cancel_mail_invoice_sent_somewhere_else` | 0/5 | 0/5 | 0/5 |
| `base.test_orders.OrderCancelTests::test_cancel_paid` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderCancelTests::test_cancel_paid_with_fee` | 0/5 | 0/5 | 0/5 |
| `base.test_orders.OrderCancelTests::test_cancel_paid_with_fee_change_secret` | 5/5 | 4/5 | 2/5 |
| `base.test_orders.OrderCancelTests::test_cancel_paid_with_too_high_fee` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderCancelTests::test_cancel_send_mail` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderCancelTests::test_cancel_send_no_mail` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderCancelTests::test_cancel_unpaid` | 2/5 | 3/5 | 3/5 |
| `base.test_orders.OrderCancelTests::test_cancel_unpaid_with_voucher` | 5/5 | 4/5 | 5/5 |
| `base.test_orders.OrderChangeManagerTests::test_clear_out_order` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderChangeManagerTests::test_clear_out_order_change_secrets` | 5/5 | 4/5 | 2/5 |
| `base.test_orders.OrderChangeManagerTests::test_cancel_order_membership` | 2/5 | 2/5 | 0/5 |

**expire_orders**

| trap | baseline | skill | placebo |
|---|---|---|---|
| `base.test_orders::test_expiring` | 5/5 | 5/5 | 5/5 |
| `base.test_orders::test_expiring_paid_invoice` | 5/5 | 5/5 | 5/5 |
| `base.test_orders::test_expire_twice` | 5/5 | 5/5 | 5/5 |
| `base.test_orders::test_expire_skipped_if_canceled_with_fee` | 5/5 | 5/5 | 4/5 |
| `base.test_orders::test_expiring_auto_disabled` | 5/5 | 5/5 | 5/5 |
| `base.test_orders::test_expiring_auto_delayed` | 1/5 | 2/5 | 1/5 |
| `base.test_orders::test_expiring_auto_delayed_weekdays` | 5/5 | 5/5 | 5/5 |
| `base.test_orders::test_do_not_expire_if_approval_pending` | 5/5 | 5/5 | 5/5 |

**extend_order**

| trap | baseline | skill | placebo |
|---|---|---|---|
| `api.test_orders::test_order_extend_paid` | 1/1 | 0/0 | 0/0 |
| `api.test_orders::test_order_extend_pending` | 1/1 | 0/0 | 0/0 |
| `api.test_orders::test_order_extend_expired_quota_empty` | 1/1 | 0/0 | 0/0 |
| `api.test_orders::test_order_extend_expired_quota_ignore` | 1/1 | 0/0 | 0/0 |
| `api.test_orders::test_order_extend_expired_quota_waiting_list` | 1/1 | 0/0 | 0/0 |
| `api.test_orders::test_order_extend_expired_quota_left` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_not_pending` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_not_expired` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_overdue_quota_empty` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_overdue_quota_blocked_by_waiting_list` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_expired_quota_left` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_expired_quota_empty` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_expired_quota_empty_ignore` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_expired_seat_free` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_expired_seat_blocked` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_expired_seat_taken` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_expired_quota_partial` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_expired_voucher_budget_ok` | 1/1 | 0/0 | 0/0 |
| `control.test_orders::test_order_extend_expired_voucher_budget_fail` | 1/1 | 0/0 | 0/0 |

**reactivate_order**

| trap | baseline | skill | placebo |
|---|---|---|---|
| `base.test_orders.OrderReactivateTest::test_paid` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderReactivateTest::test_reactivate_gift_card` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderReactivateTest::test_reactivate_membership` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderReactivateTest::test_reactivate_paid` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderReactivateTest::test_reactivate_seat_taken` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderReactivateTest::test_reactivate_sold_out` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderReactivateTest::test_reactivate_unpaid` | 3/5 | 4/5 | 5/5 |
| `base.test_orders.OrderReactivateTest::test_reactivate_voucher_budget` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderReactivateTest::test_reactivate_voucher_ok` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.OrderReactivateTest::test_reactivate_voucher_used` | 5/5 | 5/5 | 5/5 |
| `api.test_orders::test_order_reactivate` | 5/5 | 5/5 | 5/5 |
| `api.test_orders::test_order_reactivate_invalid` | 5/5 | 5/5 | 5/5 |
| `control.test_orders::test_order_reactivate_not_canceled` | 5/5 | 5/5 | 5/5 |
| `control.test_orders::test_order_reactivate` | 5/5 | 5/5 | 5/5 |

**send_download_reminders**

| trap | baseline | skill | placebo |
|---|---|---|---|
| `base.test_orders.DownloadReminderTests::test_disabled` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.DownloadReminderTests::test_downloads_all_allowed_by_plugin` | 1/5 | 2/5 | 2/5 |
| `base.test_orders.DownloadReminderTests::test_downloads_disabled` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.DownloadReminderTests::test_downloads_disabled_by_plugin` | 0/5 | 1/5 | 0/5 |
| `base.test_orders.DownloadReminderTests::test_downloads_disabled_per_product` | 0/5 | 1/5 | 0/5 |
| `base.test_orders.DownloadReminderTests::test_downloads_partially_disabled_by_plugin` | 1/5 | 2/5 | 2/5 |
| `base.test_orders.DownloadReminderTests::test_not_sent_after_reminder_date` | 0/5 | 2/5 | 0/5 |
| `base.test_orders.DownloadReminderTests::test_not_sent_for_disabled_sales_channel` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.DownloadReminderTests::test_not_sent_too_early` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.DownloadReminderTests::test_not_sent_too_soon_after_purchase` | 0/5 | 2/5 | 0/5 |
| `base.test_orders.DownloadReminderTests::test_send_not_to_attendees_with_same_address` | 5/5 | 3/5 | 4/5 |
| `base.test_orders.DownloadReminderTests::test_send_to_attendees` | 5/5 | 3/5 | 5/5 |
| `base.test_orders.DownloadReminderTests::test_send_to_attendees_subevent_future` | 0/5 | 0/5 | 0/5 |
| `base.test_orders.DownloadReminderTests::test_send_to_attendees_subevent_past` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.DownloadReminderTests::test_sent_once` | 5/5 | 4/5 | 5/5 |
| `base.test_orders.DownloadReminderTests::test_sent_paid_only` | 5/5 | 5/5 | 5/5 |

**send_expiry_warnings**

| trap | baseline | skill | placebo |
|---|---|---|---|
| `base.test_orders.PaymentReminderTests::test_disabled` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.PaymentReminderTests::test_paid` | 5/5 | 5/5 | 5/5 |
| `base.test_orders.PaymentReminderTests::test_prevent_reminder_mail` | 0/5 | 2/5 | 1/5 |
| `base.test_orders.PaymentReminderTests::test_prevent_reminder_mail_confirmed_but_not_all_paid` | 5/5 | 4/5 | 4/5 |
| `base.test_orders.PaymentReminderTests::test_prevent_reminder_mail_failed_state` | 5/5 | 4/5 | 4/5 |
| `base.test_orders.PaymentReminderTests::test_sent_days` | 5/5 | 4/5 | 4/5 |
| `base.test_orders.PaymentReminderTests::test_sent_no_expiry` | 0/5 | 0/5 | 0/5 |
| `base.test_orders.PaymentReminderTests::test_sent_not_immediately_after_purchase` | 0/5 | 1/5 | 1/5 |
| `base.test_orders.PaymentReminderTests::test_sent_once` | 5/5 | 4/5 | 4/5 |

