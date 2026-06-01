"""Tests for the version compatibility check (Guide §8.1)."""

from debate_arena.shared.version import (
    EXPECTED_CONFIG_VERSION,
    __version__,
    is_compatible,
)


def test_code_version_is_set() -> None:
    assert __version__ == "1.00"


def test_matching_config_version_is_compatible() -> None:
    assert is_compatible(EXPECTED_CONFIG_VERSION) is True


def test_mismatched_config_version_is_incompatible() -> None:
    assert is_compatible("0.99") is False
