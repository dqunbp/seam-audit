from lumen_sdk import ImageResult, OutputImage, VideoJob


class FakeLumenClient:
    """In-memory stand-in for lumen_sdk.LumenClient.

    Set `fail_with` to an exception to make the next call raise it, or
    `filter_next = True` to make the next generation come back filtered.
    """

    def __init__(self):
        self.calls: list[tuple] = []
        self.fail_with: Exception | None = None
        self.filter_next = False
        self._seq = 0

    def _next_id(self, prefix: str) -> str:
        self._seq += 1
        return f"{prefix}_{self._seq}"

    def _maybe_fail(self):
        if self.fail_with is not None:
            exc, self.fail_with = self.fail_with, None
            raise exc

    def generate_image(self, prompt: str, size: str = "1024x1024") -> ImageResult:
        self.calls.append(("generate_image", prompt))
        self._maybe_fail()
        result_id = self._next_id("img")
        if self.filter_next:
            self.filter_next = False
            return ImageResult(id=result_id, status="filtered", images=[], filter_reason="policy")
        width, height = (int(x) for x in size.split("x"))
        return ImageResult(
            id=result_id,
            status="succeeded",
            images=[OutputImage(url=f"https://cdn.lumen.test/{result_id}.png", width=width, height=height)],
        )

    def create_video(self, prompt: str, callback_url: str, duration_s: int = 5) -> VideoJob:
        self.calls.append(("create_video", prompt))
        self._maybe_fail()
        return VideoJob(id=self._next_id("vid"), status="queued")
