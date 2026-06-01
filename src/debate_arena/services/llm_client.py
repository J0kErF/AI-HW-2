"""Gemini LLM client adapter.

Wraps the google-genai SDK and routes every call through the ApiGatekeeper, so
rate limits, budget, retries, and logging apply uniformly (Guide §5). Token
usage is reported back to the gatekeeper for cost accounting.
"""

from typing import Any

from google import genai
from google.genai import types


def _usage(resp: Any) -> tuple[int, int]:
    """Extract (input_tokens, output_tokens) from a genai response."""
    meta = getattr(resp, "usage_metadata", None)
    if meta is None:
        return (0, 0)
    return (meta.prompt_token_count or 0, meta.candidates_token_count or 0)


class GeminiClient:
    """Thin, gatekept wrapper over google-genai.

    Input:  a model id, a user prompt, and an optional system instruction.
    Output: (text, (input_tokens, output_tokens)).
    Setup:  an ApiGatekeeper and the Gemini API key (developer API).
    """

    def __init__(self, gatekeeper: Any, api_key: str) -> None:
        self._gk = gatekeeper
        self._client = genai.Client(api_key=api_key)

    def complete(self, model: str, prompt: str, system: str | None = None) -> tuple[str, tuple]:
        """Generate a completion, accounted and rate-limited via the gatekeeper."""
        config = types.GenerateContentConfig(system_instruction=system) if system else None

        def _call() -> Any:
            return self._client.models.generate_content(
                model=model, contents=prompt, config=config
            )

        resp = self._gk.execute(_call, service="llm", model=model, usage_extractor=_usage)
        return (resp.text or ""), _usage(resp)
