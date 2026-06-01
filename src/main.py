"""Thin application entry point — delegates to the CLI menu over the SDK.

No business logic lives here (Guide §4.1): it only wires and launches.
Run with: `uv run python src/main.py`
"""

from debate_arena.cli.menu import main

if __name__ == "__main__":
    main()
