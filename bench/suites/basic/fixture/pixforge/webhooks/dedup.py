from .. import clock


def mark_processed(conn, source: str, event_id: str) -> bool:
    """Record that an inbound event was handled. Returns False if it already was.

    Call it inside the same transaction as the event's side effects, so an
    event is never recorded without its effects (or applied without being recorded).
    """
    cur = conn.execute(
        "INSERT OR IGNORE INTO processed_events (source, event_id, processed_at) VALUES (?, ?, ?)",
        (source, event_id, clock.iso_now()),
    )
    return cur.rowcount == 1
