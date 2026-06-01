"""Debate orchestrator — drives the debate over a process transport.

Works against a `DebaterHandle` abstraction so the orchestration logic is fully
unit-testable with fakes, while production uses real OS processes + IPC queues
(services/process_handle.py). A handle exposes:
    start_and_return() -> self   # (re)start the worker process, return handle
    is_alive() -> bool
    terminate() -> None
    request(message: dict) -> dict   # send + receive a turn; raises TimeoutError
See docs/PRD_debate_orchestration.md.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from debate_arena.constants import Stance

_SIDES = ("pro", "con")


@dataclass
class DebateResult:
    """Everything produced by a full debate run."""

    transcript: list[dict[str, Any]] = field(default_factory=list)
    verdict: Any = None
    interventions: list[dict[str, Any]] = field(default_factory=list)
    restarts: list[str] = field(default_factory=list)


class DebateOrchestrator:
    """Owns the debate lifecycle across the Pro/Con transports.

    Input:  a topic and configuration.
    Output: a DebateResult (transcript + verdict + resilience events).
    Setup:  Father, Watchdog, pings/side, a handle factory, and an event sink.
    """

    def __init__(self, father: Any, watchdog: Any, pings_per_side: int,
                 make_handle: Callable[[str], Any],
                 on_event: Callable[[dict], None] | None = None) -> None:
        self._father = father
        self._wd = watchdog
        self._pings = pings_per_side
        self._make_handle = make_handle
        self._on_event = on_event or (lambda _e: None)

    def run(self, topic: str) -> DebateResult:
        """Run the full debate (>=pings per side) and return its result."""
        result = DebateResult()
        handles = self._start(topic)
        context: dict[str, Any] = {"topic": topic}
        for _ in range(self._pings):
            for stance in _SIDES:
                context = self._play(handles, stance, context, topic, result)
        result.verdict = self._father.judge(result.transcript)
        self._shutdown(handles)
        return result

    def _start(self, topic: str) -> dict[str, Any]:
        handles: dict[str, Any] = {}
        for stance in _SIDES:
            handle = self._make_handle(stance)
            self._wd.supervise(stance, handle.start_and_return)
            handles[stance] = handle
        return handles

    def _play(self, handles: dict[str, Any], stance: str, context: dict[str, Any],
              topic: str, result: DebateResult) -> dict[str, Any]:
        message = {**context, "topic": topic}
        turn = self._request_with_recovery(handles, stance, message, result)
        issues = self._father.validate(turn)
        if issues:
            self._on_event({"type": "validation", "stance": stance, "issues": issues})
        if self._father.detect_capitulation(turn, Stance(stance)):
            intervention = self._father.intervene(Stance(stance), "Re-assert your stance.")
            result.interventions.append(intervention)
            self._on_event(intervention)
        result.transcript.append(turn)
        self._on_event(turn)
        return turn

    def _request_with_recovery(self, handles: dict[str, Any], stance: str,
                               message: dict[str, Any], result: DebateResult) -> dict[str, Any]:
        for _ in range(2):
            try:
                return handles[stance].request(message)
            except TimeoutError:
                result.restarts.append(stance)
                handles[stance] = self._wd.restart(stance)
        return {
            "turn_id": f"{stance}-timeout", "stance": stance, "type": "system",
            "claim": "(no response)", "sources": [], "responding_to": message.get("turn_id"),
        }

    @staticmethod
    def _shutdown(handles: dict[str, Any]) -> None:
        for handle in handles.values():
            handle.terminate()
