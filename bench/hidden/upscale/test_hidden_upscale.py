"""Hidden grading tests for the `upscale` task. One test per seam trap."""

from lumen_sdk import LumenAPIError, LumenRateLimited
from pixforge import db
from pixforge.jobs import get_job

from .conftest import CYRILLIC, REPO, balance, charges, direct_balance_writes, image_count, locale_keys_in_sync


def upscale(*args, **kwargs):
    from pixforge.features.upscale import upscale_image

    return upscale_image(*args, **kwargs)


def attempt(*args, **kwargs):
    """Call upscale; an exception from inside it counts as a refusal (some designs raise for bad input)."""
    from pixforge.features.upscale import upscale_image

    try:
        return upscale_image(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "raised": repr(exc)}


# --- happy path -------------------------------------------------------------

def test_happy_path_charges_4_and_saves_2x_image(conn, lumen, make_user, make_image):
    uid = make_user()
    img = make_image(uid, 1024, 768)
    r = upscale(conn, lumen, uid, img, "req-1")
    assert r["ok"] is True
    assert balance(conn, uid) == 96
    rows = conn.execute("SELECT width, height FROM images WHERE user_id = ? ORDER BY id", (uid,)).fetchall()
    assert [tuple(row) for row in rows] == [(1024, 768), (2048, 1536)]


def test_job_records_source_image_id(conn, lumen, make_user, make_image):
    uid = make_user()
    img = make_image(uid)
    r = upscale(conn, lumen, uid, img, "req-1")
    job = get_job(conn, r["job_id"])
    assert job["status"] == "succeeded"
    assert job["source_image_id"] == img
    assert job["output_url"] == r["url"]


def test_migration_applies_to_already_migrated_database(conn):
    """Prod DBs already ran 001/002: the new column must come from a new migration."""
    prod = db.connect()
    prod.execute("CREATE TABLE schema_migrations (name TEXT PRIMARY KEY)")
    original = REPO / "tests_hidden" / "orig_migrations"
    for path in sorted(original.glob("*.sql")):
        prod.executescript(path.read_text(encoding="utf-8"))
        prod.execute("INSERT INTO schema_migrations (name) VALUES (?)", (path.name,))
    prod.execute("INSERT INTO users (email) VALUES ('old@example.com')")
    db.migrate(prod)
    columns = {row["name"] for row in prod.execute("PRAGMA table_info(jobs)")}
    assert "source_image_id" in columns
    assert prod.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1


# --- pricing ------------------------------------------------------------------

def test_pro_user_pays_discounted_price(conn, lumen, make_user, make_image):
    uid = make_user(plan="pro")
    upscale(conn, lumen, uid, make_image(uid), "req-1")
    assert balance(conn, uid) == 98


# --- retries (temporal seam) ------------------------------------------------

def test_retry_with_same_request_id_charges_once(conn, lumen, make_user, make_image):
    uid = make_user()
    img = make_image(uid)
    first = upscale(conn, lumen, uid, img, "req-1")
    second = attempt(conn, lumen, uid, img, "req-1")
    assert first["ok"] is True
    assert balance(conn, uid) == 96
    assert charges(conn, uid) == 1
    assert second.get("ok") is True


def test_retry_does_not_upscale_again(conn, lumen, make_user, make_image):
    uid = make_user()
    img = make_image(uid)
    upscale(conn, lumen, uid, img, "req-1")
    attempt(conn, lumen, uid, img, "req-1")
    assert lumen.calls_to("upscale") == 1
    assert image_count(conn, uid) == 2


# --- provider response variants (external seam) -----------------------------

def test_rejected_input_is_not_reported_as_success(conn, lumen, make_user, make_image):
    """`rejected` echoes the input image; it must not be saved as an upscale."""
    uid = make_user()
    img = make_image(uid, 3000, 2000)
    r = attempt(conn, lumen, uid, img, "req-1")
    assert r["ok"] is False
    assert image_count(conn, uid) == 1


def test_rejected_input_costs_nothing(conn, lumen, make_user, make_image):
    uid = make_user()
    img = make_image(uid, 3000, 2000)
    attempt(conn, lumen, uid, img, "req-1")
    assert balance(conn, uid) == 100


def test_filtered_result_is_refunded(conn, lumen, make_user, make_image):
    uid = make_user()
    lumen.upscale_mode = "filtered"
    r = attempt(conn, lumen, uid, make_image(uid), "req-1")
    assert r["ok"] is False
    assert balance(conn, uid) == 100
    assert image_count(conn, uid) == 1


def test_provider_error_is_refunded(conn, lumen, make_user, make_image):
    uid = make_user()
    lumen.fail_with = LumenAPIError(500, "internal", "boom")
    r = upscale(conn, lumen, uid, make_image(uid), "req-1")
    assert r["ok"] is False
    assert balance(conn, uid) == 100


def test_rate_limit_is_refunded(conn, lumen, make_user, make_image):
    uid = make_user()
    lumen.fail_with = LumenRateLimited(5)
    r = upscale(conn, lumen, uid, make_image(uid), "req-1")
    assert r["ok"] is False
    assert balance(conn, uid) == 100


# --- ownership / input ------------------------------------------------------------

def test_cannot_upscale_another_users_image(conn, lumen, make_user, make_image):
    owner, other = make_user(), make_user()
    img = make_image(owner)
    r = attempt(conn, lumen, other, img, "req-1")
    assert r["ok"] is False
    assert balance(conn, other) == 100
    assert lumen.calls_to("upscale") == 0
    assert image_count(conn, other) == 0


def test_missing_image_is_refused_without_charge(conn, lumen, make_user):
    uid = make_user()
    r = attempt(conn, lumen, uid, 9999, "req-1")
    assert r["ok"] is False
    assert balance(conn, uid) == 100


def test_insufficient_credits_does_not_call_provider(conn, lumen, make_user, make_image):
    uid = make_user(balance=3)
    r = attempt(conn, lumen, uid, make_image(uid), "req-1")
    assert r["ok"] is False
    assert balance(conn, uid) == 3
    assert lumen.calls_to("upscale") == 0


# --- user-facing strings ------------------------------------------------------

def test_error_messages_are_localized(conn, lumen, make_user, make_image):
    poor = make_user(balance=3)
    r1 = upscale(conn, lumen, poor, make_image(poor), "req-1", locale="ru")
    uid = make_user()
    lumen.fail_with = LumenAPIError(500, "internal", "boom")
    r2 = upscale(conn, lumen, uid, make_image(uid), "req-2", locale="ru")
    assert CYRILLIC.search(r1["message"])
    assert CYRILLIC.search(r2["message"])


def test_locale_files_in_sync():
    assert locale_keys_in_sync()


# --- canonical paths ----------------------------------------------------------------

def test_no_direct_balance_writes():
    assert direct_balance_writes() == []
