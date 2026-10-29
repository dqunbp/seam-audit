"""Credit balance operations."""
from dataclasses import dataclass

from . import clock
from .db import transaction


class InsufficientCredits(Exception):
    def __init__(self, user_id: int, needed: int, balance: int):
        super().__init__(f"user {user_id} needs {needed} credits, has {balance}")
        self.needed = needed
        self.balance = balance


@dataclass(frozen=True)
class LedgerResult:
    applied: bool  # False when the idempotency key had already been used
    balance: int


def get_balance(conn, user_id: int) -> int:
    row = conn.execute("SELECT balance FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise LookupError(f"user {user_id} not found")
    return row["balance"]


def _apply(conn, user_id: int, delta: int, reason: str, idempotency_key: str) -> LedgerResult:
    with transaction(conn):
        seen = conn.execute(
            "SELECT 1 FROM credit_ledger WHERE idempotency_key = ?", (idempotency_key,)
        ).fetchone()
        if seen:
            return LedgerResult(applied=False, balance=get_balance(conn, user_id))
        balance = get_balance(conn, user_id)
        if balance + delta < 0:
            raise InsufficientCredits(user_id, -delta, balance)
        conn.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (delta, user_id))
        conn.execute(
            "INSERT INTO credit_ledger (user_id, delta, reason, idempotency_key, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (user_id, delta, reason, idempotency_key, clock.iso_now()),
        )
        return LedgerResult(applied=True, balance=balance + delta)


def charge_credits(conn, user_id: int, amount: int, reason: str, idempotency_key: str) -> LedgerResult:
    """Deduct `amount` credits. Raises InsufficientCredits if the balance is too low."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    return _apply(conn, user_id, -amount, reason, idempotency_key)


def refund_credits(conn, user_id: int, amount: int, reason: str, idempotency_key: str) -> LedgerResult:
    if amount <= 0:
        raise ValueError("amount must be positive")
    return _apply(conn, user_id, amount, reason, idempotency_key)


def grant_credits(conn, user_id: int, amount: int, reason: str, idempotency_key: str) -> LedgerResult:
    """Add purchased or promotional credits."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    return _apply(conn, user_id, amount, reason, idempotency_key)
