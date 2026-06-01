"""Built-in FIFO log rotation (Ex §8.6, Guide §7.3).

Configures a rotating file log: at most `max_files` files, each capped at
`max_lines_per_file` lines, oldest evicted first (FIFO). Config comes from
config/logging_config.json. Optionally mirrors to a rich console.

NOTE: scaffold stub — Phase 1 implements rotation under TDD.
"""

import logging
from typing import Any


def build_logger(name: str, logging_config: dict[str, Any]) -> logging.Logger:
    """Build a logger with FIFO file rotation + optional rich console.

    Input:  logger name, parsed logging_config.json.
    Output: a configured `logging.Logger`.
    Setup:  max_files / max_lines_per_file / log_dir from config.
    """
    raise NotImplementedError("Phase 1: implement line-capped FIFO RotatingFileHandler")
