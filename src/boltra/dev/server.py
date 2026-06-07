"""Development server launcher for ``boltra dev``."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from boltra.dev.config import (
    BoltraProjectConfig,
    DevConfigError,
    find_project_root,
    load_boltra_config,
)


class DevServerError(Exception):
    """Raised when the dev server cannot start."""


def _find_venv_python(project_root: Path) -> Path | None:
    """Return the project ``.venv`` Python executable when present."""
    if sys.platform == "win32":
        candidate = project_root / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = project_root / ".venv" / "bin" / "python"
    return candidate if candidate.is_file() else None


def build_uvicorn_command(
    project_root: Path,
    config: BoltraProjectConfig,
) -> list[str]:
    """Build the uvicorn command using the project's environment."""
    uvicorn_args = [
        config.app,
        "--host",
        config.host,
        "--port",
        str(config.port),
        "--reload",
    ]

    if shutil.which("uv") is not None:
        return ["uv", "run", "uvicorn", *uvicorn_args]

    venv_python = _find_venv_python(project_root)
    if venv_python is not None:
        return [str(venv_python), "-m", "uvicorn", *uvicorn_args]

    msg = "no project environment found — run `uv sync` in the project directory first"
    raise DevServerError(msg)


def format_dev_banner(config: BoltraProjectConfig) -> str:
    """Return the startup banner printed before uvicorn launches."""
    base = f"http://{config.host}:{config.port}"
    return (
        "Boltra dev server\n"
        f"  Mode:  {config.mode}\n"
        f"  App:   {config.app}\n"
        f"  URL:   {base}/\n"
        f"  Docs:  {base}/docs\n"
        "\n"
        "Starting uvicorn with --reload ...\n"
    )


def run_dev_server(*, cwd: Path | None = None) -> int:
    """Start uvicorn for the current Boltra project.

    Reads ``[tool.boltra]`` from ``pyproject.toml`` and runs
    ``uvicorn <app> --reload`` via ``uv run`` or the project ``.venv``.
    """
    try:
        project_root = find_project_root(cwd)
        config = load_boltra_config(project_root / "pyproject.toml")
        command = build_uvicorn_command(project_root, config)
    except (DevConfigError, DevServerError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1

    sys.stdout.write(format_dev_banner(config))
    sys.stdout.flush()

    try:
        result = subprocess.run(command, cwd=project_root, check=False)
    except FileNotFoundError as exc:
        sys.stderr.write(f"error: failed to start uvicorn ({exc})\n")
        return 1

    return int(result.returncode)
