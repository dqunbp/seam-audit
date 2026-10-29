"""Shared fixtures for the hidden grading tests.

Copied into <run>/tests_hidden/ after the agent finishes. Independent of the
agent's own tests/ and fakes, which the agent may have changed.
"""
import hashlib
import hmac
import json
import re
from datetime import datetime, timezone
from itertools import count
from pathlib import Path

import pytest

from lumen_sdk import ImageResult, LumenAPIError, OutputImage, UpscaleResult, VideoJob
from pixforge import clock, db

REPO = Path(__file__).resolve().parents[1]
CYRILLIC = re.compile(r"[а-яА-ЯёЁ]")


@pytest.fixture(autouse=True)
def frozen_clock():
    clock.set_now(datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc))
    yield
    clock.set_now(None)


@pytest.fixture
def conn():
    connection = db.connect()
    db.migrate(connection)
    yield connection
    connection.close()


@pytest.fixture
def make_user(conn):
    seq = count(1)

    def make(plan: str = "free", balance: int = 100, locale: str = "en") -> int:
        from pixforge.users import create_user

        return create_user(conn, f"user{next(seq)}@example.com", plan=plan, balance=balance, locale=locale)

    return make


class HiddenLumen:
    """Fake Lumen client that follows docs/lumen_api.md."""

    def __init__(self):
        self.calls: list[tuple] = []
        self.fail_with: Exception | None = None
        self.image_mode = "succeeded"  # or "filtered"
        self.upscale_mode = "auto"  # or "filtered"
        self.known_images: dict[str, tuple[int, int]] = {}
        self._seq = count(1)

    def calls_to(self, method: str) -> int:
        return sum(1 for call in self.calls if call[0] == method)

    def _maybe_fail(self):
        if self.fail_with is not None:
            exc, self.fail_with = self.fail_with, None
            raise exc

    def generate_image(self, prompt, size="1024x1024"):
        self.calls.append(("generate_image", prompt))
        self._maybe_fail()
        n = next(self._seq)
        if self.image_mode == "filtered":
            return ImageResult(id=f"img_{n}", status="filtered", images=[], filter_reason="policy")
        w, h = (int(x) for x in size.split("x"))
        return ImageResult(
            id=f"img_{n}", status="succeeded",
            images=[OutputImage(url=f"https://cdn.lumen.test/img_{n}.png", width=w, height=h)],
        )

    def upscale(self, image_url, factor=2):
        self.calls.append(("upscale", image_url, factor))
        self._maybe_fail()
        n = next(self._seq)
        if image_url not in self.known_images:
            raise LumenAPIError(422, "invalid_image_url", f"cannot fetch {image_url!r}")
        w, h = self.known_images[image_url]
        if max(w, h) > 2048:
            # Per docs: `rejected` echoes the original input image unchanged.
            return UpscaleResult(
                id=f"ups_{n}", status="rejected",
                image=OutputImage(url=image_url, width=w, height=h), reason="input_too_large",
            )
        if self.upscale_mode == "filtered":
            return UpscaleResult(id=f"ups_{n}", status="filtered", image=None, reason="policy")
        return UpscaleResult(
            id=f"ups_{n}", status="succeeded",
            image=OutputImage(url=f"https://cdn.lumen.test/ups_{n}.png", width=w * factor, height=h * factor),
        )

    def create_video(self, prompt, callback_url, duration_s=5):
        self.calls.append(("create_video", prompt))
        self._maybe_fail()
        return VideoJob(id=f"vid_{next(self._seq)}", status="queued")


@pytest.fixture
def lumen():
    return HiddenLumen()


@pytest.fixture
def make_image(conn, lumen):
    def make(user_id: int, width: int = 1024, height: int = 1024) -> int:
        from pixforge.images import save_image

        url = f"https://cdn.pixforge.test/u{user_id}/{len(lumen.known_images) + 1}.png"
        lumen.known_images[url] = (width, height)
        return save_image(conn, user_id, url, width, height)

    return make


def balance(conn, user_id: int) -> int:
    return conn.execute("SELECT balance FROM users WHERE id = ?", (user_id,)).fetchone()[0]


def charges(conn, user_id: int) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM credit_ledger WHERE user_id = ? AND delta < 0", (user_id,)
    ).fetchone()[0]


def image_count(conn, user_id: int) -> int:
    return conn.execute("SELECT COUNT(*) FROM images WHERE user_id = ?", (user_id,)).fetchone()[0]


def lumen_signature(secret: str, body: bytes, timestamp: int) -> str:
    mac = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={mac}"


def locale_keys_in_sync() -> bool:
    locales_dir = REPO / "pixforge" / "locales"
    catalogs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(locales_dir.glob("*.json"))]
    return len(catalogs) >= 2 and all(set(c) == set(catalogs[0]) for c in catalogs)


_BALANCE_WRITE = re.compile(r"UPDATE\s+users\s+SET[^;\"']*balance", re.IGNORECASE)
_LEDGER_WRITE = re.compile(r"INSERT\s+(OR\s+\w+\s+)?INTO\s+credit_ledger", re.IGNORECASE)


def direct_balance_writes() -> list[str]:
    """Files outside billing.py that write balances or the ledger directly."""
    offenders = []
    for path in (REPO / "pixforge").rglob("*.py"):
        if path.name == "billing.py":
            continue
        text = path.read_text(encoding="utf-8")
        if _BALANCE_WRITE.search(text) or _LEDGER_WRITE.search(text):
            offenders.append(str(path.relative_to(REPO)))
    return offenders
