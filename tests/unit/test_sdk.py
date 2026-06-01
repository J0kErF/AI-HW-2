"""Tests for the DebateSDK facade with injected father + handles (offline)."""

from debate_arena.constants import Stance
from debate_arena.sdk import DebateSDK
from debate_arena.services.moderator import Verdict
from tests.unit.test_orchestrator import FakeFather, FakeHandle


def test_run_debate_offline_via_injection() -> None:
    sdk = DebateSDK("config")
    handles = {"pro": FakeHandle("pro"), "con": FakeHandle("con")}
    result = sdk.run_debate(
        topic="Topic", rounds=1, make_handle=lambda s: handles[s], father=FakeFather()
    )
    assert isinstance(result.verdict, Verdict)
    assert result.verdict.winner is Stance.PRO
    assert sdk.get_transcript() == result.transcript


def test_cost_report_available() -> None:
    sdk = DebateSDK("config")
    report = sdk.get_cost_report()
    assert report.cost_usd == 0.0  # no calls made yet


def test_cost_aggregated_from_transcript_tokens() -> None:
    sdk = DebateSDK("config")
    handles = {"pro": FakeHandle("pro"), "con": FakeHandle("con")}
    sdk.run_debate(rounds=2, make_handle=lambda s: handles[s], father=FakeFather())
    report = sdk.get_cost_report()
    assert report.input_tokens == 4 * 5  # 4 turns x 5 prompt tokens
    assert report.output_tokens == 4 * 7
    assert report.cost_usd > 0  # priced from config


def test_defaults_pulled_from_config() -> None:
    sdk = DebateSDK("config")
    handles = {"pro": FakeHandle("pro"), "con": FakeHandle("con")}
    result = sdk.run_debate(make_handle=lambda s: handles[s], father=FakeFather())
    # default pings_per_side is 10 -> 20 turns
    assert len(result.transcript) == 20
