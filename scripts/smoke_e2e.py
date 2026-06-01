"""Manual end-to-end smoke test: a real, process-backed debate via Gemini.

Runs a tiny debate (1 ping/side) to verify the whole pipeline: spawned debater
processes, IPC, web search, JSON contract, Father validation + verdict, and cost
accounting. Makes real, billable API calls.

Run with: uv run python scripts/smoke_e2e.py
"""

from debate_arena.sdk import DebateSDK


def main() -> None:
    sdk = DebateSDK("config")
    result = sdk.run_debate(topic="Cats make better pets than dogs", rounds=1)
    print("\n=== TRANSCRIPT ===")
    for turn in result.transcript:
        claim = (turn.get("claim") or "")[:120]
        print(f"[{turn['stance']:>3} {turn.get('turn_id','?')}] {claim}")
        print(f"      sources: {len(turn.get('sources', []))}")
    print("\n=== VERDICT ===")
    v = result.verdict
    print(f"winner={v.winner.value} scores={v.scores}")
    print(f"justification: {v.justification[:200]}")
    print(f"\nrestarts={result.restarts} interventions={len(result.interventions)}")
    print(f"cost_usd={sdk.get_cost_report().cost_usd:.6f}")


if __name__ == "__main__":
    main()
