# Product Requirements Document (PRD) — HW2: Autonomous AI Agent Debate System

> Project code name: **debate_arena** · Document version: **1.00**
> Course: Building with LLMs (Dr. Yoram Segal) · Exercise 02 — AI Agent Debate

---

## 1. Project Overview & Context

`debate_arena` is an **autonomous multi-agent debate system**. Two debater
sub-agents argue opposing sides of a configurable motion. A third agent — the
**Moderator ("Father")** — orchestrates every turn, enforces the rules, and acts
as the **final judge**. The system shifts the focus from single-turn prompt
engineering (HW1) to **stateful, context-aware, multi-process orchestration**
with real external tool use and resilience engineering.

### 1.1 User problem
A reader/grader wants to watch two genuinely opposed LLM agents debate a topic,
grounded in real web evidence, with a non-trivial software substrate
(orchestration, resilience, cost control) that demonstrates professional
engineering — not a toy script that prints canned text.

### 1.2 Market / situational analysis
This mirrors real "agentic" systems (orchestrator + workers + tools + guardrails)
and the course's central thesis: the value is the **harness around the LLM**
(orchestration, context engineering, gatekeeping, observability), not the model.

### 1.3 Target audience
Course grader (primary), future maintainers/extenders (secondary).

---

## 2. Goals, KPIs & Acceptance Criteria

| Goal | KPI | Acceptance criterion |
|------|-----|----------------------|
| Run a full rule-compliant debate | ≥ **10 pings per side** (argument → counter-argument) | A complete transcript with ≥10 Pro and ≥10 Con turns, each routed through the Father |
| Decisive judgment | **0 ties** | Judge always returns a single winner + differential score (e.g. 80/70) + justification |
| Resilience | **100% graceful recovery** | Watchdog detects a hung/dead agent, kills & **restarts** it, debate continues or concludes cleanly |
| Grounding | **100% of argument turns carry ≥1 real web citation** | Each `argument`/`rebuttal` JSON includes a non-empty, real `sources[]` from the web-search tool |
| Quality gate | **0 Ruff violations**, **≥85% test coverage** | `uv run ruff check` clean; `uv run pytest --cov` ≥ 85% (branch + path on critical paths) |
| Cost awareness | Full token/cost accounting | README cost table (tokens in/out, $/M, per model) + Gatekeeper-enforced budget cap |
| Professional envelope | All §17 final-checklist items present | SDK, Gatekeeper, versioning, FIFO logs, diagrams, Prompt Book all delivered |

> **Budget exception (allowed):** pings may be reduced from 10 → 5 if API budget
> is constrained; this **must** be stated explicitly in the README (Ex §8.7).

---

## 3. Functional Requirements

- **FR-1 Hierarchy.** Father → Debater-Pro, Father → Debater-Con. **No direct
  child↔child communication.** Every message is `child → father → child`.
- **FR-2 Genuine opposition.** Each debater runs a *distinct persona/skill* and a
  system contract that forbids capitulation. If a debater is "swept" toward the
  opponent, the **Father intervenes and re-asserts its role** (Ex §9).
- **FR-3 Mutual reference.** Each rebuttal MUST address the opponent's specific
  prior argument. Enforced via a required `responding_to` field in the schema —
  no parallel monologues (Ex §8.3.4).
- **FR-4 Web grounding (mandatory).** Debaters call a **real web-search tool**;
  arguments cite real sources. No fabricated citations (Ex §8.3.5).
- **FR-5 Structured IPC.** All inter-agent messages are **strict JSON**, schema-
  validated, separating reasoning from output, and logged (Ex §8.3.8).
- **FR-6 Judge.** After the debate, the Father judges on **persuasion ability
  only** — it is **blind to the topic's factual truth** ("the truth is a lie"
  game, Ex §9). **Lies are allowed**; the opponent is expected to catch them.
  Output: winner + per-side score + written justification. **Never a tie.**
- **FR-7 Real LLM.** The debate content is produced by a real LLM, driven by
  **Python** — not hardcoded text, not "Claude-CLI-only" (Ex §8.4).
- **FR-8 Configurable topic & rounds.** Topic, ping count, models, timeouts,
  budgets — all from `config/`, never hardcoded.

### 3.1 Non-functional requirements
- **NFR-1 Resilience:** timeouts on every agent call; watchdog keep-alive.
- **NFR-2 Performance/cost:** token & $ accounting; rate-limited, queued API.
- **NFR-3 Security:** no secrets in Git; `.env.example` only.
- **NFR-4 Quality:** OOP, no duplication, ≤150 LOC/file, Ruff-clean, ≥85% cov.
- **NFR-5 Usability:** terminal **menu** (keyboard) + SDK entry point; readable
  transcripts (English/Hebrew).
- **NFR-6 Extensibility:** new stance, new search provider, new model — added
  without touching the core (plugin-style seams).

### 3.2 User stories
- *As a grader*, I can run one command, pick "Run debate" from a terminal menu,
  and watch a color-coded, rule-compliant debate end in a justified verdict.
- *As a grader*, I can run the same debate through the **SDK** (no UI) for
  scripted/automated checking.
- *As a maintainer*, I can swap the search provider or add a third stance via a
  documented extension point without editing the orchestrator.

---

## 4. Assumptions, Dependencies, Constraints, Out-of-Scope

**Assumptions:** API access to an LLM provider and a web-search API; grader has
`uv` installed.
**Dependencies:** LLM SDK (Anthropic), web-search API (Tavily/DuckDuckGo),
`rich`, `pydantic`, `pytest`, `ruff`, `python-dotenv`.
**Constraints:** ≤150 LOC/file; 0 Ruff violations; ≥85% coverage; no hardcoded
config; secrets only via `.env`; `uv` as the *only* package manager.
**Out of scope:** web GUI, persistence DB, multi-topic tournaments,
authentication. (Listed as extension points, not delivered — see PLAN §Extensibility.)

---

## 5. Timeline & Milestones (see TODO.md for task-level detail)

| Phase | Deliverable | Done when |
|-------|-------------|-----------|
| P0 Planning | PRD, PLAN, TODO, per-mechanism PRDs, PROMPTS | Docs approved before any code |
| P1 Core utils | config, version, gatekeeper, FIFO logging, watchdog (+ tests) | Unit tests green, ≥85% on these modules |
| P2 Agents & tool | BaseAgent, Debater, Moderator, WebSearch (+ tests, mocks) | Mocked debate round passes |
| P3 Orchestration | multiprocessing orchestrator + IPC + SDK | Full debate runs end-to-end via SDK |
| P4 UX | terminal menu, rich rendering, transcript export | Grader can drive everything from the menu |
| P5 Delivery | README (manual + transcript + cost table), diagrams, self-grade | Final checklist (Guide §17) fully ticked |

---

## 6. Risks
- **R-1 Agents agree** → mitigations FR-2/FR-6 (distinct skills + Father intervention).
- **R-2 Cost overrun** → Gatekeeper hard budget cap (PRD_gatekeeper.md).
- **R-3 Hung LLM/search call** → timeouts + Watchdog restart (PRD_watchdog.md).
- **R-4 Self-grade penalty (HW1 lesson)** → honest self-grade ~88–90 + candid
  "Known Limitations" in README. **Do not inflate** (see PROMPTS.md decision log).

---

## 7. Linked specification documents
- [PRD_debate_orchestration.md](PRD_debate_orchestration.md) — turn loop, state, IPC
- [PRD_judge_scoring.md](PRD_judge_scoring.md) — blind, no-tie persuasion scoring
- [PRD_watchdog.md](PRD_watchdog.md) — keep-alive, timeout, kill & restart
- [PRD_gatekeeper.md](PRD_gatekeeper.md) — rate limit, queue, budget cap
- [PRD_web_search.md](PRD_web_search.md) — grounding tool + citation contract
