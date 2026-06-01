"""Single source of truth for the code version (Guide §8.1).

The application validates that configuration file versions match the expected
code version at startup; a mismatch is a hard error.
"""

# Code version. Starts at 1.00 and rises with meaningful changes (Guide §8.1).
__version__ = "1.00"

# Config versions the running code is known to be compatible with.
EXPECTED_CONFIG_VERSION = "1.00"


def is_compatible(config_version: str) -> bool:
    """Return True if a config file's "version" matches the expected version."""
    return config_version == EXPECTED_CONFIG_VERSION
