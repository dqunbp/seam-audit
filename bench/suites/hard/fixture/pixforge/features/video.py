"""Text-to-video generation (asynchronous on Lumen's side)."""
import logging

from lumen_sdk import LumenClient, LumenError, LumenRateLimited

from .. import clock, jobs, quota
from ..billing import InsufficientCredits, charge_credits
from ..i18n import t
from ..jobs import JobStatus
from ..pricing import price_for
from ..users import get_user
from .common import fail_job, response_for

log = logging.getLogger(__name__)


def start_video(
    conn,
    client: LumenClient,
    user_id: int,
    prompt: str,
    request_id: str,
    callback_url: str,
    locale: str = "en",
) -> dict:
    """Start rendering a video."""
    existing = jobs.get_job_by_request(conn, request_id)
    if existing is not None:
        return response_for(existing, locale)

    user = get_user(conn, user_id)
    day = clock.today_utc()
    limit = quota.limit_for("video", user["plan"])
    if limit is not None and not quota.consume(conn, user_id, "video", limit, day):
        return {
            "ok": False,
            "job_id": None,
            "status": None,
            "error_code": "daily_video_limit",
            "message": t("errors.daily_video_limit", locale, limit=limit),
        }

    cost = price_for("video", user["plan"])
    job_id = jobs.create_job(conn, user_id, "video", request_id, cost)

    try:
        charge_credits(conn, user_id, cost, "video", f"charge:video:{request_id}")
    except InsufficientCredits:
        if limit is not None:
            quota.release(conn, user_id, "video", day)
        fail_job(conn, job_id, "insufficient_credits", refund=False)
        return response_for(jobs.get_job(conn, job_id), locale)

    try:
        lumen_job = client.create_video(prompt, callback_url=callback_url)
    except LumenError as exc:
        log.exception("lumen create_video failed for job %s", job_id)
        if limit is not None:
            quota.release(conn, user_id, "video", day)
        error = "rate_limited" if isinstance(exc, LumenRateLimited) else "provider_failed"
        fail_job(conn, job_id, error, refund=True)
        return response_for(jobs.get_job(conn, job_id), locale)

    jobs.transition(
        conn, job_id, {JobStatus.PENDING}, JobStatus.PROCESSING, provider_job_id=lumen_job.id
    )
    return response_for(jobs.get_job(conn, job_id), locale)
