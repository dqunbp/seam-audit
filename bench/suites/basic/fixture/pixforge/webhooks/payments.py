"""Payhub webhook: credit top-ups."""
import json
import logging

from ..billing import grant_credits
from ..db import transaction
from .dedup import mark_processed
from .signing import verify_signature

log = logging.getLogger(__name__)


def handle_payhub_webhook(conn, raw_body: bytes, headers: dict, secret: str) -> tuple[int, dict]:
    """Returns (HTTP status, JSON body). Payhub retries any non-2xx delivery."""
    if not verify_signature(secret, raw_body, headers.get("Payhub-Signature")):
        return 400, {"error": "invalid signature"}

    event = json.loads(raw_body)
    if event["type"] != "checkout.completed":
        return 200, {"ignored": event["type"]}

    data = event["data"]
    with transaction(conn):
        if not mark_processed(conn, "payhub", event["id"]):
            return 200, {"duplicate": True}
        grant_credits(conn, data["user_id"], data["credits"], "topup", f"topup:{data['checkout_id']}")
    log.info("topped up user %s with %s credits", data["user_id"], data["credits"])
    return 200, {"ok": True}
