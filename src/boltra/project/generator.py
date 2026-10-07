"""Generate minimal FastAPI projects via ``boltra new``."""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from boltra.project.template_engine import (
    env_example,
    main_py,
    pyproject_toml,
    settings_py,
)
from boltra.project.validation import validate_project_name


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
    except ValueError as exc:
        raise ProjectError(str(exc)) from exc

    base = (cwd or Path.cwd()).resolve()
    project_dir = base / name

    if project_dir.exists() or project_dir.is_symlink():
        msg = f"directory '{name}' already exists"
        raise ProjectError(msg)

    try:
        project_dir.mkdir(parents=False, exist_ok=False)
    except OSError as exc:
        raise ProjectError(f"cannot create project '{name}': {exc}") from exc

    # Record each destination before writing: even a failed write can leave a file.
    written: list[Path] = []
    try:
        for filename, content in (
            ("main.py", main_py(name)),
            ("settings.py", settings_py(name)),
            ("pyproject.toml", pyproject_toml(name)),
            (".env.example", env_example(name)),
        ):
            path = project_dir / filename
            written.append(path)
            path.write_text(content, encoding="utf-8", newline="\n")
    except OSError as exc:
        # Remove only generated files; preserve anything else in the directory.
        for path in reversed(written):
            with suppress(OSError):
                path.unlink(missing_ok=True)
        with suppress(OSError):
            project_dir.rmdir()
        raise ProjectError(f"cannot write project '{name}': {exc}") from exc

    return project_dir
