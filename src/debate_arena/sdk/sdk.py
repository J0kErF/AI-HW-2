"""DebateSDK — the only public surface for all consumers (Guide §4.1).

CLI menu, tests, and any future GUI/REST consumer call this facade; none contain
orchestration logic. The SDK builds the object graph from configuration (gatekeeper,
FIFO logging, Father, watchdog, orchestrator) and runs a debate. `run_debate`
exposes `father`/`make_handle` injection points so the flow is testable offline.
"""

from pathlib import Path
from typing import Any

from debate_arena.services.moderator import ModeratorAgent
from debate_arena.services.orchestrator import DebateOrchestrator, DebateResult
from debate_arena.services.reporting import CostEstimate, aggregate_tokens
from debate_arena.services.watchdog import Watchdog
from debate_arena.shared.config import ConfigManager
from debate_arena.shared.env import load_env
from debate_arena.shared.gatekeeper import ApiGatekeeper
from debate_arena.shared.logging_setup import build_logger


class DebateSDK:
    """Single entry point for running and inspecting debates."""

    def __init__(self, config_dir: str | Path = "config") -> None:
        load_env()
        self._config_dir = str(config_dir)
        self._config = ConfigManager(config_dir)
        self._logger = build_logger("debate_arena", self._config.load("logging_config"))
        rate = self._config.load("rate_limits")
        self._gatekeeper = ApiGatekeeper(rate, rate["budget"], logger=self._logger)
        self._last_result: DebateResult | None = None

    def run_debate(self, topic: str | None = None, rounds: int | None = None,
                   make_handle: Any = None, father: Any = None,
                   on_event: Any = None) -> DebateResult:
        """Run a full debate; topic/rounds default to config values."""
        topic = topic or self._config.get("setup", "debate", "default_topic")
        rounds = rounds or self._config.get("setup", "debate", "pings_per_side")
        father = father or self._build_father(rounds)
        make_handle = make_handle or self._default_make_handle()
        orchestrator = DebateOrchestrator(
            father, self._build_watchdog(), rounds, make_handle, on_event
        )
        self._last_result = orchestrator.run(topic)
        self._logger.info("debate complete: winner=%s", self._last_result.verdict.winner.value)
        return self._last_result

    def _build_watchdog(self) -> Watchdog:
        wd = self._config.get("setup", "watchdog")
        return Watchdog(wd["heartbeat_interval_seconds"], wd["max_missed_heartbeats"],
                        wd["max_restarts"])

    def _build_father(self, rounds: int) -> ModeratorAgent:  # pragma: no cover (live LLM)
        from debate_arena.services.llm_client import GeminiClient
        from debate_arena.shared.env import gemini_api_key

        llm = GeminiClient(self._gatekeeper, gemini_api_key())
        model = self._config.get("setup", "models", "moderator")
        return ModeratorAgent("father", model, llm, rounds, {})

    def _default_make_handle(self) -> Any:  # pragma: no cover (spawns processes)
        from debate_arena.services.process_handle import make_process_handle

        timeout = self._config.get("setup", "timeouts", "agent_call_seconds")
        return lambda stance: make_process_handle(self._config_dir, stance, timeout)

    def get_transcript(self) -> list[dict[str, Any]]:
        """Return the transcript of the most recent debate."""
        return self._last_result.transcript if self._last_result else []

    def get_cost_report(self) -> CostEstimate:
        """Aggregate cost: debater tokens (from the transcript, across processes) plus
        the Father's own gatekeeper usage in the main process."""
        gk = self._gatekeeper.get_cost_report()
        transcript = self._last_result.transcript if self._last_result else []
        deb_in, deb_out = aggregate_tokens(transcript)
        pin, pout = self._debater_price()
        deb_cost = deb_in / 1_000_000 * pin + deb_out / 1_000_000 * pout
        return CostEstimate(gk.input_tokens + deb_in, gk.output_tokens + deb_out,
                            round(gk.cost_usd + deb_cost, 6))

    def _debater_price(self) -> tuple[float, float]:
        model = self._config.get("setup", "models", "debater")
        price = self._config.get("rate_limits", "budget", "price_per_million", model) or {}
        return price.get("input", 0.0), price.get("output", 0.0)
