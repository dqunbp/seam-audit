"""Reference solution for the `video_webhook` task (used only to validate the hidden tests)."""
import json
import logging

from .. import jobs, storage
from ..db import transaction
from ..features.common import fail_job
from ..jobs import JobStatus
from .dedup import mark_processed
from .signing import verify_signature

log = logging.getLogger(__name__)

TERMINAL_EVENTS = ("video.completed", "video.failed")


def handle_lumen_webhook(conn, raw_body: bytes, headers: dict, secret: str) -> tuple[int, dict]:
    if not verify_signature(secret, raw_body, headers.get("Lumen-Signature")):
        return 400, {"error": "invalid signature"}
    try:
        event = json.loads(raw_body)
    except ValueError:
        return 400, {"error": "invalid json"}

    event_type = event.get("type")
    data = event.get("data") or {}
    if event_type not in TERMINAL_EVENTS:
        return 200, {"ignored": event_type}

    job = jobs.get_job_by_provider_id(conn, data.get("job_id"))
    if job is None:
        # Possibly delivered before start_video recorded the provider id: make Lumen retry.
        log.warning("lumen event %s for unknown job %s", event.get("id"), data.get("job_id"))
        return 409, {"error": "unknown job"}

    with transaction(conn):
        if not mark_processed(conn, "lumen", event["id"]):
            return 200, {"duplicate": True}
        videos = data.get("videos") or []
        if event_type == "video.completed" and videos:
            key = storage.import_remote(videos[0]["url"])
            jobs.transition(conn, job["id"], {JobStatus.PROCESSING}, JobStatus.SUCCEEDED, output_key=key)
        else:
            error = "content_filtered" if event_type == "video.completed" else "provider_failed"
            fail_job(conn, job["id"], error, refund=True)
    return 200, {"ok": True}
