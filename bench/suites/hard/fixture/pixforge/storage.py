"""Media storage: our own bucket for every file we show to users."""
import hashlib
from urllib.parse import urlparse

PUBLIC_BASE_URL = "https://media.pixforge.test"


class StorageError(Exception):
    pass


class MemoryBackend:
    """Dev/test backend. Production uses the S3 backend from the deploy config."""

    def __init__(self):
        self.objects: dict[str, str] = {}

    def copy_from_url(self, url: str, key: str) -> None:
        self.objects[key] = url

    def exists(self, key: str) -> bool:
        return key in self.objects


backend = MemoryBackend()


def configure(new_backend) -> None:
    global backend
    backend = new_backend


def import_remote(url: str, prefix: str = "media") -> str:
    """Copy a remote HTTPS file into our bucket. Returns its storage key."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise StorageError(f"refusing to import non-https url {url!r}")
    name = parsed.path.rsplit("/", 1)[-1]
    ext = name.rsplit(".", 1)[-1] if "." in name else "bin"
    key = f"{prefix}/{hashlib.sha256(url.encode()).hexdigest()[:20]}.{ext}"
    backend.copy_from_url(url, key)
    return key


def public_url(key: str, ttl_s: int = 3600) -> str:
    """A signed HTTPS URL for a stored file, valid for `ttl_s` seconds."""
    signature = hashlib.sha256(f"{key}:{ttl_s}".encode()).hexdigest()[:16]
    return f"{PUBLIC_BASE_URL}/{key}?ttl={ttl_s}&sig={signature}"
