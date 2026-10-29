from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class OutputImage:
    url: str
    width: int
    height: int


@dataclass(frozen=True)
class ImageResult:
    id: str
    status: Literal["succeeded", "filtered"]
    images: list[OutputImage]
    filter_reason: str | None = None


@dataclass(frozen=True)
class UpscaleResult:
    id: str
    status: Literal["succeeded", "rejected", "filtered"]
    # See docs: the meaning of `image` depends on `status`.
    image: OutputImage | None
    reason: str | None = None


@dataclass(frozen=True)
class VideoJob:
    id: str
    status: Literal["queued"]
