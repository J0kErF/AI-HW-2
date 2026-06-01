# TODO — debate_arena (HW2)

Status legend: `[ ]` not started · `[~]` in progress · `[x]` done
Work order is mandated by Guide §2.5: **docs approved before any code.**

---

## Phase 0 — Planning & docs (approve before coding)
- [x] `docs/PRD.md` — requirements, KPIs, debate rules · **owner:** team · DoD: approved
- [x] `docs/PLAN.md` — C4 + UML + sequence + ADRs · DoD: diagrams render, ADRs justified
- [x] `docs/TODO.md` — this file
- [x] `docs/PRD_debate_orchestration.md`
- [x] `docs/PRD_judge_scoring.md`
- [x] `docs/PRD_watchdog.md`
- [x] `docs/PRD_gatekeeper.md`
- [x] `docs/PRD_web_search.md`
- [x] `docs/PROMPTS.md` — prompt/decision log (living document)
- [ ] **Gate:** team approves all docs · DoD: sign-off recorded in PROMPTS.md

## Phase 1 — Core engineering (OOP utilities, TDD)
- [x] `shared/version.py` (=1.00) + startup config-version validation · DoD: test asserts mismatch raises
- [x] `shared/config.py` ConfigManager (loads `config/*.json` + `.env`, no hardcoding) · DoD: edge tests (missing key, bad version)
- [x] `shared/rate_limiter.py` SlidingWindowLimiter · DoD: minute/hour limits + window-free tested (96%)
- [x] `shared/budget.py` BudgetTracker (cost-per-million, totals, would_exceed) · DoD: 100% covered
- [x] `shared/gatekeeper.py` ApiGatekeeper (rate limit, FIFO queue, backpressure, retry, budget cap, log) · DoD: limit-hit→queue, queue-full→backpressure, budget→block, retry tested (99%)
- [x] `shared/logging_setup.py` FIFO rotating logs from `logging_config.json` · DoD: line-cap rotation + bounded file count tested (85%)
- [x] `services/watchdog.py` Watchdog (keep-alive heartbeat, timeout, kill & restart) · DoD: hang→flag, dead→flag+callback, restart, max-restarts tested (100%)
- [x] mixins: `JsonContractMixin`, `TokenAccountingMixin` · DoD: each tested in isolation (100%)
- [x] **Bonus:** `services/llm_client.py` GeminiClient (gatekept) + `shared/env.py` secrets bootstrap — live-verified

> **Phase 1 complete.** All core utilities implemented + tested ≥85% each.
> Global coverage reaches ≥85% once Phase 2/3 fill the agent/orchestrator stubs.

## Phase 2 — Tool & agents (mocked LLM/search in tests)
- [ ] `services/web_search.py` WebSearchTool (real provider + error boundary) · DoD: returns real sources; failure → graceful empty + flag
- [ ] `services/base_agent.py` BaseAgent (act/parse_json/handle_error) · DoD: malformed-JSON test
- [ ] `services/debater.py` DebaterAgent (stance, persona, anti-capitulation, cites sources, `responding_to`) · DoD: rebuttal references prior turn
- [ ] `services/moderator.py` ModeratorAgent/Father (route, intervene, judge — blind, no tie) · DoD: tie never returned; intervention on capitulation

## Phase 3 — Orchestration & SDK
- [ ] `services/orchestrator.py` multiprocessing + Queue IPC, ≥10 pings/side · DoD: full mocked debate end-to-end
- [ ] `sdk/sdk.py` DebateSDK facade (run_debate, get_transcript, get_cost_report) · DoD: integration test drives debate via SDK only
- [ ] `main.py` thin entry → SDK · DoD: no logic in main beyond wiring

## Phase 4 — UX
- [ ] `cli/menu.py` keyboard terminal menu (Run debate / Replay / Show cost / Config / Quit) · DoD: every feature reachable from menu
- [ ] `rich` rendering: distinct styles for Father / Pro / Con / Watchdog / System · DoD: screenshot captured
- [ ] transcript export to `results/` (EN/HE) · DoD: full session saved

## Phase 5 — Delivery & verification
- [ ] `uv run ruff check` → 0 violations
- [ ] `uv run pytest --cov=src` → ≥85% (branch/path on critical paths)
- [ ] Cost analysis table (tokens in/out, $/M, per model) in README
- [ ] Architecture diagrams + screenshots embedded in README
- [ ] Full session transcript + Prompt Book finalized
- [ ] **Honest self-grade ~88–90** + "Known Limitations" section (HW1 lesson — do NOT inflate)
- [ ] Fill official Word template → `uoh-rl07-ex02.pdf`; share repo with rmisegal@gmail.com; both partners submit on Moodle

---

## Open questions (resolve before/early in Phase 1)
- [ ] **Group code**: HW1 feedback shows `moamteam`; template file is `uoh-rl07`. Confirm the registered 8-char code.
- [ ] **LLM provider + web-search provider** to standardize on (Anthropic + Tavily assumed).
- [ ] **Pings**: keep 10/side, or reduce to 5/side for budget (must note in README).
- [ ] **Default topic** for the canned demo run.
