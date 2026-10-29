"""Periodic cleanup: time out jobs stuck in `processing` and refund them."""
import logging
from datetime import timedelta

from . import clock, jobs
from .features.common import refund_job
from .jobs import JobStatus

log = logging.getLogger(__name__)

MAX_PROCESSING_AGE = timedelta(minutes=30)


def expire_stale_jobs(conn, max_age: timedelta = MAX_PROCESSING_AGE) -> int:
    """Move `processing` jobs not updated for `max_age` to `timed_out` and refund them."""
    cutoff = (clock.now() - max_age).isoformat()
    stale = conn.execute(
        "SELECT * FROM jobs WHERE status = ? AND updated_at < ?", (JobStatus.PROCESSING, cutoff)
    ).fetchall()
    expired = 0
    for job in stale:
        if jobs.transition(conn, job["id"], {JobStatus.PROCESSING}, JobStatus.TIMED_OUT, error="timed_out"):
            refund_job(conn, job)
            expired += 1
    if expired:
        log.warning("expired %d stale jobs", expired)
    return expired
