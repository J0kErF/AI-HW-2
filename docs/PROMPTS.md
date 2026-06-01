# Prompt Engineering Log / Prompt Book — debate_arena

> Version 1.00 · Mandatory deliverable (Guide §8.3). This is a **living document**:
> record the meaningful prompts used to build the project, the context/goal of
> each, sample outputs, iterative refinements, and recommended practices learned.
> It directly addresses HW1 feedback ("Version Management": AI-assisted workflow
> and reasoning must be visible).

---

## How to use this log
For each significant AI-assisted step, add an entry with:
`Date · Goal · Prompt (verbatim) · Output summary · Decision/refinement`.

---

## D0 — Project framing & rubric validation
- **Goal:** Validate the HW2 strategy against the official rubric + HW1 feedback
  *before* writing code.
- **Prompt (summary):** "Deeply understand this folder; validate the proposed
  PRD/PLAN/TODO against the H standards and the HW1 feedback."
- **Output summary:** Identified that grading is driven by
  `software_submission_guidelines-V3.pdf`; found ~13 mandatory gaps (SDK,
  Gatekeeper, FIFO logs, terminal menu, watchdog restart, multiprocessing/IPC,
  per-mechanism PRDs, diagrams, Prompt Book, versioning, cost table,
  extensibility) and the debate-specific rules (≥10 pings/side, no tie, blind
  judge, anti-capitulation, mutual reference, real LLM).
- **Decision:** Adopt the official recommended tree; write docs first (Guide §2.5).

## D1 — Self-grade calibration (HW1 lesson)
- **Goal:** Avoid repeating HW1's self-grading penalty.
- **Evidence:** HW1 self-graded 98/100 @ strictness 0.95 → triggered rigorous
  scrutiny → 69.19 pre-bonus. `submit.txt §5` + feedback p.2 confirm the mechanic.
- **Decision:** Target an **honest ~88–90** with a candid "Known Limitations"
  section in the README. Do **not** inflate.

---

## Agent system prompts (to be finalized in Phase 2)

### Debater (Pro/Con) — contract sketch
> You are the **{stance}** debater. You must argue **only** the {stance} side of:
> "{topic}". You may never concede the opponent's position. Every `argument`/
> `rebuttal` must (a) cite ≥1 real source returned by the search tool, (b) set
> `responding_to` to the opponent's latest `turn_id`, (c) return strict JSON
> matching the schema. Rhetoric and selective framing are allowed; outright
> capitulation is not.

### Father (moderator) — routing
> You orchestrate turns; you never argue. Validate each child message, enforce
> citation + `responding_to` + non-capitulation; if a debater concedes, issue an
> `intervention` re-asserting its role.

### Father (judge) — blind, no tie
> You judge **persuasion only**. You are **not told** which side is factually
> correct and must not assume one. Score each side 0–100 across the rubric;
> **scores must differ** (no ties); name a single winner; justify by citing
> specific turn_ids.

---

## Refinement notes (append as the build proceeds)
- _(placeholder)_ Tightened the debater prompt after early runs showed agents
  drifting to agreement — added explicit non-capitulation + Father intervention.
