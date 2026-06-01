"""Watchdog — keep-alive supervision with kill & restart (Ex §8.6).

Monitors debater processes via heartbeats and per-call timeouts. On a hung or
dead process it terminates and respawns it (bounded by max_restarts), so the
debate recovers rather than silently skipping. See docs/PRD_watchdog.md.

NOTE: scaffold stub — multiprocessing supervision lands in Phase 1.
"""

from collections.abc import Callable
from typing import Any


class Watchdog:
    """Process supervisor.

    Input:  process handles + heartbeat/timeout/restart limits (from config).
    Output: restart events and on_dead callbacks.
    Setup:  heartbeat_interval, max_missed_heartbeats, max_restarts.
    """

    def __init__(self, heartbeat_interval: float, max_missed: int, max_restarts: int) -> None:
        self._interval = heartbeat_interval
        self._max_missed = max_missed
        self._max_restarts = max_restarts
        self._restarts: dict[str, int] = {}

    def supervise(self, proc: Any, name: str, on_dead: Callable[[str], None]) -> None:
        """Register a process for monitoring."""
        raise NotImplementedError("Phase 1: track proc + heartbeat state")

    def heartbeat(self, name: str) -> None:
        """Record a liveness heartbeat for a supervised process."""
        raise NotImplementedError("Phase 1")

    def check(self) -> list[str]:
        """Return names of processes judged hung or dead since last check."""
        raise NotImplementedError("Phase 1")

    def restart(self, name: str) -> Any:
        """Kill and respawn a process; raise once max_restarts is exceeded."""
        raise NotImplementedError("Phase 1: terminate + respawn, bound by max_restarts")
