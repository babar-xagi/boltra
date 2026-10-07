"""Validate names that become Python packages and URL prefixes."""

from __future__ import annotations

import keyword
import re


def validate_app_name(name: str) -> str:
    """Accept lowercase ASCII package names portable across supported platforms."""
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise ValueError(
            "app name must start with a lowercase ASCII letter and contain "
            "only lowercase letters, digits, or underscores"
        )
    # Keywords cannot be imported; Windows device names are invalid directories.
    reserved = {"con", "prn", "aux", "nul", "__pycache__"}
    reserved.update(
        f"{prefix}{index}" for prefix in ("com", "lpt") for index in range(10)
    )
    if keyword.iskeyword(name) or keyword.issoftkeyword(name) or name in reserved:
        raise ValueError(f"app name '{name}' is reserved; choose another name")
    return name
