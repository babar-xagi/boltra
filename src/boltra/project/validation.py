"""Project-name rules shared by the CLI and programmatic generator."""

from __future__ import annotations

import re
from typing import Final

_PROJECT_NAME: Final = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]*")


def validate_project_name(name: str) -> str:
    """Return a valid project slug or raise ``ValueError`` with a useful message."""
    if not name:
        raise ValueError("project name cannot be empty")
    if any(character in name for character in ("/", "\\", ".")):
        raise ValueError(
            f"project name '{name}' must not contain path separators or dots"
        )
    # fullmatch rejects trailing whitespace/newlines as well as invalid characters.
    if not _PROJECT_NAME.fullmatch(name):
        raise ValueError(
            f"project name '{name}' must start with a letter and contain only "
            "letters, digits, hyphens, and underscores"
        )
    return name
