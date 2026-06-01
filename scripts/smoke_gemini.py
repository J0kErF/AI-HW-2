"""Manual smoke test: verify the Gemini API key works end-to-end.

Run with: uv run python scripts/smoke_gemini.py
Not part of the test suite (it makes a real, billable API call).
"""

from debate_arena.services.llm_client import GeminiClient
from debate_arena.shared.config import ConfigManager
from debate_arena.shared.env import gemini_api_key, load_env
from debate_arena.shared.gatekeeper import ApiGatekeeper


def main() -> None:
    load_env()
    cfg = ConfigManager("config")
    rate = cfg.load("rate_limits")
    gk = ApiGatekeeper(rate, rate["budget"])
    client = GeminiClient(gk, gemini_api_key())
    model = cfg.get("setup", "models", "debater")
    text, (in_tok, out_tok) = client.complete(
        model, "Reply with exactly: debate_arena online."
    )
    print(f"model     : {model}")
    print(f"response  : {text.strip()}")
    print(f"tokens    : in={in_tok} out={out_tok}")
    print(f"cost_usd  : {gk.get_cost_report().cost_usd:.6f}")


if __name__ == "__main__":
    main()
