# PRD — Web Search Tool (grounding)

> Version 1.00 · Parent: [PRD.md](PRD.md)

## 1. Description & theory
Grounding arguments in **real** web evidence is mandatory (the assignment brief). The
WebSearchTool is the agents' only path to the outside world; it returns real
sources that become the `sources[]` of a debate message. It is a concrete
instance of the course's "Tool" concept and routes through the Gatekeeper.

## 2. Specific requirements
- Pluggable provider behind one interface (default: Tavily; fallback:
  DuckDuckGo). Provider chosen via `config/setup.json` — no hardcoding.
- Returns a normalized `list[Source]{title, url, snippet}`.
- **Error boundary:** on provider failure/timeout, degrade gracefully — return an
  empty list plus a `degraded=True` flag; the debater must then either retry or
  emit a turn flagged as unsupported (the orchestrator rejects an *argument* with
  no sources, forcing a retry — see PRD_debate_orchestration §6).
- All calls go through `ApiGatekeeper.execute` (rate limit + budget + log).
- No fabricated citations: sources must originate from a real provider response.

## 3. Interface
```python
class WebSearchTool:
    def __init__(self, gatekeeper, provider, config): ...
    def search(self, query: str, k: int = 3) -> list[Source]: ...
```

## 4. Input / output
- **Input:** `query: str`, `k: int` (result count, config default).
- **Output:** `list[Source]` (possibly empty when degraded).

## 5. Constraints & alternatives
- *Alt: scrape arbitrary pages* — rejected: brittle, ToS risk; a search API is
  cleaner and rate-limitable.
- *Alt: no tool, model "remembers"* — rejected: violates the mandatory-grounding
  rule and invites hallucinated citations.

## 6. Success criteria & edge cases (mocked in tests)
- Normal query → ≥1 normalized source.
- Provider timeout/5xx → `degraded=True`, empty list, no crash.
- Empty/whitespace query → handled (no call), returns empty.
- Every search recorded by the Gatekeeper (asserted in an integration test).
