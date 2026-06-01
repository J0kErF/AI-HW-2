"""Configuration manager (Guide §5.2, §7.2, §8.1).

Loads JSON config files from `config/` and secrets from the environment.
No tunable value is ever hardcoded in source — all reads go through here.
Validates the `version` field of each config against the code version.
"""

import json
import os
from pathlib import Path
from typing import Any

from debate_arena.constants import CONFIG_VERSION_KEY
from debate_arena.shared.version import is_compatible


class ConfigError(RuntimeError):
    """Raised on a missing file, missing key, or version mismatch."""


class ConfigManager:
    """Loads and validates configuration; the single config entry point.

    Input:  config_dir (path holding setup.json, rate_limits.json, ...).
    Output: parsed dicts via `get(...)`; secrets via `secret(...)`.
    Setup:  validates each loaded file's "version" against the code version.
    """

    def __init__(self, config_dir: str | Path) -> None:
        self._dir = Path(config_dir)
        if not self._dir.is_dir():
            raise ConfigError(f"Config dir not found: {self._dir}")
        self._cache: dict[str, dict[str, Any]] = {}

    def load(self, name: str) -> dict[str, Any]:
        """Load `<name>.json`, validate its version, and cache it."""
        if name in self._cache:
            return self._cache[name]
        path = self._dir / f"{name}.json"
        if not path.is_file():
            raise ConfigError(f"Missing config file: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        version = data.get(CONFIG_VERSION_KEY)
        if version is None or not is_compatible(version):
            raise ConfigError(f"{name}.json version {version!r} is incompatible")
        self._cache[name] = data
        return data

    def get(self, name: str, *keys: str, default: Any = None) -> Any:
        """Nested lookup: get('setup', 'debate', 'pings_per_side')."""
        node: Any = self.load(name)
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    @staticmethod
    def secret(env_var: str) -> str:
        """Read a secret from the environment only (Guide §7.4)."""
        value = os.environ.get(env_var)
        if not value:
            raise ConfigError(f"Missing required secret env var: {env_var}")
        return value
