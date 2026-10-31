"""The application's time source.

Always read time through this module (never `datetime.now()` / `date.today()`
directly): tests freeze it with `set_now()`, and all dates are UTC.
"""
from datetime import datetime, timezone

_frozen: datetime | None = None


def now() -> datetime:
    return _frozen if _frozen is not None else datetime.now(timezone.utc)


def set_now(value: datetime | None) -> None:
    """Freeze the clock at `value` (tz-aware), or unfreeze with None."""
    global _frozen
    _frozen = value


def iso_now() -> str:
    return now().isoformat()


def today_utc() -> str:
    """Current calendar day in UTC, as YYYY-MM-DD."""
    return now().astimezone(timezone.utc).date().isoformat()
