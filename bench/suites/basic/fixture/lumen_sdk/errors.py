class LumenError(Exception):
    """Base class for all errors raised by the SDK."""


class LumenAPIError(LumenError):
    """The API returned a 4xx/5xx response (other than 429)."""

    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(f"{status_code} {code}: {message}")
        self.status_code = status_code
        self.code = code
        self.message = message


class LumenRateLimited(LumenError):
    """HTTP 429. Retry after `retry_after` seconds."""

    def __init__(self, retry_after: float):
        super().__init__(f"rate limited, retry after {retry_after}s")
        self.retry_after = retry_after


class LumenTimeout(LumenError):
    """The request did not complete in time. The operation may or may not have run."""
