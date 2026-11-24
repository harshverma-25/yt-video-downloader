"""Single source of truth for application version."""

import os
import re

__version__ = "1.0.0"


def get_version() -> str:
    """Return normalized application version (semantic versioning x.y.z).

    Checks environment variables (APP_VERSION, GITHUB_REF_NAME) for release builds,
    falling back to the hardcoded __version__.
    """
    for env_var in ("APP_VERSION", "GITHUB_REF_NAME"):
        raw_val = os.environ.get(env_var, "").strip()
        if raw_val:
            # Strip leading 'v' if present (e.g. 'v1.0.0' -> '1.0.0')
            clean_ver = re.sub(r"^v", "", raw_val).strip()
            if clean_ver:
                return clean_ver
    return __version__

