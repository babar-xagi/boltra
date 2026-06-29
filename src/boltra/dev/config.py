"""Load ``[tool.boltra]`` configuration from a project's ``pyproject.toml``."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

_APP_PATH_RE: Final = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*:[a-zA-Z_][a-zA-Z0-9_]*$")
_DEFAULT_HOST: Final = "127.0.0.1"
_DEFAULT_PORT: Final = 8000


class DevConfigError(Exception):
    """Raised when Boltra project configuration cannot be loaded."""


@dataclass(frozen=True, slots=True)
class BoltraProjectConfig:
    """Boltra project settings from ``[tool.boltra]``."""

    app: str
    mode: str
    settings: str
    host: str = _DEFAULT_HOST
    port: int = _DEFAULT_PORT


def has_tool_boltra(pyproject_path: Path) -> bool:
    """Return True when ``pyproject.toml`` contains a ``[tool.boltra]`` table."""
    try:
        data = tomllib.loads(_read_pyproject_text(pyproject_path))
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
        data = tomllib.loads(_read_pyproject_text(pyproject_path))
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
    host = _load_host(boltra_table)
    port = _load_port(boltra_table)

    if not _APP_PATH_RE.match(app):
        msg = f"invalid [tool.boltra] app path '{app}' (expected module:attr)"
        raise DevConfigError(msg)

    return BoltraProjectConfig(
        app=app,
        mode=mode,
        settings=settings,
        host=host,
        port=port,
    )


def _read_pyproject_text(pyproject_path: Path) -> str:
    return pyproject_path.read_text(encoding="utf-8-sig")


def _load_host(boltra_table: dict[str, Any]) -> str:
    raw_host = boltra_table.get("host", _DEFAULT_HOST)
    if not isinstance(raw_host, str) or not raw_host.strip():
        msg = "invalid [tool.boltra] host value (expected non-empty string)"
        raise DevConfigError(msg)
    return raw_host.strip()


def _load_port(boltra_table: dict[str, Any]) -> int:
    raw_port = boltra_table.get("port", _DEFAULT_PORT)
    if isinstance(raw_port, bool) or not isinstance(raw_port, int):
        msg = "invalid [tool.boltra] port value (expected integer 1-65535)"
        raise DevConfigError(msg)
    if not 1 <= raw_port <= 65535:
        msg = "invalid [tool.boltra] port value (expected integer 1-65535)"
        raise DevConfigError(msg)
    return int(raw_port)
