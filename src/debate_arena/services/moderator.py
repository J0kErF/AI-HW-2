"""Moderator ("Father") — orchestrates turns and judges (Ex §8.1, §9).

The Father is the only hub: it validates the JSON contract (citation +
`responding_to`), intervenes when a debater is swept, and finally judges on
persuasion only — blind to the topic, never a tie. See docs/PRD_judge_scoring.md.
"""

from dataclasses import dataclass
from typing import Any

from debate_arena.constants import MessageType, Stance
from debate_arena.services.base_agent import BaseAgent

_ARGUMENTATIVE = {MessageType.ARGUMENT.value, MessageType.REBUTTAL.value}


@dataclass
class Verdict:
    """Final, decisive judgment (no ties allowed)."""

    winner: Stance
    scores: dict[str, int]
    justification: str


class ModeratorAgent(BaseAgent):
    """The Father: router, rule-enforcer, and blind persuasion judge.

    Input:  child messages (one at a time) and the running transcript.
    Output: validation results, interventions, and a final Verdict.
    Setup:  number of pings/side, model, gatekept LLM client, scoring rubric.
    """

    def __init__(self, name: str, model: str, llm: Any, rounds: int,
                 rubric: dict[str, Any]) -> None:
        super().__init__(name=name, model=model, llm=llm)
        self.rounds = rounds
        self._rubric = rubric

    def act(self, message: dict[str, Any]) -> dict[str, Any]:
        """Validate a child message before it is routed onward."""
        issues = self.validate(message)
        return {"type": "moderation", "stance": self.name, "issues": issues, "ok": not issues}

    def validate(self, message: dict[str, Any]) -> list[str]:
        """Return a list of rule violations ([] means the turn is acceptable)."""
        issues: list[str] = []
        if not message.get("claim"):
            issues.append("empty claim")
        if message.get("type") in _ARGUMENTATIVE and not message.get("sources"):
            issues.append("missing sources")
        if message.get("type") == MessageType.REBUTTAL.value and not message.get("responding_to"):
            issues.append("missing responding_to")
        return issues

    def intervene(self, stance: Stance, reason: str) -> dict[str, Any]:
        """Issue an intervention re-asserting a debater's role (Ex §9)."""
        return {"type": MessageType.INTERVENTION.value, "stance": stance.value, "reason": reason}

    def detect_capitulation(self, turn: dict[str, Any], stance: Stance) -> bool:
        """Return True if a turn concedes the opponent's position."""
        prompt = (
            f"Does this {stance.value} turn concede the opponent's position? "
            f'Reply strict JSON {{"capitulated": true|false}}.\nTurn: {turn.get("claim", "")}'
        )
        return bool(self._safe_parse(self._safe_respond(prompt)).get("capitulated", False))

    def _build_prompt(self, message: dict[str, Any]) -> str:
        lines = [f"{m['stance']} ({m['turn_id']}): {m['claim']}" for m in message["transcript"]]
        return (
            "Judge the debate below on PERSUASION ABILITY ONLY. You are NOT told which "
            "side is correct and must not assume one. Score each side 0-100; scores must "
            'differ. Reply strict JSON {"scores": {"pro": int, "con": int}, '
            '"justification": str}.\n' + "\n".join(lines)
        )

    def judge(self, transcript: list[dict[str, Any]]) -> Verdict:
        """Score persuasion only and return a single winner (never a tie)."""
        data = self._safe_parse(self._safe_respond(self._build_prompt({"transcript": transcript}),
                                                   self._judge_system()))
        scores = data.get("scores", {})
        pro, con = self._break_tie(int(scores.get("pro", 0)), int(scores.get("con", 0)), transcript)
        winner = Stance.PRO if pro > con else Stance.CON
        return Verdict(winner=winner, scores={"pro": pro, "con": con},
                       justification=data.get("justification", ""))

    @staticmethod
    def _judge_system() -> str:
        return "You are an impartial debate judge scoring rhetoric, evidence use, and rebuttals."

    def _break_tie(self, pro: int, con: int, transcript: list[dict[str, Any]]) -> tuple[int, int]:
        """Guarantee distinct scores: fewer citations, then later final turn, loses a point."""
        if pro != con:
            return pro, con
        pro_cites = self._count_sources(transcript, "pro")
        con_cites = self._count_sources(transcript, "con")
        if pro_cites != con_cites:
            return (pro - 1, con) if pro_cites < con_cites else (pro, con - 1)
        last = transcript[-1]["stance"] if transcript else "con"
        return (pro - 1, con) if last == "pro" else (pro, con - 1)

    @staticmethod
    def _count_sources(transcript: list[dict[str, Any]], stance: str) -> int:
        return sum(len(m.get("sources", [])) for m in transcript if m.get("stance") == stance)
