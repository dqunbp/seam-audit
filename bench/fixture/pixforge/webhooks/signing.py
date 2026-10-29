"""HMAC signatures of inbound webhooks.

Both Payhub and Lumen sign deliveries the same way: a header of the form
`t=<unix seconds>,v1=<hex HMAC-SHA256 of "<t>.<raw body>" with the endpoint secret>`.
"""
import hashlib
import hmac

from .. import clock

DEFAULT_TOLERANCE_S = 300


def sign(secret: str, body: bytes, timestamp: int) -> str:
    mac = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256)
    return f"t={timestamp},v1={mac.hexdigest()}"


def verify_signature(secret: str, body: bytes, header: str | None, tolerance_s: int = DEFAULT_TOLERANCE_S) -> bool:
    """True if `header` is a valid, fresh signature of `body`. Never raises."""
    if not header:
        return False
    try:
        parts = dict(item.split("=", 1) for item in header.split(","))
        timestamp = int(parts["t"])
        signature = parts["v1"]
    except (KeyError, ValueError):
        return False
    if abs(clock.now().timestamp() - timestamp) > tolerance_s:
        return False
    expected = sign(secret, body, timestamp).split("v1=", 1)[1]
    return hmac.compare_digest(expected, signature)
