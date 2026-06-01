"""Tests for the abstract BaseAgent via a minimal concrete subclass."""

from typing import Any

from debate_arena.services.base_agent import BaseAgent


class _FakeLLM:
    def complete(self, model: str, prompt: str, system: str | None = None) -> tuple:
        return "hello", (3, 4)


class _Concrete(BaseAgent):
    def act(self, message: dict[str, Any]) -> dict[str, Any]:
        return {}

    def _build_prompt(self, message: dict[str, Any]) -> str:
        return "p"


def test_respond_returns_text_and_records_tokens() -> None:
    agent = _Concrete("x", "m", _FakeLLM())
    assert agent._respond("p") == "hello"
    assert agent.token_totals == {"prompt": 3, "completion": 4}


def test_handle_error_returns_system_message() -> None:
    agent = _Concrete("x", "m", _FakeLLM())
    msg = agent.handle_error(ValueError("boom"))
    assert msg["type"] == "system"
    assert "boom" in msg["error"]


def test_safe_parse_recovers_from_malformed_json() -> None:
    agent = _Concrete("x", "m", _FakeLLM())
    assert agent._safe_parse("{not json}") == {}
    assert agent._safe_parse('{"a": 1}') == {"a": 1}
