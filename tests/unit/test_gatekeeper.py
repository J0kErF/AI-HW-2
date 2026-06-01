"""Tests for the central API gatekeeper (happy path + edge + failure modes)."""

import pytest

from debate_arena.shared.gatekeeper import (
    ApiGatekeeper,
    BudgetExceededError,
    RateLimitedError,
)


def _service(rpm: int = 100, queue: int = 5, retries: int = 2) -> dict:
    return {
        "requests_per_minute": rpm,
        "requests_per_hour": 1000,
        "concurrent_max": 5,
        "retry_after_seconds": 0,
        "max_retries": retries,
        "queue_max_depth": queue,
    }


def _rate(**kw) -> dict:
    return {"version": "1.00", "services": {"default": _service(**kw)}}


BUDGET = {
    "budget_usd": 1.0,
    "block_on_exceed": True,
    "price_per_million": {"m": {"input": 1.0, "output": 1.0}},
}


def _gk(rate=None, budget=None, clock=None, sleep=None) -> ApiGatekeeper:
    state = {"t": 0.0}
    return ApiGatekeeper(
        rate or _rate(),
        budget or BUDGET,
        clock=clock or (lambda: state["t"]),
        sleep=sleep or (lambda _s: None),
    )


def test_happy_path_returns_result() -> None:
    gk = _gk()
    assert gk.execute(lambda: "ok") == "ok"


def test_token_accounting_and_cost() -> None:
    gk = _gk()
    gk.execute(lambda: "ok", model="m", usage_extractor=lambda _r: (1_000_000, 0))
    report = gk.get_cost_report()
    assert report.input_tokens == 1_000_000
    assert report.cost_usd == 1.0


def test_budget_block_after_exhaustion() -> None:
    gk = _gk()
    gk.execute(lambda: "ok", model="m", usage_extractor=lambda _r: (1_000_000, 0))
    with pytest.raises(BudgetExceededError):
        gk.execute(lambda: "ok")


def test_backpressure_raises_when_queue_full() -> None:
    gk = _gk(rate=_rate(rpm=1, queue=0))
    gk.execute(lambda: "ok")  # fills the 1/minute window
    with pytest.raises(RateLimitedError):
        gk.execute(lambda: "ok")


def test_waits_when_queue_has_room() -> None:
    sleeps: list[float] = []
    gk = _gk(rate=_rate(rpm=1, queue=5), sleep=sleeps.append)
    gk.execute(lambda: "ok")
    assert gk.execute(lambda: "ok") == "ok"
    assert sleeps and sleeps[0] > 0


def test_retry_then_success() -> None:
    gk = _gk()
    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 2:
            raise TimeoutError("transient")
        return "ok"

    assert gk.execute(flaky) == "ok"
    assert calls["n"] == 2


def test_retry_exhausted_reraises() -> None:
    gk = _gk(rate=_rate(retries=1))

    def always() -> str:
        raise TimeoutError("down")

    with pytest.raises(TimeoutError):
        gk.execute(always)


def test_queue_status_reports_capacity() -> None:
    gk = _gk(rate=_rate(queue=7))
    assert gk.get_queue_status().max_depth == 7
