import json
import urllib.error
import urllib.request

from .errors import LumenAPIError, LumenRateLimited, LumenTimeout
from .types import ImageResult, OutputImage, UpscaleResult, VideoJob

DEFAULT_BASE_URL = "https://api.lumen.ai"


class LumenClient:
    """Thin synchronous client for the Lumen v2 API. Reference: docs/lumen_api.md."""

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout_s: float = 60.0):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s

    def generate_image(self, prompt: str, size: str = "1024x1024") -> ImageResult:
        data = self._post("/v2/images", {"prompt": prompt, "size": size})
        return ImageResult(
            id=data["id"],
            status=data["status"],
            images=[OutputImage(**img) for img in data.get("images", [])],
            filter_reason=data.get("filter_reason"),
        )

    def upscale(self, image_url: str, factor: int = 2) -> UpscaleResult:
        data = self._post("/v2/upscale", {"image_url": image_url, "factor": factor})
        image = data.get("image")
        return UpscaleResult(
            id=data["id"],
            status=data["status"],
            image=OutputImage(**image) if image else None,
            reason=data.get("reason"),
        )

    def create_video(self, prompt: str, callback_url: str, duration_s: int = 5) -> VideoJob:
        data = self._post(
            "/v2/videos", {"prompt": prompt, "callback_url": callback_url, "duration_s": duration_s}
        )
        return VideoJob(id=data["id"], status=data["status"])

    def _post(self, path: str, payload: dict) -> dict:
        request = urllib.request.Request(
            self._base_url + path,
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_s) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                raise LumenRateLimited(float(exc.headers.get("Retry-After", "1"))) from exc
            body = json.loads(exc.read() or b"{}").get("error", {})
            raise LumenAPIError(exc.code, body.get("code", "unknown"), body.get("message", "")) from exc
        except TimeoutError as exc:
            raise LumenTimeout(str(exc)) from exc
