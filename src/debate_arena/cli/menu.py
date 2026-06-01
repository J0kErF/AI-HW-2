"""Keyboard-driven terminal menu (Ex §8.6/§8.7).

The grader can drive every feature from this menu, or call the SDK directly for
automated checking. The menu contains no business logic — it delegates to
DebateSDK and renders with rich.

NOTE: scaffold stub — rendering/loop lands in Phase 4.
"""

from debate_arena.sdk import DebateSDK

MENU = """
debate_arena — main menu
  [1] Run debate
  [2] Replay last transcript
  [3] Show cost report
  [4] Show / reload configuration
  [q] Quit
"""


def main() -> None:
    """Entry point for the `debate-arena` console script."""
    _ = DebateSDK  # wired in Phase 4
    raise NotImplementedError("Phase 4: render MENU, read keys, dispatch to SDK")


if __name__ == "__main__":
    main()
