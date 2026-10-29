from lumen_sdk import LumenAPIError

from pixforge import quota
from pixforge.billing import get_balance
from pixforge.features.video import start_video
from pixforge.jobs import get_job

CALLBACK = "https://pixforge.test/hooks/lumen"


def test_start_video_charges_and_stays_processing(conn, lumen, user_id):
    response = start_video(conn, lumen, user_id, "a cat surfing", "req-1", CALLBACK)
    assert response["ok"]
    assert response["status"] == "processing"
    job = get_job(conn, response["job_id"])
    assert job["provider_job_id"].startswith("vid_")
    assert get_balance(conn, user_id) == 80


def test_free_daily_video_limit(conn, lumen, user_id):
    assert start_video(conn, lumen, user_id, "1", "req-1", CALLBACK)["ok"]
    assert start_video(conn, lumen, user_id, "2", "req-2", CALLBACK)["ok"]
    third = start_video(conn, lumen, user_id, "3", "req-3", CALLBACK, locale="en")
    assert not third["ok"]
    assert third["error_code"] == "daily_video_limit"
    assert get_balance(conn, user_id) == 60


def test_provider_error_refunds_and_releases_quota(conn, lumen, user_id):
    lumen.fail_with = LumenAPIError(500, "internal", "boom")
    response = start_video(conn, lumen, user_id, "1", "req-1", CALLBACK)
    assert response["error_code"] == "provider_failed"
    assert get_balance(conn, user_id) == 100
    assert quota.used(conn, user_id, "video") == 0
