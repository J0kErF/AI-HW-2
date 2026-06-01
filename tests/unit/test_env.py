"""Tests for env/secrets helpers and the genai usage extractor."""

import pytest

from debate_arena.services.llm_client import _usage
from debate_arena.shared.env import gemini_api_key, use_vertex


def test_gemini_api_key_prefers_gemini_var(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "abc")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    assert gemini_api_key() == "abc"


def test_gemini_api_key_missing_raises(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        gemini_api_key()


def test_use_vertex_defaults_false(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_GENAI_USE_VERTEXAI", raising=False)
    assert use_vertex() is False
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")
    assert use_vertex() is True


def test_usage_extractor_handles_missing_metadata() -> None:
    class _Resp:
        usage_metadata = None

    assert _usage(_Resp()) == (0, 0)


def test_usage_extractor_reads_token_counts() -> None:
    class _Meta:
        prompt_token_count = 7
        candidates_token_count = 3

    class _Resp:
        usage_metadata = _Meta()

    assert _usage(_Resp()) == (7, 3)
