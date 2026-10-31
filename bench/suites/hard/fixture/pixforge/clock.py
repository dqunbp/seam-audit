"""Time helpers."""
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
