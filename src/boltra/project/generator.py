"""Generate minimal FastAPI projects via ``boltra new``."""

from __future__ import annotations

from pathlib import Path

from boltra.cli.parser import validate_project_name
from boltra.project.templates import main_py, pyproject_toml, settings_py


class ProjectError(Exception):
    """Raised when project generation cannot proceed."""


def create_project(name: str, *, cwd: Path | None = None) -> Path:
    """Create a new Boltra FastAPI project directory.

    Args:
        name: Project slug (validated).
        cwd: Parent directory (defaults to current working directory).

    Returns:
        Absolute path to the created project directory.

    Raises:
        ProjectError: Invalid name or target directory already exists.
    """
    try:
        validate_project_name(name)
    except Exception as exc:
        raise ProjectError(str(exc)) from exc

    base = (cwd or Path.cwd()).resolve()
    project_dir = base / name

    if project_dir.exists():
        msg = f"directory '{name}' already exists"
        raise ProjectError(msg)

    project_dir.mkdir(parents=False, exist_ok=False)
    (project_dir / "main.py").write_text(main_py(name), encoding="utf-8", newline="\n")
    (project_dir / "settings.py").write_text(
        settings_py(name),
        encoding="utf-8",
        newline="\n",
    )
    (project_dir / "pyproject.toml").write_text(
        pyproject_toml(name),
        encoding="utf-8",
        newline="\n",
    )

    return project_dir
