"""Sliding-window rate limiter (single concern; used by the gatekeeper).

Tracks call timestamps and reports how long until a new call would fit within
both the per-minute and per-hour windows. The clock is injectable for testing.
"""

import time
from collections import deque
from collections.abc import Callable

_MINUTE = 60.0
_HOUR = 3600.0


class SlidingWindowLimiter:
    """Per-service sliding-window limiter.

    Input:  requests_per_minute, requests_per_hour, and a clock function.
    Output: `time_until_free()` -> seconds to wait (0 if a slot is free now).
    Setup:  call timestamps are recorded via `record()`.
    """

    def __init__(self, requests_per_minute: int, requests_per_hour: int,
                 clock: Callable[[], float] = time.time) -> None:
        self._rpm = requests_per_minute
        self._rph = requests_per_hour
        self._clock = clock
        self._calls: deque[float] = deque()

    def _prune(self, now: float) -> None:
        while self._calls and now - self._calls[0] >= _HOUR:
            self._calls.popleft()

    def time_until_free(self) -> float:
        """Seconds until a new call fits both windows (0 if free now)."""
        now = self._clock()
        self._prune(now)
        wait = 0.0
        minute_calls = [t for t in self._calls if now - t < _MINUTE]
        if len(minute_calls) >= self._rpm:
            wait = max(wait, _MINUTE - (now - minute_calls[0]))
        if len(self._calls) >= self._rph:
            wait = max(wait, _HOUR - (now - self._calls[0]))
        return wait

    def record(self) -> None:
        """Record that a call was made at the current time."""
        self._calls.append(self._clock())
