# PRD — Debate Orchestration Mechanism

> Version 1.00 · Parent: [PRD.md](PRD.md) · Design: [PLAN.md](PLAN.md)

## 1. Description & theory
The orchestrator implements a **hierarchical, hub-and-spoke** debate: the Father
is the only hub; debaters are spokes. This guarantees the brief's routing rule (every message
`child → father → child`) and gives a single place to enforce rules, log, and
account for cost. Debaters run as **separate OS processes** (per the brief; Guide §15)
communicating over `multiprocessing.Queue` — modeling true Inter-Process
Communication, and enabling forced restart by the Watchdog.

## 2. Specific requirements
- Maintain debate **state**: topic, round index, per-side ping counts, full
  ordered transcript, intervention log.
- Drive the loop for `pings_per_side` (target **≥10**; the free-tier capture uses
  **5** — see PRD.md budget note). The count is a single config value.
- For each turn: request → receive JSON → **validate** → enforce rules → log →
  route to opponent as context.
- Enforce **mutual reference**: a rebuttal's `responding_to` must equal the
  opponent's most recent `turn_id`.
- Enforce **anti-capitulation**: if a debater's stance polarity flips toward the
  opponent (detected by the Father, see PRD_judge_scoring §4), trigger
  `intervene()` and require a corrected turn.
- On any agent timeout/death, hand control to the Watchdog (kill & restart),
  record a `system` event, then continue; if restart fails twice, conclude early
  with the partial transcript and still produce a verdict.

## 3. Inter-agent message schema (JSON, validated)
```json
{
  "turn_id": "pro-3",
  "stance": "pro",
  "type": "argument | rebuttal | intervention | system",
  "responding_to": "con-2",
  "reasoning": "private chain (logged, not scored as output)",
  "claim": "public argument text",
  "sources": [{"title": "...", "url": "https://...", "snippet": "..."}],
  "tokens": {"prompt": 0, "completion": 0}
}
```

## 4. Input / output
- **Input:** `topic: str`, `rounds: int`, config (models, timeouts, personas).
- **Output:** `DebateResult{transcript: list[Message], verdict: Verdict,
  cost: CostReport, interventions: list, restarts: list}`.

## 5. Constraints & alternatives considered
- *Alt: asyncio* — rejected (ADR-1): cannot force-kill a hung coroutine.
- *Alt: single process, sequential* — rejected: violates "agent = process" framing
  and gives no real IPC/resilience story.

## 6. Success criteria & edge cases to test
- Happy path: 10/side completes, verdict produced.
- Malformed JSON from a child → caught, re-requested once, else `system` error turn.
- Missing/empty `sources` on an argument → rejected, re-requested.
- `responding_to` mismatch → rejected, re-requested.
- Child process killed mid-turn → Watchdog restart → loop continues.
- Capitulation → intervention recorded → corrected turn accepted.
