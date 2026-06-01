"""Reporting: cost aggregation + transcript formatting/export.

Cost is aggregated from each turn's `tokens` field, which travels back from the
debater processes through the IPC queue — so cost is visible in the main process
even though each worker has its own gatekeeper. Pure logic, fully testable.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CostEstimate:
    """Aggregated token/cost figures for a debate."""

    input_tokens: int
    output_tokens: int
    cost_usd: float


def aggregate_tokens(transcript: list[dict[str, Any]]) -> tuple[int, int]:
    """Sum prompt/completion tokens across all turns."""
    total_in = total_out = 0
    for turn in transcript:
        tokens = turn.get("tokens") or {}
        total_in += tokens.get("prompt", 0)
        total_out += tokens.get("completion", 0)
    return total_in, total_out


def estimate_cost(transcript: list[dict[str, Any]], price_in_per_m: float,
                  price_out_per_m: float) -> CostEstimate:
    """Estimate USD cost from transcript tokens and per-million prices."""
    total_in, total_out = aggregate_tokens(transcript)
    cost = total_in / 1_000_000 * price_in_per_m + total_out / 1_000_000 * price_out_per_m
    return CostEstimate(total_in, total_out, round(cost, 6))


def format_transcript(topic: str, transcript: list[dict[str, Any]], verdict: Any = None) -> str:
    """Render a human-readable transcript (English/whatever language the debate used)."""
    lines = [f"TOPIC: {topic}", "=" * 60]
    for turn in transcript:
        stance = turn.get("stance", "?").upper()
        lines.append(f"[{stance} {turn.get('turn_id', '?')}] ({turn.get('type', '?')})")
        lines.append(turn.get("claim", ""))
        for source in turn.get("sources", []):
            lines.append(f"   - {source.get('title', '')} {source.get('url', '')}")
        lines.append("")
    if verdict is not None:
        lines += ["=" * 60, f"VERDICT: winner={verdict.winner.value} scores={verdict.scores}",
                  verdict.justification]
    return "\n".join(lines)


def export_transcript(out_dir: str | Path, topic: str, transcript: list[dict[str, Any]],
                      verdict: Any = None) -> Path:
    """Write the transcript as both readable text and structured JSON; return the text path."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    text_path = out / "transcript.txt"
    text_path.write_text(format_transcript(topic, transcript, verdict), encoding="utf-8")
    payload: dict[str, Any] = {"topic": topic, "transcript": transcript}
    if verdict is not None:
        payload["verdict"] = {"winner": verdict.winner.value, "scores": verdict.scores,
                              "justification": verdict.justification}
    (out / "transcript.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return text_path
