"""Tests for ConfigManager: loading, nested lookup, versioning, edge cases."""

import json

import pytest

from debate_arena.shared.config import ConfigError, ConfigManager


def test_load_real_setup(config: ConfigManager) -> None:
    data = config.load("setup")
    assert data["version"] == "1.00"


def test_nested_get(config: ConfigManager) -> None:
    assert config.get("setup", "debate", "pings_per_side") == 5


def test_get_missing_key_returns_default(config: ConfigManager) -> None:
    assert config.get("setup", "nope", default="fallback") == "fallback"


def test_missing_dir_raises(tmp_path) -> None:
    with pytest.raises(ConfigError):
        ConfigManager(tmp_path / "does-not-exist")


def test_missing_file_raises(config: ConfigManager) -> None:
    with pytest.raises(ConfigError):
        config.load("not_a_real_config")


def test_bad_version_raises(tmp_path) -> None:
    (tmp_path / "setup.json").write_text(json.dumps({"version": "0.1"}), encoding="utf-8")
    with pytest.raises(ConfigError):
        ConfigManager(tmp_path).load("setup")
