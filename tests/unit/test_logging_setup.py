"""Tests for FIFO line-rotating logging (Ex §8.6, Guide §7.3)."""

import logging

from debate_arena.shared.logging_setup import build_logger


def _cfg(log_dir, max_files=3, max_lines=5, console=False) -> dict:
    return {
        "version": "1.00",
        "log_dir": str(log_dir),
        "level": "INFO",
        "fifo": {"max_files": max_files, "max_lines_per_file": max_lines, "base_name": "debate"},
        "console": {"enabled": console, "rich": False},
    }


def test_rotates_and_caps_total_files(tmp_path) -> None:
    log = build_logger("t_rotate", _cfg(tmp_path))
    for i in range(100):
        log.info("line %d", i)
    for handler in log.handlers:
        handler.flush()
    files = sorted(tmp_path.glob("debate.log*"))
    assert 1 <= len(files) <= 3  # FIFO: oldest evicted, total bounded


def test_rotated_files_respect_line_cap(tmp_path) -> None:
    log = build_logger("t_cap", _cfg(tmp_path, max_lines=5))
    for i in range(60):
        log.info("line %d", i)
    for handler in log.handlers:
        handler.flush()
    for f in tmp_path.glob("debate.log*"):
        assert sum(1 for _ in f.open(encoding="utf-8")) <= 5


def test_creates_missing_log_dir(tmp_path) -> None:
    sub = tmp_path / "nested" / "logs"
    log = build_logger("t_dir", _cfg(sub))
    log.info("hello")
    assert sub.is_dir()


def test_no_duplicate_file_handlers(tmp_path) -> None:
    build_logger("t_dup", _cfg(tmp_path))
    log = build_logger("t_dup", _cfg(tmp_path))
    file_handlers = [h for h in log.handlers if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) == 1
