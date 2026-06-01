"""Tests for the ModeratorAgent: validation, intervention, blind no-tie judge."""

from debate_arena.constants import Stance
from debate_arena.services.moderator import ModeratorAgent, Verdict


class _FakeLLM:
    def __init__(self, text: str) -> None:
        self.text = text

    def complete(self, model, prompt, system=None) -> tuple:
        return self.text, (2, 2)


class _RaisingLLM:
    def complete(self, model, prompt, system=None) -> tuple:
        raise ConnectionError("provider down")


def _moderator(text: str) -> ModeratorAgent:
    return ModeratorAgent("father", "gemini-2.5-flash", _FakeLLM(text), rounds=10, rubric={})


def _resilient_moderator() -> ModeratorAgent:
    return ModeratorAgent("father", "gemini-2.5-flash", _RaisingLLM(), rounds=10, rubric={})


def _arg(stance: str, turn_id: str, n_sources: int = 1, claim: str = "c", **extra) -> dict:
    msg = {
        "type": "rebuttal" if extra.get("responding_to") else "argument",
        "stance": stance,
        "turn_id": turn_id,
        "claim": claim,
        "sources": [{"title": "t", "url": "u", "snippet": "s"}] * n_sources,
    }
    msg.update(extra)
    return msg


def test_validate_flags_empty_claim_and_missing_sources() -> None:
    mod = _moderator("{}")
    issues = mod.validate({"type": "argument", "claim": "", "sources": []})
    assert "empty claim" in issues
    assert "missing sources" in issues


def test_validate_flags_missing_responding_to_on_rebuttal() -> None:
    mod = _moderator("{}")
    issues = mod.validate({"type": "rebuttal", "claim": "c",
                           "sources": [{"url": "u"}]})
    assert "missing responding_to" in issues


def test_judge_returns_winner_with_distinct_scores() -> None:
    mod = _moderator('{"scores": {"pro": 80, "con": 70}, "justification": "j"}')
    verdict = mod.judge([_arg("pro", "pro-1")])
    assert isinstance(verdict, Verdict)
    assert verdict.winner is Stance.PRO
    assert verdict.scores == {"pro": 80, "con": 70}


def test_judge_breaks_tie_using_citation_count() -> None:
    mod = _moderator('{"scores": {"pro": 75, "con": 75}, "justification": "tie"}')
    transcript = [_arg("pro", "pro-1", n_sources=2), _arg("con", "con-1", n_sources=1)]
    verdict = mod.judge(transcript)
    assert verdict.scores["pro"] != verdict.scores["con"]  # never a tie
    assert verdict.winner is Stance.PRO  # con had fewer citations -> loses the point


def test_judge_tolerates_degraded_system_turns() -> None:
    mod = _moderator('{"scores": {"pro": 60, "con": 55}, "justification": "ok"}')
    transcript = [_arg("pro", "pro-1"), {"type": "system", "stance": "con"}]  # no turn_id/claim
    verdict = mod.judge(transcript)  # must not KeyError
    assert verdict.winner is Stance.PRO


def test_detect_capitulation_parses_boolean() -> None:
    mod = _moderator('{"capitulated": true}')
    assert mod.detect_capitulation({"claim": "You are right"}, Stance.PRO) is True


def test_judge_degrades_gracefully_on_provider_failure() -> None:
    mod = _resilient_moderator()
    transcript = [_arg("pro", "pro-1", n_sources=2), _arg("con", "con-1", n_sources=1)]
    verdict = mod.judge(transcript)  # LLM raises -> citation-based fallback, no crash
    assert verdict.scores["pro"] != verdict.scores["con"]
    assert verdict.winner is Stance.PRO


def test_detect_capitulation_false_on_provider_failure() -> None:
    mod = _resilient_moderator()
    assert mod.detect_capitulation({"claim": "anything"}, Stance.PRO) is False


def test_intervene_returns_intervention_message() -> None:
    mod = _moderator("{}")
    msg = mod.intervene(Stance.CON, "stop conceding")
    assert msg["type"] == "intervention"
    assert msg["stance"] == "con"
