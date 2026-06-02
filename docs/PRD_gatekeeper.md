# PRD — API Gatekeeper & Budget Control

> Version 1.00 · Parent: [PRD.md](PRD.md) · Rubric: Guide §5

## 1. Description & theory
Every external API call (LLM + web search) **must** flow through one central
`ApiGatekeeper` (Guide §5.1; the assignment brief "Gatekeeper — economic blocking layer").
It is the difference between *measuring* cost (a token tracker) and *enforcing*
it. The Gatekeeper applies rate limits, queues on saturation, retries transient
failures, **hard-stops on budget exhaustion**, and logs every call.

## 2. Specific requirements
- **No direct API calls** anywhere else (asserted by a test that greps the code
  base for provider SDK calls outside `gatekeeper.py`/the tool adapters).
- **Rate limits from config** (`config/rate_limits.json`, versioned) — never
  hardcoded (Guide §5.2/§7.2).
- **FIFO queue** with a configured max depth + **backpressure** when full
  (Guide §5.3); drained as rate windows reset; requests are queued, **not dropped**.
- **Retry** transient failures up to `max_retries` with `retry_after_seconds`.
- **Budget cap:** track cumulative tokens & $; when projected cost would exceed
  `budget_usd`, **block** further calls and raise `BudgetExceeded` (graceful
  degradation: the debate concludes early and still judges).
- **Logging:** every call (service, tokens, latency, outcome) logged via the FIFO
  logger.

## 3. Interface (Guide §5.1)
```python
class ApiGatekeeper:
    def __init__(self, config: RateLimitConfig, budget: BudgetConfig): ...
    def execute(self, api_call, *args, **kwargs):  # the only way out
        # check rate limit -> queue if needed -> check budget -> call
        # -> retry on transient -> record tokens/cost -> log
        ...
    def get_queue_status(self) -> QueueStatus: ...
    def get_cost_report(self) -> CostReport: ...
```

## 4. Config (`config/rate_limits.json`, excerpt)
```json
{
  "version": "1.00",
  "services": {
    "default": {"requests_per_minute": 30, "requests_per_hour": 500,
                "concurrent_max": 5, "retry_after_seconds": 30, "max_retries": 3}
  },
  "budget": {"budget_usd": 1.00, "block_on_exceed": true}
}
```

## 5. Input / output
- **Input:** a callable + args, plus service name for per-service limits.
- **Output:** the call's result, or raises `RateLimited`(queued past max) /
  `BudgetExceeded` / the underlying error after retries.

## 6. Success criteria & edge cases
- Burst beyond `requests_per_minute` → excess queued (FIFO), then drained.
- Queue full → backpressure signal, not silent drop.
- Cumulative cost crosses `budget_usd` → next `execute` blocks + raises.
- Transient 5xx → retried up to `max_retries`, then surfaced.
- Cost report totals match the sum of per-call records (accounting invariant).
