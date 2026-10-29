# Seam-audit benchmark — pretix-probe-haiku

31 runs. Score = share of hidden trap tests passed (mean ± sd over repetitions).

## haiku

| task | baseline | skill | placebo |
|---|---|---|---|
| expire_orders | 90% ± 6% (n=5) | 92% ± 7% (n=5) | 88% ± 0% (n=5) |
| extend_order | 100% ± 0% (n=1) | — | — |
| reactivate_order | 97% ± 4% (n=5) | 99% ± 3% (n=5) | 100% ± 0% (n=5) |
| **all** | **94%** | **96%** | **94%** |

| metric (mean per run) | baseline | skill | placebo |
|---|---|---|---|
| visible suite green | 100% | 100% | 100% |
| cost, $ | 0.03 | 0.04 | 0.03 |
| turns | 27.4 | 37.0 | 29.0 |
| files read | 1.6 | 4.2 | 2.8 |
| diff lines | 168.5 | 183.6 | 154.1 |
| skill invoked | 0% | 100% | 100% |
| seam table in output | 0% | 70% | 0% |

### Per-trap pass rate

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

