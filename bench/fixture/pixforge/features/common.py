"""Lifecycle shared by every paid, provider-backed feature.

    job = create_job(...)                 # one job per client request_id
    charge_credits(...)                   # idempotent per request_id
    call the provider
    succeed: transition(..., SUCCEEDED)   | fail: fail_job(..., refund=True)
    return response_for(job)
"""
from ..billing import refund_credits
from ..i18n import t
from ..jobs import JobStatus, get_job, transition


def refund_job(conn, job) -> None:
    """Return a job's cost to its owner. At most once per job, whoever calls it."""
    refund_credits(conn, job["user_id"], job["cost"], f"refund:{job['kind']}", f"refund:job:{job['id']}")


def fail_job(conn, job_id: int, error_code: str, *, refund: bool) -> bool:
    """Mark a non-terminal job failed with `error_code` (an `errors.*` i18n key suffix).

    Refunds only if this call actually moved the job to failed, so concurrent
    or repeated failure reports can't refund twice. Returns whether it moved.
    """
    moved = transition(
        conn, job_id, {JobStatus.PENDING, JobStatus.PROCESSING}, JobStatus.FAILED, error=error_code
    )
    if moved and refund:
        refund_job(conn, get_job(conn, job_id))
    return moved


def response_for(job, locale: str) -> dict:
    """The API response for a job's current state."""
    if job["status"] == JobStatus.SUCCEEDED:
        return {"ok": True, "job_id": job["id"], "status": job["status"], "url": job["output_url"]}
    if job["status"] in (JobStatus.PENDING, JobStatus.PROCESSING):
        return {"ok": True, "job_id": job["id"], "status": job["status"], "url": None}
    return {
        "ok": False,
        "job_id": job["id"],
        "status": job["status"],
        "error_code": job["error"],
        "message": t(f"errors.{job['error']}", locale, cost=job["cost"]),
    }
