import json

from pixforge import clock
from pixforge.billing import get_balance
from pixforge.webhooks.payments import handle_payhub_webhook
from pixforge.webhooks.signing import sign

SECRET = "whsec_payhub"


def _deliver(conn, event: dict, secret: str = SECRET):
    body = json.dumps(event).encode()
    headers = {"Payhub-Signature": sign(secret, body, int(clock.now().timestamp()))}
    return handle_payhub_webhook(conn, body, headers, SECRET)


def _checkout(user_id, event_id="evt_1"):
    return {
        "id": event_id,
        "type": "checkout.completed",
        "data": {"user_id": user_id, "credits": 50, "checkout_id": "co_1"},
    }


def test_topup(conn, user_id):
    status, _ = _deliver(conn, _checkout(user_id))
    assert status == 200
    assert get_balance(conn, user_id) == 150


def test_duplicate_delivery_is_applied_once(conn, user_id):
    _deliver(conn, _checkout(user_id))
    status, body = _deliver(conn, _checkout(user_id))
    assert status == 200
    assert body == {"duplicate": True}
    assert get_balance(conn, user_id) == 150


def test_bad_signature_is_rejected(conn, user_id):
    status, _ = _deliver(conn, _checkout(user_id), secret="wrong")
    assert status == 400
    assert get_balance(conn, user_id) == 100
