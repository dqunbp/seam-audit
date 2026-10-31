from lumen_sdk import LumenAPIError, LumenRateLimited

from pixforge.billing import get_balance
from pixforge.features.generate import generate_image
from pixforge.images import list_images


def test_generates_and_charges(conn, lumen, user_id):
    response = generate_image(conn, lumen, user_id, "a cat", "req-1")
    assert response["ok"]
    assert response["url"].startswith("https://media.pixforge.test/")
    assert get_balance(conn, user_id) == 98
    assert len(list_images(conn, user_id)) == 1


def test_pro_pays_half(conn, lumen, pro_user_id):
    generate_image(conn, lumen, pro_user_id, "a cat", "req-1")
    assert get_balance(conn, pro_user_id) == 99


def test_retry_with_same_request_id_is_not_charged_twice(conn, lumen, user_id):
    first = generate_image(conn, lumen, user_id, "a cat", "req-1")
    second = generate_image(conn, lumen, user_id, "a cat", "req-1")
    assert second == first
    assert get_balance(conn, user_id) == 98
    assert len(lumen.calls) == 1


def test_filtered_result_is_refunded(conn, lumen, user_id):
    lumen.filter_next = True
    response = generate_image(conn, lumen, user_id, "a cat", "req-1")
    assert not response["ok"]
    assert response["error_code"] == "content_filtered"
    assert get_balance(conn, user_id) == 100
    assert list_images(conn, user_id) == []


def test_provider_error_is_refunded(conn, lumen, user_id):
    lumen.fail_with = LumenAPIError(500, "internal", "boom")
    response = generate_image(conn, lumen, user_id, "a cat", "req-1")
    assert response["error_code"] == "provider_failed"
    assert get_balance(conn, user_id) == 100


def test_rate_limited_is_refunded(conn, lumen, user_id):
    lumen.fail_with = LumenRateLimited(5)
    response = generate_image(conn, lumen, user_id, "a cat", "req-1")
    assert response["error_code"] == "rate_limited"
    assert get_balance(conn, user_id) == 100


def test_insufficient_credits_does_not_call_provider(conn, lumen):
    from pixforge.users import create_user

    poor = create_user(conn, "poor@example.com", balance=1)
    response = generate_image(conn, lumen, poor, "a cat", "req-1", locale="ru")
    assert response["error_code"] == "insufficient_credits"
    assert "2" in response["message"]
    assert lumen.calls == []
