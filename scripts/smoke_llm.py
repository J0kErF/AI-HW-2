"""Provider-agnostic LLM smoke test: verify the configured provider works.

Run with: uv run python scripts/smoke_llm.py
"""

from debate_arena.services.llm_client import build_llm_client
from debate_arena.shared.config import ConfigManager
from debate_arena.shared.env import load_env
from debate_arena.shared.gatekeeper import ApiGatekeeper


def main() -> None:
    load_env()
    cfg = ConfigManager("config")
    rate = cfg.load("rate_limits")
    gk = ApiGatekeeper(rate, rate["budget"])
    client = build_llm_client(gk, cfg)
    model = cfg.get("setup", "models", "debater")
    text, (in_tok, out_tok) = client.complete(model, "Reply with exactly: debate_arena online.")
    print(f"provider : {cfg.get('setup', 'provider')}")
    print(f"model    : {model}")
    print(f"response : {text.strip()[:200]}")
    print(f"tokens   : in={in_tok} out={out_tok}")


if __name__ == "__main__":
    main()
