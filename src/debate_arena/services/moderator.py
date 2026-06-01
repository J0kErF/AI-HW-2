"""Moderator ("Father") — orchestrates turns and judges (Ex §8.1, §9).

The Father is the only hub: it routes every message, validates the JSON contract,
enforces citation + `responding_to` + non-capitulation, intervenes when a debater
is swept, and finally judges on persuasion only — blind to the topic, never a tie.
See docs/PRD_judge_scoring.md.

NOTE: scaffold stub — judging/LLM wiring lands in Phase 2.
"""

from dataclasses import dataclass
from typing import Any

from debate_arena.constants import Stance
from debate_arena.services.base_agent import BaseAgent


@dataclass
class Verdict:
    """Final, decisive judgment (no ties allowed)."""

    winner: Stance
    scores: dict[str, int]
    justification: str


class ModeratorAgent(BaseAgent):
    """The Father: router, rule-enforcer, and blind persuasion judge.

    Input:  child messages (one at a time) and the running transcript.
    Output: routed turns, interventions, and a final Verdict.
    Setup:  number of pings/side, model, gatekeeper, and the scoring rubric.
    """

    def __init__(self, name: str, model: str, gatekeeper: Any, rounds: int,
                 rubric: dict[str, Any]) -> None:
        super().__init__(name=name, model=model, gatekeeper=gatekeeper)
        self.rounds = rounds
        self._rubric = rubric

    def act(self, message: dict[str, Any]) -> dict[str, Any]:
        """Validate + route a child message to the opponent as context."""
        raise NotImplementedError("Phase 2: validate schema, citation, responding_to")

    def _build_prompt(self, message: dict[str, Any]) -> str:
        """Build the judge prompt (rules + transcript only; topic-blind)."""
        raise NotImplementedError("Phase 2")

    def intervene(self, stance: Stance, reason: str) -> dict[str, Any]:
        """Issue an intervention re-asserting a debater's role (Ex §9)."""
        return {"type": "intervention", "stance": stance.value, "reason": reason}

    def detect_capitulation(self, turn: dict[str, Any], stance: Stance) -> bool:
        """Return True if a turn concedes the opponent's position."""
        raise NotImplementedError("Phase 2")

    def judge(self, transcript: list[dict[str, Any]]) -> Verdict:
        """Score persuasion only and return a single winner (never a tie)."""
        raise NotImplementedError("Phase 2: blind scoring + tie-break guarantee")
