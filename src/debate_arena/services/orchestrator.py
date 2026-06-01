"""Debate orchestrator — multiprocessing + IPC (Ex §8.2/§8.6, Guide §15).

Spawns Pro and Con as separate processes, communicates via multiprocessing
queues (child -> father -> child), drives >=10 pings/side, supervises with the
Watchdog, and finishes with the Father's verdict.
See docs/PRD_debate_orchestration.md.

NOTE: scaffold stub — process loop lands in Phase 3.
"""

from dataclasses import dataclass, field
from typing import Any

from debate_arena.services.moderator import ModeratorAgent, Verdict
from debate_arena.services.watchdog import Watchdog


@dataclass
class DebateResult:
    """Everything produced by a full debate run."""

    transcript: list[dict[str, Any]] = field(default_factory=list)
    verdict: Verdict | None = None
    interventions: list[dict[str, Any]] = field(default_factory=list)
    restarts: list[str] = field(default_factory=list)


class DebateOrchestrator:
    """Owns the debate lifecycle across three processes.

    Input:  a topic and configuration.
    Output: a DebateResult (transcript + verdict + resilience events).
    Setup:  Father, Watchdog, pings/side, and process/IPC parameters.
    """

    def __init__(self, father: ModeratorAgent, watchdog: Watchdog, pings_per_side: int,
                 config: dict[str, Any]) -> None:
        self._father = father
        self._watchdog = watchdog
        self._pings = pings_per_side
        self._config = config

    def run(self, topic: str) -> DebateResult:
        """Run the full debate and return its result."""
        raise NotImplementedError(
            "Phase 3: spawn Pro/Con processes, pump IPC queues, supervise, judge"
        )
