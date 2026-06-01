# PRD — Watchdog / Timeout Mechanism

> Version 1.00 · Parent: [PRD.md](PRD.md)

## 1. Description & theory
Every autonomous-agent project must assume an agent can hang (Ex §8.6). The
Watchdog is a supervisor that monitors debater processes via a **keep-alive
heartbeat** and **per-call timeouts**, and — critically — on failure it
**kills and restarts** the process (not merely "skips it"). This is the
"real mechanics" the HW1 feedback demanded: no faked resilience.

## 2. Specific requirements
- **Timeout** on every agent/tool call (value from `config/setup.json`).
- **Heartbeat:** each debater process emits a heartbeat each loop tick; missing
  `max_missed_heartbeats` ⇒ considered hung.
- **Kill & restart:** terminate the process, respawn it with the same stance and
  the transcript context, resume the debate.
- **Bounded restarts:** at most `max_restarts` per agent; on exceeding, the
  orchestrator concludes early (still produces a verdict) and logs the failure.
- All watchdog actions logged as `system` events and surfaced in the UI
  (distinct style) and in `DebateResult.restarts`.

## 3. Interface
```python
class Watchdog:
    def supervise(self, proc, name, on_dead): ...   # register a process
    def heartbeat(self, name) -> None: ...          # called by/for the child
    def check(self) -> list[str]: ...               # names judged hung/dead
    def restart(self, name) -> Process: ...         # kill + respawn
```

## 4. Input / output
- **Input:** process handles, `timeout_seconds`, `heartbeat_interval`,
  `max_missed_heartbeats`, `max_restarts` (all config).
- **Output:** restart events; `on_dead(name)` callbacks; no return value on the
  happy path.

## 5. Constraints & alternatives
- *Alt: `concurrent.futures` timeout only* — insufficient: it abandons the future
  but cannot guarantee the worker is dead; a real process can be `terminate()`d.
- Uses `multiprocessing` primitives so a genuinely stuck child is force-killable.

## 6. Success criteria & edge cases (tested with fakes)
- Worker that sleeps past the timeout → detected → killed → restarted → debate
  resumes.
- Worker that exits/crashes → detected dead → restarted.
- Worker exceeding `max_restarts` → early, clean conclusion + verdict.
- Healthy worker → never restarted (no false positives).
