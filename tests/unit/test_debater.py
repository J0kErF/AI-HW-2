"""Tests for the DebaterAgent (mocked LLM + search)."""

from debate_arena.constants import Stance
from debate_arena.services.debater import DebaterAgent
from debate_arena.services.web_search import Source


class _FakeLLM:
    def __init__(self, text: str) -> None:
        self.text = text

    def complete(self, model, prompt, system=None) -> tuple:
        return self.text, (5, 7)


class _FakeSearch:
    def __init__(self, sources) -> None:
        self._sources = sources
        self.degraded = False

    def search(self, query, k=None):
        return self._sources


def _debater(text: str, sources=None) -> DebaterAgent:
    sources = sources if sources is not None else [Source("T", "https://x", "snip")]
    return DebaterAgent(
        "pro-agent", Stance.PRO, "relentless advocate", "gemini-2.5-flash",
        _FakeLLM(text), _FakeSearch(sources),
    )


def test_opening_argument_shape() -> None:
    d = _debater('{"reasoning": "r", "claim": "Nuclear is clean"}')
    out = d.act({"topic": "Nuclear energy"})
    assert out["type"] == "argument"
    assert out["responding_to"] is None
    assert out["stance"] == "pro"
    assert out["turn_id"] == "pro-1"
    assert out["claim"] == "Nuclear is clean"
    assert out["sources"] and out["sources"][0]["url"] == "https://x"


def test_rebuttal_references_opponent_turn() -> None:
    d = _debater('{"reasoning": "r", "claim": "Your data is stale"}')
    out = d.act({"turn_id": "con-2", "claim": "Nuclear is risky", "topic": "Nuclear energy"})
    assert out["type"] == "rebuttal"
    assert out["responding_to"] == "con-2"


def test_malformed_json_falls_back_to_raw_claim() -> None:
    d = _debater("not json at all")
    out = d.act({"topic": "Nuclear energy"})
    assert out["claim"] == "not json at all"


def test_tokens_are_accounted() -> None:
    d = _debater('{"claim": "c"}')
    out = d.act({"topic": "Nuclear energy"})
    assert out["tokens"] == {"prompt": 5, "completion": 7}
