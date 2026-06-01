"""Run a full debate with live rich rendering and export the transcript.

Uses config defaults (topic, pings_per_side=5, free-tier Gemini flash, keyless
DuckDuckGo). Saves results/transcript.{txt,json}. Makes real, billable calls.

Run with: uv run python scripts/run_debate.py
"""

from rich.console import Console

from debate_arena.cli.render import make_event_renderer
from debate_arena.sdk import DebateSDK
from debate_arena.services.reporting import export_transcript


def main() -> None:
    console = Console()
    sdk = DebateSDK("config")
    topic = sdk._config.get("setup", "debate", "default_topic")
    result = sdk.run_debate(topic=topic, on_event=make_event_renderer(console))
    path = export_transcript("results", topic, result.transcript, result.verdict)
    report = sdk.get_cost_report()
    console.rule("[bold]Summary")
    console.print(f"winner={result.verdict.winner.value} scores={result.verdict.scores}")
    console.print(f"restarts={result.restarts} interventions={len(result.interventions)}")
    console.print(f"tokens in/out = {report.input_tokens}/{report.output_tokens} "
                  f"cost=${report.cost_usd:.6f}")
    console.print(f"saved -> {path}")


if __name__ == "__main__":
    main()
