# debate_arena — Autonomous AI Agent Debate System

> HW2 · Exercise 02 (AI Agent Debate) · Course: Building with LLMs (Dr. Yoram Segal)
> Status: **Phase 0 complete (planning + scaffold)** — implementation in progress.

Two LLM **debater** sub-agents argue opposing sides of a configurable motion,
each grounded in **real web search**. A third **Moderator ("Father")** agent
orchestrates every turn (`child → father → child`), enforces the rules, and acts
as a **blind, no-tie persuasion judge**. The system runs the debaters as separate
processes with real IPC, supervised by a **Watchdog** (keep-alive + kill/restart),
with all API traffic routed through a budget-enforcing **Gatekeeper**.

---

## 1. Installation
```bash
git clone <repo-url>
cd aihw2
uv sync                      # creates the venv and installs from uv.lock
cp .env.example .env         # then fill in your API keys (never committed)
```

## 2. Usage
```bash
# Interactive terminal menu (keyboard-driven)
uv run python src/main.py

# Or drive it programmatically through the SDK (no UI)
uv run python -c "from debate_arena.sdk import DebateSDK; print(DebateSDK().run_debate())"

# Quality gates
uv run ruff check
uv run pytest --cov=src
```

Configuration lives in `config/` (`setup.json`, `rate_limits.json`,
`logging_config.json`). **No tunable value is hardcoded** — edit config, not code.
Topic, pings-per-side, models, timeouts, and budget are all set there.

## 3. Architecture (summary)
All logic is reachable only through the **`DebateSDK`** facade. See
[docs/PLAN.md](docs/PLAN.md) for C4, UML class, and sequence diagrams, and the
per-mechanism specs in `docs/PRD_*.md`.

```
Grader ── menu / SDK ──> DebateSDK ──> Orchestrator ──> Father(Moderator)
                                          │                 ├── Pro (process)
                                          │                 └── Con (process)
                         Watchdog ◀───────┘   WebSearch ──> Gatekeeper ──> APIs
```

## 4. Documentation map
- [docs/PRD.md](docs/PRD.md) — requirements, KPIs, debate rules
- [docs/PLAN.md](docs/PLAN.md) — architecture, diagrams, ADRs
- [docs/TODO.md](docs/TODO.md) — phased task tracking
- [docs/PRD_debate_orchestration.md](docs/PRD_debate_orchestration.md),
  [PRD_judge_scoring.md](docs/PRD_judge_scoring.md),
  [PRD_watchdog.md](docs/PRD_watchdog.md),
  [PRD_gatekeeper.md](docs/PRD_gatekeeper.md),
  [PRD_web_search.md](docs/PRD_web_search.md)
- [docs/PROMPTS.md](docs/PROMPTS.md) — Prompt Book / AI-assisted dev log

## 5. Configuration guide
| File | Controls |
|------|----------|
| `config/setup.json` | topic, pings/side (**5**), personas, models (free-tier `gemini-2.5-flash`), search provider (**duckduckgo**, keyless), timeouts, watchdog |
| `config/rate_limits.json` | per-service rate limits + budget cap + pricing |
| `config/logging_config.json` | FIFO log rotation (max files × max lines) |

> Search defaults to **keyless DuckDuckGo** (`ddgs`) — no Tavily key needed. To use
> Tavily instead, set `search.provider` to `tavily` and add `TAVILY_API_KEY` to `.env`.

## 6. Cost analysis
Runs on the **free Google AI (Gemini) tier** with `gemini-2.5-flash` for both
debaters and the moderator (the free tier grants **0 quota for `gemini-2.5-pro`**).
Web search uses **keyless DuckDuckGo** (`ddgs`), so **no Tavily key is required**.

> **Budget note (required by Ex §8.7):** pings are set to **5 per side** (reduced
> from 10) to fit the free tier. This is explicitly permitted and not penalized.
> Cost is aggregated from each turn's token usage (see `get_cost_report`).

| Model | Input tokens | Output tokens | Total cost |
|-------|-------------:|--------------:|-----------:|
| _filled after the captured full run_ | _tbd_ | _tbd_ | _tbd_ |

## 7. Session transcripts & screenshots
_Embedded after the first full run (Phase 4/5): full debate transcript +
terminal screenshots of the menu, a live debate, and watchdog recovery._

## 8. UI/UX notes
The terminal menu is evaluated against Nielsen's usability heuristics
(visibility of status, error prevention, consistency); see docs as it lands.

## 9. Known limitations
_Maintained honestly for an accurate self-assessment (HW1 lesson). To be
completed at submission; current state: planning + scaffold only._

## 10. Contributing & quality standards
Ruff-clean (`select = E,F,W,I,N,UP,B,C4,SIM`), files ≤150 LOC, ≥85% coverage,
TDD (red→green→refactor), `uv` only. See `pyproject.toml`.

## 11. License & credits
MIT. Authors: **TODO (name + ID)**, partner **TODO (name + ID)**.
Group code: **moamteam**. Submission PDF: `moamteam-ex02.pdf` (official template).
Repo shared with the lecturer (rmisegal@gmail.com); each partner submits on Moodle.
