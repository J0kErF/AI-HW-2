"""Tests for the DebateOrchestrator using fake handles + the real Watchdog."""

from debate_arena.constants import Stance
from debate_arena.services.moderator import Verdict
from debate_arena.services.orchestrator import DebateOrchestrator
from debate_arena.services.watchdog import Watchdog


class FakeHandle:
    """Stand-in debater transport: canned turns, optional timeouts."""

    def __init__(self, stance: str, fail_times: int = 0) -> None:
        self.stance = stance
        self._fail = fail_times
        self._n = 0
        self.alive = True
        self.terminated = 0

    def start_and_return(self) -> "FakeHandle":
        self.alive = True
        return self

    def is_alive(self) -> bool:
        return self.alive

    def terminate(self) -> None:
        self.terminated += 1
        self.alive = False

    def request(self, message: dict) -> dict:
        if self._fail > 0:
            self._fail -= 1
            raise TimeoutError(f"{self.stance} hung")
        self._n += 1
        return {
            "turn_id": f"{self.stance}-{self._n}", "stance": self.stance,
            "type": "argument", "claim": "c", "sources": [{"url": "u"}],
            "responding_to": message.get("turn_id"),
        }


class FakeFather:
    """Stand-in moderator/judge."""

    def __init__(self, capitulate: bool = False) -> None:
        self._cap = capitulate
        self.validated = 0

    def validate(self, turn: dict) -> list:
        self.validated += 1
        return []

    def detect_capitulation(self, turn: dict, stance: Stance) -> bool:
        return self._cap

    def intervene(self, stance: Stance, reason: str) -> dict:
        return {"type": "intervention", "stance": stance.value, "reason": reason}

    def judge(self, transcript: list) -> Verdict:
        return Verdict(Stance.PRO, {"pro": 80, "con": 70}, "j")


def _orch(father, pings=2, handles=None):
    handles = handles or {"pro": FakeHandle("pro"), "con": FakeHandle("con")}
    return DebateOrchestrator(father, Watchdog(1, 3, 2), pings, lambda s: handles[s]), handles


def test_run_produces_full_transcript_and_verdict() -> None:
    orch, _ = _orch(FakeFather(), pings=2)
    result = orch.run("Nuclear energy")
    assert len(result.transcript) == 4  # 2 pro + 2 con
    assert result.verdict.winner is Stance.PRO


def test_timeout_triggers_watchdog_restart() -> None:
    handles = {"pro": FakeHandle("pro", fail_times=1), "con": FakeHandle("con")}
    orch, _ = _orch(FakeFather(), pings=1, handles=handles)
    result = orch.run("Topic")
    assert "pro" in result.restarts
    assert handles["pro"].terminated >= 1
    assert len(result.transcript) == 2  # still completes


def test_capitulation_records_intervention() -> None:
    orch, _ = _orch(FakeFather(capitulate=True), pings=1)
    result = orch.run("Topic")
    assert len(result.interventions) == 2  # one per turn flagged


def test_handles_terminated_on_shutdown() -> None:
    orch, handles = _orch(FakeFather(), pings=1)
    orch.run("Topic")
    assert handles["pro"].terminated >= 1
    assert handles["con"].terminated >= 1
