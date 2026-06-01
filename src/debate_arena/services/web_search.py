"""Web search tool — mandatory grounding (Ex §8.3.5; docs/PRD_web_search.md).

Provider-agnostic: a `provider(query, k) -> list[dict]` callable is injected and
wrapped by the gatekeeper. Results are normalized to `Source`; any provider
failure degrades gracefully (empty list + `degraded` flag) so the orchestrator
can reject an unsupported argument and re-request.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Source:
    """A normalized web-search result used as a debate citation."""

    title: str
    url: str
    snippet: str


class WebSearchTool:
    """Grounding tool.

    Input:  a query string and result count k.
    Output: a list[Source] (possibly empty when degraded).
    Setup:  gatekeeper, a provider callable, and a default result count.
    """

    def __init__(self, gatekeeper: Any, provider: Callable[[str, int], list[dict]],
                 k_default: int = 3) -> None:
        self._gk = gatekeeper
        self._provider = provider
        self._k = k_default
        self.degraded = False

    def search(self, query: str, k: int | None = None) -> list[Source]:
        """Search the web for `query`, returning up to `k` normalized sources."""
        if not query or not query.strip():
            return []
        k = k or self._k
        self.degraded = False
        try:
            raw = self._gk.execute(lambda: self._provider(query, k), service="search")
        except Exception:  # any provider failure must degrade gracefully (PRD §6)
            self.degraded = True
            return []
        return [self._normalize(item) for item in (raw or [])][:k]

    @staticmethod
    def _normalize(item: dict[str, Any]) -> Source:
        return Source(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("snippet") or item.get("content", ""),
        )
