"""Debater agent (Pro/Con) — argues one side, never capitulates.

Each debater cites real sources, sets `responding_to`, and emits strict JSON.
See docs/PRD_debate_orchestration.md for the message schema.

NOTE: scaffold stub — LLM/persona wiring lands in Phase 2.
"""

from typing import Any

from debate_arena.constants import Stance
from debate_arena.services.base_agent import BaseAgent
from debate_arena.services.web_search import WebSearchTool


class DebaterAgent(BaseAgent):
    """A single-stance debater.

    Input:  the opponent's latest message (or the opening prompt).
    Output: an `argument`/`rebuttal` message citing >=1 real source.
    Setup:  stance, persona text, model, gatekeeper, and a web-search tool.
    """

    def __init__(self, name: str, stance: Stance, persona: str, model: str,
                 gatekeeper: Any, search: WebSearchTool) -> None:
        super().__init__(name=name, model=model, gatekeeper=gatekeeper)
        self.stance = stance
        self.persona = persona
        self._search = search

    def act(self, message: dict[str, Any]) -> dict[str, Any]:
        """Compose the next stance-consistent, source-cited debate turn."""
        raise NotImplementedError("Phase 2: search evidence, prompt LLM, return schema JSON")

    def _build_prompt(self, message: dict[str, Any]) -> str:
        """Build the debater prompt enforcing stance + non-capitulation."""
        raise NotImplementedError("Phase 2")

    def _search_evidence(self, claim: str) -> list[Any]:
        """Gather supporting sources for a claim via the web-search tool."""
        return self._search.search(claim)
