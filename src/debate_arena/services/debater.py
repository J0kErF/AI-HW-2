"""Debater agent (Pro/Con) — argues one side, never capitulates.

Searches for evidence, prompts the LLM for a stance-consistent claim, and emits a
strict-JSON debate message that cites real sources and sets `responding_to`.
See docs/PRD_debate_orchestration.md for the schema.
"""

from dataclasses import asdict
from typing import Any

from debate_arena.constants import MessageType, Stance
from debate_arena.services.base_agent import BaseAgent
from debate_arena.services.web_search import WebSearchTool


class DebaterAgent(BaseAgent):
    """A single-stance debater.

    Input:  the opponent's latest message (or the opening prompt with `topic`).
    Output: an `argument`/`rebuttal` message citing >=1 real source.
    Setup:  stance, persona text, model, gatekept LLM client, and a search tool.
    """

    def __init__(self, name: str, stance: Stance, persona: str, model: str,
                 llm: Any, search: WebSearchTool) -> None:
        super().__init__(name=name, model=model, llm=llm)
        self.stance = stance
        self.persona = persona
        self._search = search
        self._counter = 0
        self._pending_sources: list[Any] = []

    def act(self, message: dict[str, Any]) -> dict[str, Any]:
        """Compose the next stance-consistent, source-cited debate turn."""
        self._counter += 1
        opponent_claim = message.get("claim")
        topic = message.get("topic", "")
        is_opening = opponent_claim is None
        sources = self._search.search(opponent_claim or topic)
        self._pending_sources = sources
        raw = self._respond(self._build_prompt(message), self._system_prompt())
        parsed = self._safe_parse(raw)
        return {
            "turn_id": f"{self.stance.value}-{self._counter}",
            "stance": self.stance.value,
            "type": (MessageType.ARGUMENT if is_opening else MessageType.REBUTTAL).value,
            "responding_to": None if is_opening else message.get("turn_id"),
            "reasoning": parsed.get("reasoning", ""),
            "claim": parsed.get("claim") or raw.strip(),
            "sources": [asdict(s) for s in sources],
            "tokens": self.token_totals,
        }

    def _system_prompt(self) -> str:
        return (
            f"You are the {self.stance.value.upper()} debater: {self.persona} "
            f"Argue ONLY the {self.stance.value} side. Never concede the opponent's "
            "position. Reply as strict JSON: {\"reasoning\": str, \"claim\": str}."
        )

    def _build_prompt(self, message: dict[str, Any]) -> str:
        topic = message.get("topic", "")
        opponent = message.get("claim")
        evidence = "\n".join(
            f"- {s.title}: {s.snippet} ({s.url})" for s in self._pending_sources
        )
        if opponent is None:
            return f"Topic: {topic}\nEvidence:\n{evidence}\nOpen with your strongest argument."
        return (
            f"Topic: {topic}\nOpponent argued: {opponent}\nEvidence:\n{evidence}\n"
            "Rebut the opponent directly and advance your side."
        )
