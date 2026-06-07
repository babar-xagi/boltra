"""Load ``[tool.boltra]`` configuration from a project's ``pyproject.toml``."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

_APP_PATH_RE: Final = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*:[a-zA-Z_][a-zA-Z0-9_]*$")


class DevConfigError(Exception):
    """Raised when Boltra project configuration cannot be loaded."""


@dataclass(frozen=True, slots=True)
class BoltraProjectConfig:
    """Boltra project settings from ``[tool.boltra]``."""

    app: str
    mode: str
    settings: str
    host: str = "127.0.0.1"
    port: int = 8000


def has_tool_boltra(pyproject_path: Path) -> bool:
    """Return True when ``pyproject.toml`` contains a ``[tool.boltra]`` table."""
    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return False
    tool = data.get("tool")
    if not isinstance(tool, dict):
        return False
    boltra = tool.get("boltra")
    return isinstance(boltra, dict) and bool(boltra)


def find_project_root(start: Path | None = None) -> Path:
    """Find the nearest directory with ``[tool.boltra]`` in ``pyproject.toml``."""
    current = (start or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        pyproject = directory / "pyproject.toml"
        if pyproject.is_file() and has_tool_boltra(pyproject):
            return directory
    msg = "not in a Boltra project (missing [tool.boltra] in pyproject.toml)"
    raise DevConfigError(msg)


def load_boltra_config(pyproject_path: Path) -> BoltraProjectConfig:
    """Parse ``[tool.boltra]`` from the given ``pyproject.toml`` path."""
    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except OSError as exc:
        msg = f"cannot read {pyproject_path}"
        raise DevConfigError(msg) from exc
    except tomllib.TOMLDecodeError as exc:
        msg = f"invalid TOML in {pyproject_path}"
        raise DevConfigError(msg) from exc

    tool: dict[str, Any] = data.get("tool", {})
    if not isinstance(tool, dict):
        tool = {}
    boltra_table = tool.get("boltra", {})
    if not isinstance(boltra_table, dict) or not boltra_table:
        msg = "[tool.boltra] section missing from pyproject.toml"
        raise DevConfigError(msg)

    app = str(boltra_table.get("app", "main:app"))
    mode = str(boltra_table.get("mode", "fastapi-kit"))
    settings = str(boltra_table.get("settings", "settings.py"))

    if not _APP_PATH_RE.match(app):
        msg = f"invalid [tool.boltra] app path '{app}' (expected module:attr)"
        raise DevConfigError(msg)

    return BoltraProjectConfig(app=app, mode=mode, settings=settings)
