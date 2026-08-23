"""Conservative request pacing and retry-with-backoff for Reddit calls.

PRAW already throttles internally, but this module adds an explicit
minimum interval between API calls and exponential backoff on transient
failures (429 / 5xx / network errors). All scraping is sequential by
design — no concurrent request bursts.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import TypeVar

import prawcore

logger = logging.getLogger(__name__)

T = TypeVar("T")

# prawcore exceptions that are worth retrying with backoff.
RETRYABLE_EXCEPTIONS = (
    prawcore.exceptions.ResponseException,
    prawcore.exceptions.RequestException,
    ConnectionError,
    TimeoutError,
)


class RateLimitExceeded(Exception):
    """Raised when retries are exhausted (e.g. persistent 429 responses)."""


def backoff_delays(base_seconds: float, attempts: int) -> list[float]:
    """Exponential schedule: base * 2**i, capped at 60s per wait."""
    return [min(60.0, base_seconds * (2**i)) for i in range(attempts)]


class RateLimiter:
    """Enforces a minimum interval between successive Reddit API calls."""

    def __init__(
        self,
        min_interval_seconds: float = 1.1,
        max_retries: int = 5,
        backoff_base_seconds: float = 2.0,
    ) -> None:
        if min_interval_seconds < 0:
            raise ValueError("min_interval_seconds must be >= 0")
        self.min_interval = float(min_interval_seconds)
        self.max_retries = int(max_retries)
        self.backoff_base = float(backoff_base_seconds)
        self._last_call: float | None = None

    def _pace(self) -> None:
        if self._last_call is not None:
            elapsed = time.monotonic() - self._last_call
            remaining = self.min_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self._last_call = time.monotonic()

    def call(self, operation: Callable[[], T], *, description: str = "reddit call") -> T:
        """Run one paced Reddit API operation with exponential-backoff retries.

        Raises RateLimitExceeded when all attempts fail.
        """
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                self._pace()
                return operation()
            except RETRYABLE_EXCEPTIONS as error:  # noqa: PERF203 - retry loop
                last_error = error
                status = getattr(error, "response", None)
                delay = backoff_delays(self.backoff_base, attempt + 1)[-1]
                logger.warning(
                    "retryable_reddit_error",
                    extra={
                        "description": description,
                        "attempt": attempt + 1,
                        "max_retries": self.max_retries,
                        "delay_seconds": delay,
                        "error_type": type(error).__name__,
                        "http_status": getattr(status, "status_code", None),
                    },
                )
                time.sleep(delay)

        raise RateLimitExceeded(
            f"{description} failed after {self.max_retries} attempts"
        ) from last_error
