from .. import clock


def mark_processed(conn, source: str, event_id: str) -> bool:
    cur = conn.execute(
        "INSERT OR IGNORE INTO processed_events (source, event_id, processed_at) VALUES (?, ?, ?)",
        (source, event_id, clock.iso_now()),
    )
    return cur.rowcount == 1
