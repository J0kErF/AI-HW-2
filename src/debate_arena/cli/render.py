"""Rich rendering of debate events (visual I/O — omitted from coverage).

Produces an `on_event` callback the orchestrator calls for each turn, giving the
grader a live, color-coded debate where Father / Pro / Con / Watchdog / System
messages are visually distinct (Ex §8.7, Guide §10).
"""

from typing import Any

from rich.console import Console
from rich.panel import Panel

_STYLE = {
    "pro": "bold green", "con": "bold red", "intervention": "bold yellow",
    "system": "bold magenta", "validation": "dim yellow", "moderation": "cyan",
}


def make_event_renderer(console: Console | None = None) -> Any:  # pragma: no cover
    """Return an on_event(event) callback that prints a styled panel per event."""
    out = console or Console()

    def on_event(event: dict[str, Any]) -> None:
        etype = event.get("type", "")
        stance = event.get("stance", "")
        style = _STYLE.get(etype if etype in _STYLE else stance, "white")
        title = (stance or etype or "event").upper()
        body = event.get("claim") or event.get("reason") or str(
            event.get("issues") or event
        )
        sources = event.get("sources") or []
        if sources:
            body += "\n\nsources:\n" + "\n".join(
                f"  - {s.get('title', '')} {s.get('url', '')}" for s in sources
            )
        out.print(Panel(str(body), title=title, border_style=style))

    return on_event
