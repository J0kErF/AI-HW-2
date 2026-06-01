"""OpenAI-compatible LLM client (NVIDIA build.nvidia.com / DeepSeek, etc.).

Wraps the OpenAI SDK against any OpenAI-compatible endpoint and routes every call
through the ApiGatekeeper. Retryable provider errors (429/5xx) are mapped to
ConnectionError so the gatekeeper retries with backoff. The underlying client is
injectable for offline testing.
"""

from typing import Any

from openai import APIConnectionError, APIError, OpenAI

_RETRYABLE_CODES = {429, 500, 502, 503, 504}


def _usage_openai(resp: Any) -> tuple[int, int]:
    """Extract (input_tokens, output_tokens) from an OpenAI-style response."""
    usage = getattr(resp, "usage", None)
    if usage is None:
        return (0, 0)
    return (getattr(usage, "prompt_tokens", 0) or 0, getattr(usage, "completion_tokens", 0) or 0)


class OpenAICompatClient:
    """Gatekept wrapper over an OpenAI-compatible chat endpoint.

    Input:  a model id, a user prompt, and an optional system instruction.
    Output: (text, (input_tokens, output_tokens)).
    Setup:  an ApiGatekeeper, api key, and base_url (e.g. NVIDIA integrate API).
    """

    def __init__(self, gatekeeper: Any, api_key: str, base_url: str,
                 client: Any = None) -> None:
        self._gk = gatekeeper
        self._client = client or OpenAI(base_url=base_url, api_key=api_key)

    def complete(self, model: str, prompt: str, system: str | None = None) -> tuple[str, tuple]:
        """Generate a completion, accounted and rate-limited via the gatekeeper."""
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        def _call() -> Any:
            try:
                return self._client.chat.completions.create(
                    model=model, messages=messages, temperature=0.7, max_tokens=4096,
                    extra_body={"chat_template_kwargs": {"thinking": False}},
                )
            except APIConnectionError as exc:
                raise ConnectionError(str(exc)) from exc
            except APIError as exc:
                if getattr(exc, "status_code", None) in _RETRYABLE_CODES:
                    raise ConnectionError(str(exc)) from exc
                raise

        resp = self._gk.execute(_call, service="llm", model=model, usage_extractor=_usage_openai)
        message = resp.choices[0].message
        text = message.content or getattr(message, "reasoning_content", "") or ""
        return text, _usage_openai(resp)
