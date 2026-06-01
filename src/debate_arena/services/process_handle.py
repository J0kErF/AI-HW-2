"""Real process transport for debaters — multiprocessing + IPC (Guide §15).

Each debater runs in its own OS process (Ex §8.2: "agent = process"), receiving
opponent turns on a request queue and returning its turn on a response queue.
This module is integration glue (spawns processes, builds live clients) and is
exercised by the live run / smoke test rather than unit tests.
"""

import multiprocessing as mp
import queue
from typing import Any

from debate_arena.constants import Stance
from debate_arena.services.debater import DebaterAgent
from debate_arena.services.llm_client import GeminiClient
from debate_arena.services.search_providers import build_provider
from debate_arena.services.web_search import WebSearchTool
from debate_arena.shared.config import ConfigManager
from debate_arena.shared.env import gemini_api_key, load_env
from debate_arena.shared.gatekeeper import ApiGatekeeper


def build_debater(stance: str, config_dir: str) -> DebaterAgent:  # pragma: no cover
    """Construct a fully wired DebaterAgent inside the worker process."""
    load_env()
    cfg = ConfigManager(config_dir)
    rate = cfg.load("rate_limits")
    gatekeeper = ApiGatekeeper(rate, rate["budget"])
    llm = GeminiClient(gatekeeper, gemini_api_key())
    search = WebSearchTool(gatekeeper, build_provider(cfg),
                           cfg.get("setup", "search", "results_per_query"))
    model = cfg.get("setup", "models", "debater")
    persona = cfg.get("setup", "debate", "personas", stance)
    return DebaterAgent(f"{stance}-agent", Stance(stance), persona, model, llm, search)


def debater_worker(stance: str, config_dir: str, req: Any, resp: Any) -> None:  # pragma: no cover
    """Worker loop: pull a request, act, push the turn; None is the poison pill."""
    agent = build_debater(stance, config_dir)
    while True:
        message = req.get()
        if message is None:
            break
        try:
            resp.put(agent.act(message))
        except Exception as exc:  # any failure becomes a system turn, never a hang
            resp.put({"type": "system", "stance": stance, "error": str(exc),
                      "claim": "", "sources": [], "responding_to": message.get("turn_id")})


class ProcessDebaterHandle:  # pragma: no cover
    """Process-backed debater transport (request/response over mp queues)."""

    def __init__(self, config_dir: str, stance: str, timeout: float) -> None:
        self._config_dir = config_dir
        self._stance = stance
        self._timeout = timeout
        self._proc: Any = None
        self._req: Any = None
        self._resp: Any = None

    def start_and_return(self) -> "ProcessDebaterHandle":
        ctx = mp.get_context("spawn")
        self._req, self._resp = ctx.Queue(), ctx.Queue()
        self._proc = ctx.Process(
            target=debater_worker,
            args=(self._stance, self._config_dir, self._req, self._resp), daemon=True,
        )
        self._proc.start()
        return self

    def is_alive(self) -> bool:
        return bool(self._proc and self._proc.is_alive())

    def terminate(self) -> None:
        if self._proc and self._proc.is_alive():
            self._proc.terminate()

    def request(self, message: dict) -> dict:
        self._req.put(message)
        try:
            return self._resp.get(timeout=self._timeout)
        except queue.Empty as exc:
            raise TimeoutError(f"{self._stance} timed out") from exc


def make_process_handle(config_dir: str, stance: str, timeout: float) -> ProcessDebaterHandle:  # pragma: no cover
    """Factory for a process-backed debater handle."""
    return ProcessDebaterHandle(config_dir, stance, timeout)
