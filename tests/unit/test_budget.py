"""Tests for the budget tracker."""

from debate_arena.shared.budget import BudgetTracker

PRICES = {"m": {"input": 10.0, "output": 20.0}}


def test_cost_of_computes_from_price_per_million() -> None:
    bt = BudgetTracker(budget_usd=1.0, price_per_million=PRICES)
    assert bt.cost_of("m", 1_000_000, 0) == 10.0
    assert bt.cost_of("m", 0, 1_000_000) == 20.0


def test_unknown_model_costs_zero() -> None:
    bt = BudgetTracker(budget_usd=1.0, price_per_million=PRICES)
    assert bt.cost_of("missing", 1_000_000, 1_000_000) == 0.0


def test_record_accumulates_totals_and_per_service() -> None:
    bt = BudgetTracker(budget_usd=100.0, price_per_million=PRICES)
    added = bt.record("llm", "m", 1_000_000, 0)
    assert added == 10.0
    assert bt.total_cost == 10.0
    assert bt.input_tokens == 1_000_000
    assert bt.per_service["llm"]["cost_usd"] == 10.0


def test_would_exceed_at_or_over_budget() -> None:
    bt = BudgetTracker(budget_usd=1.0, price_per_million=PRICES)
    assert bt.would_exceed(0.0) is False
    bt.record("llm", "m", 100_000, 0)  # 1.0 exactly
    assert bt.would_exceed(0.0) is True
