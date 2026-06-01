"""Abstract base agent (OOP root for Father and debaters; Guide §16).

Defines the shared contract: act(), parse_json() (via mixin), and handle_error().
Concrete agents implement `_build_prompt` and `act`.

NOTE: scaffold stub — LLM wiring lands in Phase 2.
"""

from abc import ABC, abstractmethod
from typing import Any

from debate_arena.services.mixins import JsonContractMixin, TokenAccountingMixin


class BaseAgent(TokenAccountingMixin, JsonContractMixin, ABC):
    """Common base for all agents.

    Input:  a routed message dict (from the Father / orchestrator).
    Output: a schema-valid message dict.
    Setup:  name, model id, and the shared gatekeeper for LLM calls.
    """

    def __init__(self, name: str, model: str, gatekeeper: Any) -> None:
        super().__init__()
        self.name = name
        self.model = model
        self._gatekeeper = gatekeeper

    @abstractmethod
    def act(self, message: dict[str, Any]) -> dict[str, Any]:
        """Produce this agent's next message in response to `message`."""
        raise NotImplementedError

    @abstractmethod
    def _build_prompt(self, message: dict[str, Any]) -> str:
        """Build the LLM prompt for this agent's role and current context."""
        raise NotImplementedError

    def handle_error(self, exc: Exception) -> dict[str, Any]:
        """Convert an exception into a structured `system` error message."""
        return {"type": "system", "stance": self.name, "error": str(exc)}
