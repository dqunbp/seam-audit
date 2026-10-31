"""Per-user daily usage limits for the free plan."""
from . import clock
from .db import transaction

# Free plan: maximum operations of each kind per UTC calendar day.
# Kinds not listed here are unlimited.
FREE_DAILY_LIMITS = {
    "video": 2,
}


def limit_for(kind: str, plan: str) -> int | None:
    if plan != "free":
        return None
    return FREE_DAILY_LIMITS.get(kind)


def consume(conn, user_id: int, kind: str, limit: int, day: str | None = None) -> bool:
    """Take one unit of the user's quota for `day`. Returns False if the limit is reached."""
    day = day or clock.today_utc()
    with transaction(conn):
        conn.execute(
            "INSERT INTO quota_usage (user_id, kind, day, used) VALUES (?, ?, ?, 0)"
            " ON CONFLICT (user_id, kind, day) DO NOTHING",
            (user_id, kind, day),
        )
        cur = conn.execute(
            "UPDATE quota_usage SET used = used + 1"
            " WHERE user_id = ? AND kind = ? AND day = ? AND used < ?",
            (user_id, kind, day, limit),
        )
        return cur.rowcount == 1


def release(conn, user_id: int, kind: str, day: str) -> None:
    """Give back one unit taken by `consume`."""
    conn.execute(
        "UPDATE quota_usage SET used = used - 1"
        " WHERE user_id = ? AND kind = ? AND day = ? AND used > 0",
        (user_id, kind, day),
    )


def used(conn, user_id: int, kind: str, day: str | None = None) -> int:
    day = day or clock.today_utc()
    row = conn.execute(
        "SELECT used FROM quota_usage WHERE user_id = ? AND kind = ? AND day = ?",
        (user_id, kind, day),
    ).fetchone()
    return row["used"] if row else 0
