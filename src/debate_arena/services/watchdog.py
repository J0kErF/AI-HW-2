"""Watchdog — keep-alive supervision with kill & restart (Ex §8.6).

Monitors agent processes via heartbeats and a timeout derived from
heartbeat_interval × max_missed. A hung or dead process is terminated and
respawned (bounded by max_restarts), so the debate recovers rather than silently
skipping. See docs/PRD_watchdog.md.

The supervised object only needs an `is_alive()` / `terminate()` contract
(satisfied by multiprocessing.Process), and a `spawn()` factory that (re)creates
and starts it — which is what makes a real restart possible.
"""

import time
from collections.abc import Callable
from typing import Any


class WatchdogError(RuntimeError):
    """Raised when a process exceeds its allowed number of restarts."""


class Watchdog:
    """Process supervisor.

    Input:  per process, a `spawn()` factory and optional `on_dead` callback.
    Output: restart events; `check()` lists processes judged hung/dead.
    Setup:  heartbeat_interval, max_missed, max_restarts (from config).
    """

    def __init__(self, heartbeat_interval: float, max_missed: int, max_restarts: int,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self._interval = heartbeat_interval
        self._max_missed = max_missed
        self._max_restarts = max_restarts
        self._clock = clock
        self._procs: dict[str, dict[str, Any]] = {}

    def supervise(self, name: str, spawn: Callable[[], Any],
                  on_dead: Callable[[str], None] | None = None) -> Any:
        """Start and register a process for monitoring; return the process."""
        proc = spawn()
        self._procs[name] = {
            "proc": proc, "spawn": spawn, "on_dead": on_dead,
            "last": self._clock(), "restarts": 0,
        }
        return proc

    def heartbeat(self, name: str) -> None:
        """Record a liveness heartbeat for a supervised process."""
        if name in self._procs:
            self._procs[name]["last"] = self._clock()

    def check(self) -> list[str]:
        """Return names of processes judged hung (timed out) or dead."""
        now = self._clock()
        flagged: list[str] = []
        for name, entry in self._procs.items():
            hung = now - entry["last"] > self._interval * self._max_missed
            dead = not entry["proc"].is_alive()
            if hung or dead:
                flagged.append(name)
                if entry["on_dead"] is not None:
                    entry["on_dead"](name)
        return flagged

    def restart(self, name: str) -> Any:
        """Kill and respawn a process; raise once max_restarts is exceeded."""
        entry = self._procs[name]
        entry["proc"].terminate()
        entry["restarts"] += 1
        if entry["restarts"] > self._max_restarts:
            raise WatchdogError(f"{name} exceeded max_restarts={self._max_restarts}")
        proc = entry["spawn"]()
        entry["proc"] = proc
        entry["last"] = self._clock()
        return proc
