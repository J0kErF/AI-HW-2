"""Central API gatekeeper — the only path to external APIs (Guide §5).

Enforces config-driven rate limits, FIFO queueing with backpressure, retries,
a hard budget cap, and per-call logging. Full behaviour: docs/PRD_gatekeeper.md.

NOTE: scaffold stub — Phase 1 implements the logic under TDD.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


class RateLimitedError(RuntimeError):
    """Raised when the queue is full past its configured max depth."""


class BudgetExceededError(RuntimeError):
    """Raised when a call would push cumulative cost past the budget cap."""


@dataclass
class CostReport:
    """Aggregated token/cost accounting for the run."""

    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    per_service: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class QueueStatus:
    """Snapshot of the gatekeeper queue."""

    depth: int = 0
    max_depth: int = 0


class ApiGatekeeper:
    """Centralized API call manager (interface per Guide §5.1).

    Input:  rate-limit + budget config; a service name per call.
    Output: the wrapped call's result, or raises RateLimited / BudgetExceeded.
    Setup:  limits/budget come from config/rate_limits.json (never hardcoded).
    """

    def __init__(self, rate_config: dict[str, Any], budget_config: dict[str, Any]) -> None:
        self._rate = rate_config
        self._budget = budget_config
        self._report = CostReport()

    def execute(self, api_call: Callable[..., Any], *args: Any, service: str = "default",
                **kwargs: Any) -> Any:
        """Run an external call through rate-limit → budget → retry → log."""
        raise NotImplementedError("Phase 1: implement rate limit, queue, retry, budget, log")

    def get_queue_status(self) -> QueueStatus:
        """Return current queue depth and capacity."""
        raise NotImplementedError("Phase 1")

    def get_cost_report(self) -> CostReport:
        """Return aggregated token/cost accounting."""
        return self._report
