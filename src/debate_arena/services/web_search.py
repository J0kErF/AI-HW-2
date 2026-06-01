"""Web search tool — mandatory grounding (Ex §8.3.5; docs/PRD_web_search.md).

Pluggable provider behind one interface; all calls route through the gatekeeper;
graceful degradation on failure (empty list + degraded flag).

NOTE: scaffold stub — provider wiring lands in Phase 2.
"""

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
    Setup:  gatekeeper, provider name, and search config.
    """

    def __init__(self, gatekeeper: Any, provider: str, config: dict[str, Any]) -> None:
        self._gatekeeper = gatekeeper
        self._provider = provider
        self._config = config
        self.degraded = False

    def search(self, query: str, k: int = 3) -> list[Source]:
        """Search the web for `query`, returning up to `k` normalized sources."""
        if not query or not query.strip():
            return []
        raise NotImplementedError("Phase 2: call provider via gatekeeper, normalize, degrade")
