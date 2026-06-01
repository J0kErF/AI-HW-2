"""Reusable, single-concern mixins (Guide §4.2).

Each mixin handles exactly one concern, overrides no other mixin's methods, and
is independently testable. Factored out to avoid duplication across agents.
"""

import json
from typing import Any


class JsonContractMixin:
    """Parse and validate strict-JSON agent messages."""

    @staticmethod
    def parse_json(raw: str) -> dict[str, Any]:
        """Parse a JSON string, raising ValueError on malformed input."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON message: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("Agent message must be a JSON object")
        return data


class TokenAccountingMixin:
    """Accumulate prompt/completion token counts across calls."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._prompt_tokens = 0
        self._completion_tokens = 0

    def record_tokens(self, prompt: int, completion: int) -> None:
        """Add a call's token usage to the running totals."""
        self._prompt_tokens += prompt
        self._completion_tokens += completion

    @property
    def token_totals(self) -> dict[str, int]:
        """Return cumulative prompt/completion token counts."""
        return {"prompt": self._prompt_tokens, "completion": self._completion_tokens}
