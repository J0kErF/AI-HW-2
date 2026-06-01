"""Central API gatekeeper — the only path to external APIs (Guide §5).

Enforces config-driven rate limits, FIFO queueing with backpressure, retries,
a hard budget cap, and per-call logging. Full behaviour: docs/PRD_gatekeeper.md.
Rate-limit and budget mechanics live in single-concern helpers (rate_limiter,
budget); this module orchestrates them.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from debate_arena.shared.budget import BudgetTracker
from debate_arena.shared.rate_limiter import SlidingWindowLimiter

_TRANSIENT = (ConnectionError, TimeoutError)


class RateLimitedError(RuntimeError):
    """Raised when the wait queue is full past its configured max depth."""


class BudgetExceededError(RuntimeError):
    """Raised when the budget cap has been reached and blocking is enabled."""


@dataclass
class CostReport:
    """Aggregated token/cost accounting for the run."""

    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    per_service: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class QueueStatus:
    """Snapshot of the gatekeeper wait queue."""

    depth: int = 0
    max_depth: int = 0


class ApiGatekeeper:
    """Centralized API call manager (interface per Guide §5.1).

    Input:  the full rate_limits config dict and its budget section; per call,
            a callable plus a service name and optional model/usage_extractor.
    Output: the wrapped call's result, or raises RateLimitedError /
            BudgetExceededError / the underlying error after retries.
    Setup:  limits/budget come from config (never hardcoded); clock/sleep/logger
            are injectable for testing.
    """

    def __init__(self, rate_config: dict[str, Any], budget_config: dict[str, Any],
                 clock: Callable[[], float] = time.time,
                 sleep: Callable[[float], None] = time.sleep,
                 logger: Any | None = None) -> None:
        self._services = rate_config["services"]
        self._clock = clock
        self._sleep = sleep
        self._log = logger
        self._limiters: dict[str, SlidingWindowLimiter] = {}
        self._waiting = 0
        self._max_depth = self._services["default"].get("queue_max_depth", 0)
        self._budget = BudgetTracker(
            budget_config["budget_usd"],
            budget_config.get("price_per_million", {}),
            budget_config.get("block_on_exceed", True),
        )

    def _limiter(self, service: str) -> SlidingWindowLimiter:
        cfg = self._services.get(service, self._services["default"])
        self._max_depth = cfg.get("queue_max_depth", 0)
        if service not in self._limiters:
            self._limiters[service] = SlidingWindowLimiter(
                cfg["requests_per_minute"], cfg["requests_per_hour"], self._clock
            )
        return self._limiters[service]

    def _throttle(self, limiter: SlidingWindowLimiter, queue_max: int) -> None:
        wait = limiter.time_until_free()
        if wait <= 0:
            return
        self._waiting += 1
        if self._waiting > queue_max:
            self._waiting -= 1
            raise RateLimitedError(f"wait queue full (max_depth={queue_max})")
        try:
            self._sleep(wait)
        finally:
            self._waiting -= 1

    def _invoke(self, api_call: Callable[..., Any], cfg: dict[str, Any],
                args: tuple, kwargs: dict) -> Any:
        attempts = cfg.get("max_retries", 0) + 1
        for i in range(attempts):
            try:
                return api_call(*args, **kwargs)
            except _TRANSIENT:
                if i == attempts - 1:
                    raise
                self._sleep(cfg.get("retry_after_seconds", 0))
        return None  # pragma: no cover

    def execute(self, api_call: Callable[..., Any], *args: Any, service: str = "default",
                model: str | None = None,
                usage_extractor: Callable[[Any], tuple[int, int]] = lambda _r: (0, 0),
                **kwargs: Any) -> Any:
        """Run an external call through budget → rate-limit → retry → accounting."""
        if self._budget.block_on_exceed and self._budget.would_exceed():
            raise BudgetExceededError(f"budget ${self._budget.budget_usd} reached")
        cfg = self._services.get(service, self._services["default"])
        limiter = self._limiter(service)
        self._throttle(limiter, cfg.get("queue_max_depth", 0))
        limiter.record()
        result = self._invoke(api_call, cfg, args, kwargs)
        in_tok, out_tok = usage_extractor(result)
        cost = self._budget.record(service, model, in_tok, out_tok)
        if self._log is not None:
            self._log.info("api_call service=%s model=%s cost=%.4f", service, model, cost)
        return result

    def get_queue_status(self) -> QueueStatus:
        """Return current wait-queue depth and capacity."""
        return QueueStatus(depth=self._waiting, max_depth=self._max_depth)

    def get_cost_report(self) -> CostReport:
        """Return aggregated token/cost accounting."""
        return CostReport(
            input_tokens=self._budget.input_tokens,
            output_tokens=self._budget.output_tokens,
            cost_usd=self._budget.total_cost,
            per_service=self._budget.per_service,
        )
