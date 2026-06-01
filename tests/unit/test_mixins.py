"""Isolated tests for the single-concern agent mixins (Guide §4.2)."""

import pytest

from debate_arena.services.mixins import JsonContractMixin, TokenAccountingMixin


def test_parse_json_valid_object() -> None:
    assert JsonContractMixin.parse_json('{"a": 1}') == {"a": 1}


def test_parse_json_strips_markdown_fences() -> None:
    assert JsonContractMixin.parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert JsonContractMixin.parse_json('```\n{"b": 2}\n```') == {"b": 2}


def test_parse_json_malformed_raises() -> None:
    with pytest.raises(ValueError):
        JsonContractMixin.parse_json("{not json}")


def test_parse_json_non_object_raises() -> None:
    with pytest.raises(ValueError):
        JsonContractMixin.parse_json("[1, 2, 3]")


class _Accounted(TokenAccountingMixin):
    """Minimal concrete user of the accounting mixin."""


def test_token_accounting_accumulates() -> None:
    acc = _Accounted()
    acc.record_tokens(10, 5)
    acc.record_tokens(1, 2)
    assert acc.token_totals == {"prompt": 11, "completion": 7}
