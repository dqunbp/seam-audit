import pytest

from pixforge.billing import InsufficientCredits, charge_credits, get_balance, refund_credits


def test_charge_deducts(conn, user_id):
    result = charge_credits(conn, user_id, 10, "test", "k1")
    assert result.applied
    assert get_balance(conn, user_id) == 90


def test_same_key_applies_once(conn, user_id):
    charge_credits(conn, user_id, 10, "test", "k1")
    again = charge_credits(conn, user_id, 10, "test", "k1")
    assert not again.applied
    assert get_balance(conn, user_id) == 90


def test_insufficient_credits(conn, user_id):
    with pytest.raises(InsufficientCredits):
        charge_credits(conn, user_id, 1000, "test", "k1")
    assert get_balance(conn, user_id) == 100


def test_refund_same_key_applies_once(conn, user_id):
    charge_credits(conn, user_id, 10, "test", "c1")
    refund_credits(conn, user_id, 10, "test", "refund:job:1")
    refund_credits(conn, user_id, 10, "test", "refund:job:1")
    assert get_balance(conn, user_id) == 100
