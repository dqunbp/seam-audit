"""Reference solution for the `upscale` task (used only to validate the hidden tests)."""
import logging

from lumen_sdk import LumenClient, LumenError, LumenRateLimited

from .. import jobs
from ..billing import InsufficientCredits, charge_credits
from ..i18n import t
from ..images import get_image, save_image
from ..jobs import JobStatus
from ..pricing import price_for
from ..users import get_user
from .common import fail_job, response_for

log = logging.getLogger(__name__)


def upscale_image(conn, client: LumenClient, user_id: int, image_id: int, request_id: str, locale: str = "en") -> dict:
    existing = jobs.get_job_by_request(conn, request_id)
    if existing is not None:
        return response_for(existing, locale)

    image = get_image(conn, image_id)
    if image is None or image["user_id"] != user_id:
        return {"ok": False, "job_id": None, "status": None, "error_code": "not_found",
                "message": t("errors.not_found", locale)}

    user = get_user(conn, user_id)
    cost = price_for("upscale", user["plan"])
    job_id = jobs.create_job(conn, user_id, "upscale", request_id, cost)
    conn.execute("UPDATE jobs SET source_image_id = ? WHERE id = ?", (image_id, job_id))

    try:
        charge_credits(conn, user_id, cost, "upscale", f"charge:upscale:{request_id}")
    except InsufficientCredits:
        fail_job(conn, job_id, "insufficient_credits", refund=False)
        return response_for(jobs.get_job(conn, job_id), locale)

    try:
        result = client.upscale(image["url"], factor=2)
    except LumenRateLimited:
        fail_job(conn, job_id, "rate_limited", refund=True)
        return response_for(jobs.get_job(conn, job_id), locale)
    except LumenError:
        log.exception("lumen upscale failed for job %s", job_id)
        fail_job(conn, job_id, "provider_failed", refund=True)
        return response_for(jobs.get_job(conn, job_id), locale)

    # `rejected` echoes the *input* image, so `image` alone does not mean success.
    if result.status != "succeeded" or result.image is None:
        error = "upscale_rejected" if result.status == "rejected" else "content_filtered"
        fail_job(conn, job_id, error, refund=True)
        return response_for(jobs.get_job(conn, job_id), locale)

    output = result.image
    save_image(conn, user_id, output.url, output.width, output.height)
    jobs.transition(conn, job_id, {JobStatus.PENDING}, JobStatus.SUCCEEDED, output_url=output.url)
    return response_for(jobs.get_job(conn, job_id), locale)
