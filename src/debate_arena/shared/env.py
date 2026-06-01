"""Environment / secrets bootstrap.

Loads the git-ignored `.env` file so secrets are available via os.environ.
Secrets are never read from anywhere else (Guide §7.4).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[3]


def load_env(dotenv_path: str | Path | None = None) -> None:
    """Load `.env` (repo root by default) into the process environment."""
    path = Path(dotenv_path) if dotenv_path else _REPO_ROOT / ".env"
    load_dotenv(path, override=False)


def gemini_api_key() -> str:
    """Return the Gemini API key from the environment, or raise if absent."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set in .env")
    return key


def use_vertex() -> bool:
    """True if the SDK should route through Vertex AI instead of the dev API."""
    return os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"
