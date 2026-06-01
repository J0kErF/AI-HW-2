"""Built-in FIFO log rotation (Ex §8.6, Guide §7.3).

Rotates the log every `max_lines_per_file` lines, keeping at most `max_files`
files (oldest evicted first — FIFO). Configuration comes from
config/logging_config.json. Optionally mirrors to a (rich) console.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


class LineRotatingFileHandler(RotatingFileHandler):
    """RotatingFileHandler that rolls over by line count instead of bytes."""

    def __init__(self, filename: str, max_lines: int, max_files: int,
                 encoding: str = "utf-8") -> None:
        super().__init__(filename, mode="a", maxBytes=0,
                         backupCount=max(max_files - 1, 0), encoding=encoding)
        self._max_lines = max_lines
        self._lines = self._count_lines(filename)

    @staticmethod
    def _count_lines(filename: str) -> int:
        path = Path(filename)
        if not path.exists():
            return 0
        with path.open(encoding="utf-8") as handle:
            return sum(1 for _ in handle)

    def shouldRollover(self, record: logging.LogRecord) -> bool:  # noqa: N802 (stdlib override)
        if self._max_lines <= 0:
            return False
        if self._lines >= self._max_lines:
            return True
        self._lines += 1
        return False

    def doRollover(self) -> None:  # noqa: N802 (stdlib override)
        super().doRollover()
        self._lines = 1


def _console_handler(console: dict[str, Any]) -> logging.Handler:
    if console.get("rich"):
        from rich.logging import RichHandler

        return RichHandler()
    return logging.StreamHandler()


def build_logger(name: str, logging_config: dict[str, Any]) -> logging.Logger:
    """Build a logger with FIFO file rotation + optional console.

    Input:  logger name, parsed logging_config.json.
    Output: a configured `logging.Logger` (idempotent per name).
    Setup:  max_files / max_lines_per_file / log_dir come from config.
    """
    fifo = logging_config["fifo"]
    log_dir = Path(logging_config["log_dir"])
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging_config.get("level", "INFO"))
    logger.propagate = False
    if logger.handlers:  # idempotent: don't stack duplicate handlers
        return logger
    file_handler = LineRotatingFileHandler(
        str(log_dir / f"{fifo['base_name']}.log"),
        fifo["max_lines_per_file"], fifo["max_files"],
    )
    file_handler.setFormatter(logging.Formatter(_FORMAT))
    logger.addHandler(file_handler)
    if logging_config.get("console", {}).get("enabled"):
        logger.addHandler(_console_handler(logging_config["console"]))
    return logger
