# PRD — Judge / Scoring Mechanism (Father as judge)

> Version 1.00 · Parent: [PRD.md](PRD.md)

## 1. Description & theory
The Father judges **persuasion ability only**, deliberately **blind to the
topic's factual truth** — the course's "the truth is a lie" TV-game framing
(the assignment brief). A judge who "knows the right answer" would be biased; withholding the
domain truth keeps scoring on rhetoric, evidence use, and rebuttal quality.

## 2. Specific requirements
- **No tie, ever** (the assignment brief). Output a single `winner` and a **differential
  score** (e.g. `pro: 80, con: 70`). Equal scores are forbidden by construction.
- Judge prompt receives **only**: the rules, the scoring rubric, and the
  transcript — never a "correct side."
- **Lies are allowed in the debate**; the judge rewards the opponent for catching
  them and penalizes uncaught fabrication only insofar as it affects persuasion.
- Produce a written `justification` citing specific turns.

## 3. Scoring rubric (each 0–25, summed to 0–100 per side)
| Dimension | What it measures |
|-----------|------------------|
| Persuasiveness | Rhetorical force, clarity, structure |
| Evidence use | Quality/relevance of cited sources |
| Rebuttal quality | Directly engaging & dismantling the opponent |
| Consistency | Holding the stance without capitulating |

## 4. Capitulation signal (consumed by orchestrator)
Judge/Father exposes `detect_capitulation(turn, stance) -> bool` used live during
the debate (not only at the end): flags a turn whose net position agrees with the
opponent. Drives `intervene()` (the assignment brief: Father must re-assert the role).

## 5. Input / output
- **Input:** `transcript: list[Message]`, `rules`, `rubric` (from config).
- **Output:** `Verdict{winner: "pro"|"con", scores: {pro:int, con:int},
  justification: str}` with `scores.pro != scores.con`.

## 6. Constraints & alternatives
- *Alt: numeric auto-scoring from heuristics only* — rejected: assignment requires
  a real LLM judgment of persuasion, not a Python formula (the assignment brief).
- Tie-break rule if the model returns equal scores: deterministically subtract 1
  from the side with fewer total citations; if still equal, from the side with
  the later final turn. Guarantees a decision.

## 7. Success criteria & edge cases
- Equal raw scores → tie-break applied → distinct scores returned.
- Empty/curtailed transcript (early conclusion) → still returns a verdict.
- Judge never references external truth in `justification` (asserted by a test
  scanning for forbidden "the correct answer is" patterns in the prompt).
