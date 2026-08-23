"""Rate limiter behavior tests (pure timing logic, no network)."""

from __future__ import annotations

import pytest

import reddit.rate_limit as rate_limit_module
from reddit.rate_limit import RateLimitExceeded, RateLimiter, backoff_delays


def test_backoff_schedule_is_exponential_and_capped() -> None:
    delays = backoff_delays(base_seconds=2.0, attempts=8)
    assert delays[0] == 2.0
    assert delays[1] == 4.0
    assert delays[2] == 8.0
    assert all(d <= 60.0 for d in delays)


def test_call_returns_operation_result() -> None:
    limiter = RateLimiter(min_interval_seconds=0.0)
    assert limiter.call(lambda: 42) == 42


def test_retries_then_succeeds(monkeypatch) -> None:
    monkeypatch.setattr(rate_limit_module.time, "sleep", lambda *_: None)
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("transient")
        return "ok"

    limiter = RateLimiter(min_interval_seconds=0.0, max_retries=5, backoff_base_seconds=0.01)
    assert limiter.call(flaky) == "ok"
    assert calls["n"] == 3


def test_raises_rate_limit_exceeded_after_exhaustion(monkeypatch) -> None:
    monkeypatch.setattr(rate_limit_module.time, "sleep", lambda *_: None)

    def always_fails():
        raise ConnectionError("down")

    limiter = RateLimiter(min_interval_seconds=0.0, max_retries=2, backoff_base_seconds=0.01)
    with pytest.raises(RateLimitExceeded):
        limiter.call(always_fails)


def test_negative_interval_rejected() -> None:
    with pytest.raises(ValueError):
        RateLimiter(min_interval_seconds=-1)
