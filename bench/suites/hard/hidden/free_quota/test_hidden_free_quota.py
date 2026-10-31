"""Hidden grading tests for the `free_quota` task. One test per seam trap."""
from datetime import datetime, timezone

from lumen_sdk import LumenAPIError
from pixforge import clock
from pixforge.billing import grant_credits
from pixforge.features.generate import generate_image
from pixforge.features.video import start_video

from .conftest import CYRILLIC, balance, direct_balance_writes, locale_keys_in_sync


def gen(conn, lumen, uid, rid, locale="en"):
    return generate_image(conn, lumen, uid, "a cat", rid, locale=locale)


def burn(conn, lumen, uid, n, prefix="r"):
    """Generate n images; return how many succeeded."""
    return sum(bool(gen(conn, lumen, uid, f"{prefix}{uid}-{i}")["ok"]) for i in range(n))


# --- the limit itself ---------------------------------------------------------------

def test_sixth_image_of_the_day_is_refused(conn, lumen, make_user):
    uid = make_user()
    assert burn(conn, lumen, uid, 5) == 5
    assert gen(conn, lumen, uid, "sixth")["ok"] is False


def test_refused_request_is_not_charged_and_not_sent_to_provider(conn, lumen, make_user):
    uid = make_user()
    burn(conn, lumen, uid, 5)
    gen(conn, lumen, uid, "sixth")
    assert balance(conn, uid) == 90
    assert lumen.calls_to("generate_image") == 5


def test_limit_message_is_localized_and_names_the_limit(conn, lumen, make_user):
    uid = make_user()
    burn(conn, lumen, uid, 5)
    ru = gen(conn, lumen, uid, "sixth-ru", locale="ru")
    en = gen(conn, lumen, uid, "sixth-en", locale="en")
    assert CYRILLIC.search(ru["message"]) and "5" in ru["message"]
    assert "5" in en["message"] and not CYRILLIC.search(en["message"])


def test_pro_users_are_unlimited(conn, lumen, make_user):
    free = make_user()
    assert burn(conn, lumen, free, 6) == 5
    uid = make_user(plan="pro")
    assert burn(conn, lumen, uid, 7) == 7


def test_limit_is_per_user(conn, lumen, make_user):
    a, b = make_user(), make_user()
    assert burn(conn, lumen, a, 6) == 5
    assert burn(conn, lumen, b, 5) == 5


# --- what counts against the limit ----------------------------------------------------

def test_failed_generations_do_not_count(conn, lumen, make_user):
    uid = make_user()
    lumen.fail_with = LumenAPIError(500, "internal", "boom")
    assert gen(conn, lumen, uid, "err")["ok"] is False
    lumen.image_mode = "filtered"
    assert gen(conn, lumen, uid, "filtered")["ok"] is False
    lumen.image_mode = "succeeded"
    assert burn(conn, lumen, uid, 6) == 5


def test_insufficient_credits_attempt_does_not_count(conn, lumen, make_user):
    uid = make_user(balance=0)
    assert gen(conn, lumen, uid, "broke")["ok"] is False
    grant_credits(conn, uid, 100, "test", "test-topup")
    assert burn(conn, lumen, uid, 6) == 5


def test_retried_request_id_counts_once(conn, lumen, make_user):
    uid = make_user()
    ids = ["a", "a", "b", "c", "d", "e"]
    assert all(gen(conn, lumen, uid, rid)["ok"] for rid in ids)
    assert gen(conn, lumen, uid, "f")["ok"] is False


def test_videos_do_not_use_up_the_image_limit(conn, lumen, make_user):
    uid = make_user()
    assert start_video(conn, lumen, uid, "v1", "v1", "https://cb")["ok"]
    assert start_video(conn, lumen, uid, "v2", "v2", "https://cb")["ok"]
    assert burn(conn, lumen, uid, 6) == 5


# --- the day boundary (time seam) -----------------------------------------------------

def test_limit_resets_at_utc_midnight(conn, lumen, make_user):
    uid = make_user()
    clock.set_now(datetime(2026, 3, 1, 23, 30, tzinfo=timezone.utc))
    burn(conn, lumen, uid, 5, prefix="d1-")
    assert gen(conn, lumen, uid, "late")["ok"] is False
    clock.set_now(datetime(2026, 3, 2, 0, 10, tzinfo=timezone.utc))
    assert gen(conn, lumen, uid, "next-day")["ok"] is True


# --- strings / canonical paths -----------------------------------------------------------

def test_locale_files_in_sync():
    assert locale_keys_in_sync()


def test_no_direct_balance_writes():
    assert direct_balance_writes() == []
