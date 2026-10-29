from datetime import timedelta

from pixforge import clock
from pixforge.billing import get_balance
from pixforge.features.video import start_video
from pixforge.jobs import get_job
from pixforge.sweeper import expire_stale_jobs


def test_stale_processing_job_times_out_and_is_refunded(conn, lumen, user_id):
    job_id = start_video(conn, lumen, user_id, "x", "req-1", "https://cb")["job_id"]
    clock.set_now(clock.now() + timedelta(minutes=31))
    assert expire_stale_jobs(conn) == 1
    assert get_job(conn, job_id)["status"] == "timed_out"
    assert get_balance(conn, user_id) == 100
    # Running again does nothing.
    assert expire_stale_jobs(conn) == 0
    assert get_balance(conn, user_id) == 100
