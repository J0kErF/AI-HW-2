"""Tests for the web-search grounding tool (mocked provider + gatekeeper)."""

from debate_arena.services.web_search import Source, WebSearchTool


class RecordingGatekeeper:
    """Fake gatekeeper that records the service and runs the call."""

    def __init__(self) -> None:
        self.services: list[str] = []

    def execute(self, call, *args, service="default", **kwargs):
        self.services.append(service)
        return call()


def _provider(results):
    def fn(_query, _k):
        return results

    return fn


def test_normal_query_returns_normalized_sources() -> None:
    gk = RecordingGatekeeper()
    raw = [{"title": "T", "url": "https://x", "content": "snip"}]
    tool = WebSearchTool(gk, _provider(raw))
    out = tool.search("nuclear energy")
    assert out == [Source(title="T", url="https://x", snippet="snip")]
    assert tool.degraded is False


def test_empty_query_skips_call() -> None:
    gk = RecordingGatekeeper()
    tool = WebSearchTool(gk, _provider([{"title": "x"}]))
    assert tool.search("   ") == []
    assert gk.services == []  # no API call made


def test_provider_failure_degrades_gracefully() -> None:
    def boom(_q, _k):
        raise TimeoutError("provider down")

    tool = WebSearchTool(RecordingGatekeeper(), boom)
    assert tool.search("query") == []
    assert tool.degraded is True


def test_search_routes_through_gatekeeper_service() -> None:
    gk = RecordingGatekeeper()
    tool = WebSearchTool(gk, _provider([]))
    tool.search("query")
    assert gk.services == ["search"]


def test_result_count_is_capped() -> None:
    gk = RecordingGatekeeper()
    raw = [{"title": str(i), "url": "u", "content": "c"} for i in range(10)]
    tool = WebSearchTool(gk, _provider(raw), k_default=3)
    assert len(tool.search("query")) == 3
