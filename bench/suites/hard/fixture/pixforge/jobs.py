"""Job records and their status lifecycle.

    pending ──► processing ──► succeeded
       │             │    └──► failed
       │             └───────► timed_out   (sweeper)
       ├──► succeeded
       └──► failed

succeeded / failed / timed_out are terminal: a job never leaves them.
"""
from enum import StrEnum

from . import clock


class JobStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


TERMINAL = frozenset({JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.TIMED_OUT})

_UPDATABLE_FIELDS = {"provider_job_id", "output_key", "error"}


def create_job(conn, user_id: int, kind: str, request_id: str, cost: int) -> int:
    now = clock.iso_now()
    cur = conn.execute(
        "INSERT INTO jobs (user_id, kind, status, request_id, cost, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, kind, JobStatus.PENDING, request_id, cost, now, now),
    )
    return cur.lastrowid


def get_job(conn, job_id: int):
    return conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()


def get_job_by_request(conn, request_id: str):
    return conn.execute("SELECT * FROM jobs WHERE request_id = ?", (request_id,)).fetchone()


def get_job_by_provider_id(conn, provider_job_id: str):
    return conn.execute(
        "SELECT * FROM jobs WHERE provider_job_id = ?", (provider_job_id,)
    ).fetchone()


def transition(conn, job_id: int, from_statuses, to_status: JobStatus, **fields) -> bool:
    """Move a job from one of `from_statuses` to `to_status`. Returns whether it moved."""
    unknown = set(fields) - _UPDATABLE_FIELDS
    if unknown:
        raise ValueError(f"cannot update job fields: {sorted(unknown)}")
    from_statuses = [str(s) for s in from_statuses]
    assignments = ", ".join(f"{name} = ?" for name in fields)
    sql = "UPDATE jobs SET status = ?, updated_at = ?"
    if assignments:
        sql += ", " + assignments
    sql += f" WHERE id = ? AND status IN ({', '.join('?' for _ in from_statuses)})"
    params = [str(to_status), clock.iso_now(), *fields.values(), job_id, *from_statuses]
    return conn.execute(sql, params).rowcount == 1
