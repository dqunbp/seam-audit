"""Hidden grading tests for the `video_webhook` task. One test per seam trap."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from pixforge import clock
from pixforge.features.video import start_video
from pixforge.jobs import get_job
from pixforge.sweeper import expire_stale_jobs

from .conftest import balance, direct_balance_writes, lumen_signature, stored_in_our_bucket

SECRET = "whsec_lumen_test"
VIDEO_URL = "https://cdn.lumen.test/o/vid.mp4"


@pytest.fixture(autouse=True)
def real_time_clock():
    # Freeze at the real current time, so the handler accepts fresh signatures
    # whether it reads time via pixforge.clock or the system clock.
    clock.set_now(datetime.now(timezone.utc))
    yield
    clock.set_now(None)


@pytest.fixture
def video(conn, lumen, make_user):
    """A free user (balance 100) with one processing video job (cost 20)."""
    uid = make_user()
    r = start_video(conn, lumen, uid, "a cat surfing", "req-1", "https://pixforge.test/hooks/lumen")
    job = get_job(conn, r["job_id"])
    assert job["status"] == "processing" and balance(conn, uid) == 80
    return {"user_id": uid, "job_id": job["id"], "lumen_id": job["provider_job_id"]}


def handle(conn, body: bytes, headers: dict):
    from pixforge.webhooks.lumen import handle_lumen_webhook

    status, payload = handle_lumen_webhook(conn, body, headers, SECRET)
    return status


_ids = iter(range(1, 10_000))


def event(type_: str, data: dict, event_id: str | None = None) -> dict:
    return {
        "id": event_id or f"evt_{next(_ids)}",
        "type": type_,
        "created": int(clock.now().timestamp()),
        "data": data,
    }


def completed(lumen_id, videos=None, moderation=None, event_id=None):
    if videos is None:
        videos = [{"url": VIDEO_URL, "duration_s": 5}]
    return event("video.completed", {"job_id": lumen_id, "videos": videos, "moderation": moderation}, event_id)


def failed(lumen_id, event_id=None):
    return event("video.failed", {"job_id": lumen_id, "error": {"code": "render_error", "message": "x"}}, event_id)


def progress(lumen_id, value=0.5):
    return event("video.progress", {"job_id": lumen_id, "progress": value})


def deliver(conn, payload: dict, *, secret=SECRET, timestamp=None, signed=True):
    body = json.dumps(payload).encode()
    headers = {}
    if signed:
        ts = timestamp if timestamp is not None else int(clock.now().timestamp())
        headers["Lumen-Signature"] = lumen_signature(secret, body, ts)
    return handle(conn, body, headers)


def status_of(conn, video):
    return get_job(conn, video["job_id"])["status"]


# --- happy paths ----------------------------------------------------------------

def test_completed_marks_job_succeeded(conn, video):
    code = deliver(conn, completed(video["lumen_id"]))
    job = get_job(conn, video["job_id"])
    assert 200 <= code < 300
    assert job["status"] == "succeeded"
    assert job["output_key"]
    assert balance(conn, video["user_id"]) == 80


def test_video_is_copied_to_our_storage(conn, video, memory_storage):
    """Lumen output URLs expire after 24h: the job must point at our bucket."""
    deliver(conn, completed(video["lumen_id"]))
    job = get_job(conn, video["job_id"])
    assert stored_in_our_bucket(job["output_key"])
    assert memory_storage.objects[job["output_key"]] == VIDEO_URL


def test_event_before_job_is_recorded_gets_retried(conn, lumen, make_user):
    """The webhook can beat start_video's own commit: it must not be acked and lost."""
    uid = make_user()
    early = {}

    def deliver_early(video_id):
        early["event"] = completed(video_id, event_id="evt_early")
        early["code"] = deliver(conn, early["event"])

    lumen.on_create_video = deliver_early
    r = start_video(conn, lumen, uid, "quick clip", "req-early", "https://pixforge.test/hooks/lumen")
    lumen.on_create_video = None
    assert not 200 <= early["code"] < 300, "acknowledged an event it could not apply"
    retry = deliver(conn, early["event"])
    assert 200 <= retry < 300
    assert get_job(conn, r["job_id"])["status"] == "succeeded"


def test_failed_marks_job_failed_and_refunds(conn, video):
    code = deliver(conn, failed(video["lumen_id"]))
    assert 200 <= code < 300
    assert status_of(conn, video) == "failed"
    assert balance(conn, video["user_id"]) == 100


def test_progress_is_acknowledged_and_keeps_processing(conn, video):
    code = deliver(conn, progress(video["lumen_id"]))
    assert 200 <= code < 300
    assert status_of(conn, video) == "processing"


# --- signature (security seam) --------------------------------------------------

def test_wrong_signature_is_rejected(conn, video):
    code = deliver(conn, completed(video["lumen_id"]), secret="not-the-secret")
    assert 400 <= code < 500
    assert status_of(conn, video) == "processing"


def test_missing_signature_is_rejected(conn, video):
    code = deliver(conn, failed(video["lumen_id"]), signed=False)
    assert 400 <= code < 500
    assert balance(conn, video["user_id"]) == 80


def test_stale_signature_is_rejected(conn, video):
    old = int(clock.now().timestamp()) - 600
    code = deliver(conn, completed(video["lumen_id"]), timestamp=old)
    assert 400 <= code < 500
    assert status_of(conn, video) == "processing"


# --- at-least-once delivery / ordering (temporal seams) ----------------------------

def test_duplicate_failed_event_refunds_once(conn, video):
    payload = failed(video["lumen_id"], event_id="evt_dup")
    first = deliver(conn, payload)
    second = deliver(conn, payload)
    assert 200 <= first < 300 and 200 <= second < 300
    assert balance(conn, video["user_id"]) == 100


def test_duplicate_completed_event_is_harmless(conn, video):
    payload = completed(video["lumen_id"], event_id="evt_dup")
    deliver(conn, payload)
    code = deliver(conn, payload)
    assert 200 <= code < 300
    assert status_of(conn, video) == "succeeded"
    assert balance(conn, video["user_id"]) == 80


def test_progress_after_completed_keeps_succeeded(conn, video):
    deliver(conn, completed(video["lumen_id"]))
    deliver(conn, progress(video["lumen_id"], 0.9))
    assert status_of(conn, video) == "succeeded"


def test_failed_after_completed_does_not_refund(conn, video):
    deliver(conn, completed(video["lumen_id"]))
    deliver(conn, failed(video["lumen_id"]))
    assert status_of(conn, video) == "succeeded"
    assert balance(conn, video["user_id"]) == 80


def test_failed_after_sweeper_timeout_does_not_refund_twice(conn, video):
    real_now = clock.now()
    clock.set_now(real_now + timedelta(minutes=31))
    assert expire_stale_jobs(conn) == 1
    clock.set_now(real_now)
    assert balance(conn, video["user_id"]) == 100
    code = deliver(conn, failed(video["lumen_id"]))
    assert code < 500
    assert balance(conn, video["user_id"]) == 100


def test_unknown_job_does_not_crash(conn, video):
    deliver(conn, completed("vid_does_not_exist"))
    assert status_of(conn, video) == "processing"


# --- payload variants (external seam) ----------------------------------------------

def test_moderated_completion_is_not_success(conn, video):
    deliver(conn, completed(video["lumen_id"], videos=[], moderation={"reason": "policy"}))
    assert status_of(conn, video) != "succeeded"


def test_moderated_completion_is_refunded(conn, video):
    deliver(conn, completed(video["lumen_id"], videos=[], moderation={"reason": "policy"}))
    assert balance(conn, video["user_id"]) == 100


# --- canonical paths ----------------------------------------------------------------

def test_no_direct_balance_writes():
    assert direct_balance_writes() == []
