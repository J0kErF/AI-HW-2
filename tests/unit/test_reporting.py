"""Tests for cost aggregation + transcript formatting/export."""

import json

from debate_arena.constants import Stance
from debate_arena.services.moderator import Verdict
from debate_arena.services.reporting import (
    aggregate_tokens,
    estimate_cost,
    export_transcript,
    format_transcript,
)

_TRANSCRIPT = [
    {"stance": "pro", "turn_id": "pro-1", "type": "argument", "claim": "Nuclear is clean",
     "sources": [{"title": "IAEA", "url": "https://iaea.org"}],
     "tokens": {"prompt": 100, "completion": 40}},
    {"stance": "con", "turn_id": "con-1", "type": "rebuttal", "claim": "Waste is forever",
     "sources": [], "tokens": {"prompt": 50, "completion": 10}},
]
_VERDICT = Verdict(Stance.PRO, {"pro": 80, "con": 70}, "Pro was more persuasive.")


def test_aggregate_tokens_sums_turns() -> None:
    assert aggregate_tokens(_TRANSCRIPT) == (150, 50)


def test_estimate_cost_uses_prices() -> None:
    est = estimate_cost(_TRANSCRIPT, price_in_per_m=10.0, price_out_per_m=20.0)
    assert est.input_tokens == 150
    assert est.cost_usd == round(150 / 1e6 * 10 + 50 / 1e6 * 20, 6)


def test_format_transcript_includes_key_parts() -> None:
    text = format_transcript("Nuclear energy", _TRANSCRIPT, _VERDICT)
    assert "Nuclear energy" in text
    assert "Nuclear is clean" in text
    assert "winner=pro" in text
    assert "https://iaea.org" in text


def test_export_writes_text_and_json(tmp_path) -> None:
    path = export_transcript(tmp_path, "Nuclear energy", _TRANSCRIPT, _VERDICT)
    assert path.exists()
    payload = json.loads((tmp_path / "transcript.json").read_text(encoding="utf-8"))
    assert payload["topic"] == "Nuclear energy"
    assert payload["verdict"]["winner"] == "pro"
    assert len(payload["transcript"]) == 2
