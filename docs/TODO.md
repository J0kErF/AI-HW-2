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
- [x] **Gate:** team approves all docs · DoD: sign-off recorded in PROMPTS.md (see `PROMPTS.md` → **D-GATE**)

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
- [x] `services/web_search.py` WebSearchTool (provider-agnostic + gatekept + error boundary) · DoD: degrade-on-failure + cap tested (100%)
- [x] `services/base_agent.py` BaseAgent (act/parse_json/handle_error/_respond/_safe_parse) · DoD: malformed-JSON + token accounting tested (92%)
- [x] `services/debater.py` DebaterAgent (stance, persona, anti-capitulation, cites sources, `responding_to`) · DoD: rebuttal references prior turn (100%)
- [x] `services/moderator.py` ModeratorAgent/Father (validate, intervene, capitulation, judge — blind, no tie + tie-break) · DoD: tie never returned (93%)
- [x] real search providers (Tavily/DuckDuckGo) behind the injected `provider` callable — delivered in Phase 3 (`services/search_providers.py`, config-selected)

> **Phase 2 core complete.** Global coverage **86.9%** ≥ 85% gate. 62 tests pass.

## Phase 3 — Orchestration & SDK
- [x] `services/orchestrator.py` — drives ≥10 pings/side over a DebaterHandle transport; watchdog restart on timeout; graceful conclusion (97%)
- [x] `services/process_handle.py` — real multiprocessing + Queue IPC (one process per debater); integration glue
- [x] `services/search_providers.py` — Tavily + DuckDuckGo (`ddgs`) providers, config-selected
- [x] `sdk/sdk.py` DebateSDK facade (run_debate, get_transcript, get_cost_report) with offline injection points (100%)
- [x] `main.py` thin entry → SDK
- [x] **LIVE e2e verified**: real spawned processes + web search + Gemini → Pro argued w/ 3 sources, Con hit 503 → watchdog restarted it → Father judged, no tie, no crash.

> **Phase 3 complete.** 72 tests, 94.97% coverage, ruff clean.
> Resilience fix: Father LLM calls degrade gracefully (`_safe_respond`); transient
> 429/5xx mapped to gatekeeper retry; JSON fence-stripping for model replies.

### Phase 3 follow-ups (resolved in Phase 4)
- [x] Aggregate cost across worker processes from each turn's `tokens` field (per-process gatekeepers don't share state) → real cost table. Done in `services/reporting.py` (100% tested); cost table filled in README §6.
- [x] Free-tier note: `gemini-2.5-pro` has 0 free quota; using `gemini-2.5-flash`. 503s are intermittent on free tier — set **pings = 5** for the captured run (README §6/§9).

## Phase 4 — UX
- [x] `cli/menu.py` keyboard terminal menu (Run / Replay / Cost / Config / Quit) · DoD: every feature reachable; smoke-tested
- [x] `cli/render.py` `rich` rendering: distinct styles per Pro/Con/intervention/system/validation/moderation
- [x] `services/reporting.py` cost aggregation (cross-process, from transcript tokens) + transcript export to `results/` (txt + json) · DoD: tested (100%)
- [x] SDK threads `on_event` for live rendering; `get_cost_report` now returns real aggregated cost
- [x] capture run output for README — committed verbatim **terminal output** in `docs/sample_run/` (transcript.txt/json + rerun_console.txt) in lieu of PNGs (headless terminal app); referenced from README §7. _Optional: add PNG screenshots of the interactive menu if a desktop session is available._

> **Phase 4 complete.** 77 tests, 95.39% coverage, ruff clean. Cross-process
> cost issue resolved (debater tokens travel in the IPC payload).

## Phase 5 — Delivery & verification
- [ ] `uv run ruff check` → 0 violations
- [ ] `uv run pytest --cov=src` → ≥85% (branch/path on critical paths)
- [ ] Cost analysis table (tokens in/out, $/M, per model) in README
- [ ] Architecture diagrams + screenshots embedded in README
- [ ] Full session transcript + Prompt Book finalized
- [ ] **Honest self-grade ~88–90** + "Known Limitations" section (HW1 lesson — do NOT inflate)
- [ ] Fill official Word template → `moamteam-ex02.pdf`; share repo with rmisegal@gmail.com; both partners submit on Moodle

---

## Resolved decisions
- [x] **Group code**: **`moamteam`** (confirmed). Submission PDF: `moamteam-ex02.pdf`.
- [x] **LLM provider**: **Google Gemini, free tier**, `gemini-2.5-flash` for debaters AND moderator (`gemini-2.5-pro` has 0 free quota).
- [x] **Web search**: **DuckDuckGo (`ddgs`), keyless / free** — no Tavily key required (Tavily kept optional via config).
- [x] **Pings**: **5 per side** (reduced from 10 for the free tier; permitted by Ex §8.7, noted in README).
- [x] **Default topic**: "Nuclear energy should be a core part of the climate solution" (configurable).
