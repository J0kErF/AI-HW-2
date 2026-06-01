"""DebateSDK — the only public surface for all consumers (Guide §4.1).

CLI menu, automated tests, and any future GUI/REST consumer call this facade;
none of them contain orchestration logic. The SDK wires config, gatekeeper,
logging, agents, watchdog, and orchestrator together.

NOTE: scaffold stub — wiring lands in Phase 3.
"""

from pathlib import Path
from typing import Any

from debate_arena.services.orchestrator import DebateResult
from debate_arena.shared.config import ConfigManager


class DebateSDK:
    """Single entry point for running and inspecting debates.

    Input:  a config directory (defaults to ./config).
    Output: DebateResult, transcript, and cost report.
    Setup:  builds the full object graph from configuration on init.
    """

    def __init__(self, config_dir: str | Path = "config") -> None:
        self._config = ConfigManager(config_dir)
        self._last_result: DebateResult | None = None

    def run_debate(self, topic: str | None = None, rounds: int | None = None) -> DebateResult:
        """Run a full debate; topic/rounds default to config values."""
        raise NotImplementedError("Phase 3: build graph from config, run orchestrator")

    def get_transcript(self) -> list[dict[str, Any]]:
        """Return the transcript of the most recent debate."""
        if self._last_result is None:
            return []
        return self._last_result.transcript

    def get_cost_report(self) -> Any:
        """Return token/cost accounting for the most recent debate."""
        raise NotImplementedError("Phase 3: expose gatekeeper cost report")
