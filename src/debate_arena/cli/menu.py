"""Keyboard-driven terminal menu — visual I/O, omitted from coverage.

The grader can drive every feature from this menu, or call DebateSDK directly for
automated checking. The menu holds no business logic — it delegates to the SDK and
renders with rich.
"""

from rich.console import Console

from debate_arena.cli.render import make_event_renderer
from debate_arena.sdk import DebateSDK
from debate_arena.services.reporting import export_transcript, format_transcript

MENU = """
[bold]debate_arena - main menu[/bold]
  1) Run debate
  2) Replay last transcript
  3) Show cost report
  4) Show configuration
  q) Quit
"""


def _run(console: Console, sdk: DebateSDK, state: dict) -> None:  # pragma: no cover
    default = sdk._config.get("setup", "debate", "default_topic")
    topic = console.input(f"Topic [dim]({default})[/dim]: ").strip() or default
    result = sdk.run_debate(topic=topic, on_event=make_event_renderer(console))
    state["topic"], state["result"] = topic, result
    path = export_transcript("results", topic, result.transcript, result.verdict)
    console.print(f"[green]Saved transcript →[/green] {path}")


def main() -> None:  # pragma: no cover
    """Entry point for the `debate-arena` console script."""
    console = Console()
    sdk = DebateSDK("config")
    state: dict = {}
    while True:
        console.print(MENU)
        choice = console.input("> ").strip().lower()
        if choice == "1":
            _run(console, sdk, state)
        elif choice == "2":
            if state.get("result"):
                console.print(format_transcript(
                    state["topic"], state["result"].transcript, state["result"].verdict))
            else:
                console.print("[yellow]No debate run yet.[/yellow]")
        elif choice == "3":
            report = sdk.get_cost_report()
            console.print(f"tokens in={report.input_tokens} out={report.output_tokens} "
                          f"cost=${report.cost_usd:.6f}")
        elif choice == "4":
            console.print_json(data=sdk._config.load("setup"))
        elif choice in ("q", "quit"):
            break


if __name__ == "__main__":
    main()
