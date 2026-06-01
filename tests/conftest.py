"""Shared pytest fixtures (Guide §6.1)."""

from pathlib import Path

import pytest

from debate_arena.shared.config import ConfigManager

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def config_dir() -> Path:
    """Path to the real project config directory."""
    return REPO_ROOT / "config"


@pytest.fixture
def config(config_dir: Path) -> ConfigManager:
    """A ConfigManager bound to the project config."""
    return ConfigManager(config_dir)
