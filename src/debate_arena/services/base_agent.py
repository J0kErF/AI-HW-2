"""Abstract base agent (OOP root for Father and debaters; Guide §16).

Defines the shared contract: act(), JSON parsing/validation (via mixins),
error handling, and a gatekept LLM completion helper. Concrete agents implement
`_build_prompt` and `act`. Agents talk to the model through an injected client
(`complete(model, prompt, system) -> (text, (in_tokens, out_tokens))`), which
keeps them decoupled from the provider and trivial to mock.
"""

from abc import ABC, abstractmethod
from typing import Any

from debate_arena.services.mixins import JsonContractMixin, TokenAccountingMixin


class BaseAgent(TokenAccountingMixin, JsonContractMixin, ABC):
    """Common base for all agents.

    Input:  a routed message dict (from the Father / orchestrator).
    Output: a schema-valid message dict.
    Setup:  name, model id, and a gatekept LLM client.
    """

    def __init__(self, name: str, model: str, llm: Any) -> None:
        super().__init__()
        self.name = name
        self.model = model
        self._llm = llm

    @abstractmethod
    def act(self, message: dict[str, Any]) -> dict[str, Any]:
        """Produce this agent's next message in response to `message`."""
        raise NotImplementedError

    @abstractmethod
    def _build_prompt(self, message: dict[str, Any]) -> str:
        """Build the LLM prompt for this agent's role and current context."""
        raise NotImplementedError

    def _respond(self, prompt: str, system: str | None = None) -> str:
        """Call the LLM, account for tokens, and return the text."""
        text, (in_tokens, out_tokens) = self._llm.complete(self.model, prompt, system)
        self.record_tokens(in_tokens, out_tokens)
        return text

    def _safe_parse(self, raw: str) -> dict[str, Any]:
        """Parse JSON, returning {} on malformed input (graceful degradation)."""
        try:
            return self.parse_json(raw)
        except ValueError:
            return {}

    def handle_error(self, exc: Exception) -> dict[str, Any]:
        """Convert an exception into a structured `system` error message."""
        return {"type": "system", "stance": self.name, "error": str(exc)}
