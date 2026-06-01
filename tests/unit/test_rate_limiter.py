"""Tests for the sliding-window rate limiter."""

from debate_arena.shared.rate_limiter import SlidingWindowLimiter


def _clock(state: dict) -> callable:
    return lambda: state["t"]


def test_under_limit_is_free() -> None:
    lim = SlidingWindowLimiter(requests_per_minute=2, requests_per_hour=100)
    assert lim.time_until_free() == 0


def test_minute_limit_forces_wait() -> None:
    state = {"t": 0.0}
    lim = SlidingWindowLimiter(2, 100, clock=_clock(state))
    lim.record()
    lim.record()
    wait = lim.time_until_free()
    assert 0 < wait <= 60


def test_window_frees_after_minute() -> None:
    state = {"t": 0.0}
    lim = SlidingWindowLimiter(2, 100, clock=_clock(state))
    lim.record()
    lim.record()
    state["t"] = 61.0
    assert lim.time_until_free() == 0


def test_hour_limit_forces_wait() -> None:
    state = {"t": 0.0}
    lim = SlidingWindowLimiter(1000, 2, clock=_clock(state))
    lim.record()
    lim.record()
    wait = lim.time_until_free()
    assert 0 < wait <= 3600
