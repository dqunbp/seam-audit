"""Text-to-image generation."""
import logging

from lumen_sdk import LumenClient, LumenError, LumenRateLimited

from .. import jobs
from ..billing import InsufficientCredits, charge_credits
from ..images import save_image
from ..jobs import JobStatus
from ..pricing import price_for
from ..users import get_user
from .common import fail_job, response_for

log = logging.getLogger(__name__)


def generate_image(conn, client: LumenClient, user_id: int, prompt: str, request_id: str, locale: str = "en") -> dict:
    """Generate one image from `prompt` and add it to the user's library.

    `request_id` comes from the client app, which retries on network errors:
    a repeated request_id returns the original job's result without charging again.

    Returns {"ok": True, "job_id", "status", "url"} or
            {"ok": False, "job_id", "status", "error_code", "message"}.
    """
    existing = jobs.get_job_by_request(conn, request_id)
    if existing is not None:
        return response_for(existing, locale)

    user = get_user(conn, user_id)
    cost = price_for("image", user["plan"])
    job_id = jobs.create_job(conn, user_id, "image", request_id, cost)

    try:
        charge_credits(conn, user_id, cost, "image", f"charge:image:{request_id}")
    except InsufficientCredits:
        fail_job(conn, job_id, "insufficient_credits", refund=False)
        return response_for(jobs.get_job(conn, job_id), locale)

    try:
        result = client.generate_image(prompt)
    except LumenRateLimited:
        fail_job(conn, job_id, "rate_limited", refund=True)
        return response_for(jobs.get_job(conn, job_id), locale)
    except LumenError:
        log.exception("lumen generate_image failed for job %s", job_id)
        fail_job(conn, job_id, "provider_failed", refund=True)
        return response_for(jobs.get_job(conn, job_id), locale)

    # "filtered" is a normal 200 response with no images, not an exception.
    if result.status != "succeeded" or not result.images:
        log.info("lumen filtered job %s: %s", job_id, result.filter_reason)
        fail_job(conn, job_id, "content_filtered", refund=True)
        return response_for(jobs.get_job(conn, job_id), locale)

    output = result.images[0]
    save_image(conn, user_id, output.url, output.width, output.height)
    jobs.transition(conn, job_id, {JobStatus.PENDING}, JobStatus.SUCCEEDED, output_url=output.url)
    return response_for(jobs.get_job(conn, job_id), locale)
