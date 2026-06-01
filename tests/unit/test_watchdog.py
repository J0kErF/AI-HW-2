"""Tests for the Watchdog (keep-alive + kill/restart, with fakes)."""

import pytest

from debate_arena.services.watchdog import Watchdog, WatchdogError


class FakeProc:
    """A stand-in process exposing the is_alive()/terminate() contract."""

    def __init__(self, alive: bool = True) -> None:
        self._alive = alive
        self.terminated = False

    def is_alive(self) -> bool:
        return self._alive

    def terminate(self) -> None:
        self.terminated = True
        self._alive = False


def _clock(state: dict):
    return lambda: state["t"]


def test_supervise_starts_process() -> None:
    spawned: list[FakeProc] = []
    wd = Watchdog(heartbeat_interval=1, max_missed=3, max_restarts=2)
    proc = wd.supervise("pro", lambda: spawned.append(FakeProc()) or spawned[-1])
    assert proc is spawned[0]


def test_healthy_process_not_flagged() -> None:
    state = {"t": 0.0}
    wd = Watchdog(1, 3, 2, clock=_clock(state))
    wd.supervise("pro", FakeProc)
    state["t"] = 2.0
    wd.heartbeat("pro")
    assert wd.check() == []


def test_missed_heartbeats_flagged() -> None:
    state = {"t": 0.0}
    wd = Watchdog(1, 3, 2, clock=_clock(state))
    wd.supervise("pro", FakeProc)
    state["t"] = 10.0
    assert wd.check() == ["pro"]


def test_dead_process_flagged_and_callback_fired() -> None:
    events: list[str] = []
    wd = Watchdog(1, 3, 2)
    wd.supervise("con", lambda: FakeProc(alive=False), on_dead=events.append)
    assert wd.check() == ["con"]
    assert events == ["con"]


def test_restart_kills_old_and_spawns_new() -> None:
    procs: list[FakeProc] = []
    wd = Watchdog(1, 3, 2)
    wd.supervise("pro", lambda: procs.append(FakeProc()) or procs[-1])
    new = wd.restart("pro")
    assert procs[0].terminated is True
    assert new is procs[1]


def test_restart_beyond_max_raises() -> None:
    wd = Watchdog(1, 3, max_restarts=1)
    wd.supervise("pro", FakeProc)
    wd.restart("pro")
    with pytest.raises(WatchdogError):
        wd.restart("pro")
