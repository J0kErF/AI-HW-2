"""Budget tracker (single concern; used by the gatekeeper).

Computes per-call cost from a price-per-million table, accumulates token and
cost totals globally and per service, and reports when the budget is reached.
"""

from typing import Any


class BudgetTracker:
    """Cumulative token/cost accounting against a USD cap.

    Input:  budget_usd and a {model: {input, output}} price-per-million table.
    Output: cost figures via `record`, `total_cost`, `would_exceed`.
    Setup:  block_on_exceed governs whether the gatekeeper should hard-stop.
    """

    def __init__(self, budget_usd: float, price_per_million: dict[str, dict[str, float]],
                 block_on_exceed: bool = True) -> None:
        self.budget_usd = budget_usd
        self.block_on_exceed = block_on_exceed
        self._prices = price_per_million
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = 0.0
        self.per_service: dict[str, dict[str, Any]] = {}

    def cost_of(self, model: str | None, input_tokens: int, output_tokens: int) -> float:
        """Return the USD cost of a call; unknown/None model costs 0.0."""
        price = self._prices.get(model or "", {})
        return (input_tokens / 1_000_000) * price.get("input", 0.0) + (
            output_tokens / 1_000_000
        ) * price.get("output", 0.0)

    def record(self, service: str, model: str | None, input_tokens: int,
               output_tokens: int) -> float:
        """Accumulate a call's tokens/cost; return the cost added."""
        cost = self.cost_of(model, input_tokens, output_tokens)
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_cost += cost
        bucket = self.per_service.setdefault(
            service, {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
        )
        bucket["input_tokens"] += input_tokens
        bucket["output_tokens"] += output_tokens
        bucket["cost_usd"] += cost
        return cost

    def would_exceed(self, prospective_cost: float = 0.0) -> bool:
        """True if total + prospective cost is at or over the budget."""
        return self.total_cost + prospective_cost >= self.budget_usd
