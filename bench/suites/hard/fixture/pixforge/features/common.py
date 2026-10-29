from .. import storage
from ..billing import refund_credits
from ..i18n import t
from ..jobs import JobStatus, get_job, transition


def refund_job(conn, job) -> None:
    refund_credits(conn, job["user_id"], job["cost"], f"refund:{job['kind']}", f"refund:job:{job['id']}")


def fail_job(conn, job_id: int, error_code: str, *, refund: bool) -> bool:
    moved = transition(
        conn, job_id, {JobStatus.PENDING, JobStatus.PROCESSING}, JobStatus.FAILED, error=error_code
    )
    if moved and refund:
        refund_job(conn, get_job(conn, job_id))
    return moved


def response_for(job, locale: str) -> dict:
    if job["status"] == JobStatus.SUCCEEDED:
        return {"ok": True, "job_id": job["id"], "status": job["status"], "url": storage.public_url(job["output_key"])}
    if job["status"] in (JobStatus.PENDING, JobStatus.PROCESSING):
        return {"ok": True, "job_id": job["id"], "status": job["status"], "url": None}
    return {
        "ok": False,
        "job_id": job["id"],
        "status": job["status"],
        "error_code": job["error"],
        "message": t(f"errors.{job['error']}", locale, cost=job["cost"]),
    }
