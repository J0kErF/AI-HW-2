"""Tests for the OpenAI-compatible client (offline, injected client)."""

from debate_arena.services.openai_client import OpenAICompatClient, _usage_openai


class _Usage:
    prompt_tokens = 11
    completion_tokens = 4


class _Message:
    content = "hi"
    reasoning_content = None


class _Choice:
    message = _Message()


class _Resp:
    choices = [_Choice()]
    usage = _Usage()


class _Completions:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _Resp()


class _FakeOpenAI:
    def __init__(self) -> None:
        self.chat = type("Chat", (), {"completions": _Completions()})()


class _GK:
    def execute(self, call, *args, service="default", **kwargs):
        return call()


def test_complete_returns_text_and_usage() -> None:
    client = OpenAICompatClient(_GK(), "key", "url", client=_FakeOpenAI())
    text, usage = client.complete("deepseek", "prompt", "system")
    assert text == "hi"
    assert usage == (11, 4)


def test_usage_openai_handles_missing_usage() -> None:
    class _R:
        usage = None

    assert _usage_openai(_R()) == (0, 0)
