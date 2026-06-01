"""Immutable project constants (Guide §7.3).

Only physical/mathematical constants, enum-like keys, and structural defaults
live here. Tunable values belong in `config/`, never in source.
"""

from enum import Enum


class Stance(str, Enum):
    """The two debate sides."""

    PRO = "pro"
    CON = "con"


class MessageType(str, Enum):
    """Types of inter-agent messages routed through the Father."""

    ARGUMENT = "argument"
    REBUTTAL = "rebuttal"
    INTERVENTION = "intervention"
    SYSTEM = "system"


# Structural keys for config sections (avoid stringly-typed access scattered in code).
CONFIG_VERSION_KEY = "version"
