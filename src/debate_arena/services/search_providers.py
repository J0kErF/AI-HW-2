"""Concrete web-search providers (Tavily + DuckDuckGo).

Each provider is a `(query, k) -> list[dict]` callable returning raw results that
WebSearchTool normalizes. Selection is config-driven. Integration glue, exercised
by the live run rather than unit tests.
"""

import os
from collections.abc import Callable
from typing import Any


def duckduckgo_provider(query: str, k: int) -> list[dict]:  # pragma: no cover
    """Keyless DuckDuckGo text search (via the `ddgs` package)."""
    from ddgs import DDGS

    with DDGS() as ddgs:
        return [
            {"title": r.get("title"), "url": r.get("href"), "content": r.get("body")}
            for r in ddgs.text(query, max_results=k)
        ]


def tavily_provider_factory(api_key: str) -> Callable[[str, int], list[dict]]:  # pragma: no cover
    """Build a Tavily-backed provider bound to an API key."""
    from tavily import TavilyClient

    client = TavilyClient(api_key)

    def provider(query: str, k: int) -> list[dict]:
        res = client.search(query, max_results=k)
        return [
            {"title": r.get("title"), "url": r.get("url"), "content": r.get("content", "")}
            for r in res.get("results", [])
        ]

    return provider


def build_provider(config: Any) -> Callable[[str, int], list[dict]]:  # pragma: no cover
    """Pick a provider from config; fall back to keyless DuckDuckGo."""
    name = config.get("setup", "search", "provider")
    tavily_key = os.environ.get("TAVILY_API_KEY")
    if name == "tavily" and tavily_key:
        return tavily_provider_factory(tavily_key)
    return duckduckgo_provider
