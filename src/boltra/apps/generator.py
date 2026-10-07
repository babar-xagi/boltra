"""Create an app package and register its router on the configured FastAPI app."""

from __future__ import annotations

import os
import tempfile
from contextlib import suppress
from importlib.resources import files
from pathlib import Path
from string import Template

from boltra.apps.registration import register_router
from boltra.apps.validation import validate_app_name
from boltra.dev.config import DevConfigError, find_project_root, load_boltra_config


class AppError(Exception):
    """Raised when app creation or registration cannot safely proceed."""


def add_app(name: str, *, cwd: Path | None = None) -> Path:
    """Create ``apps/<name>`` and register its router; preserve unrelated files.

    The project must configure a source module containing a direct top-level
    FastAPI instance. Settings are not modified and no app code is executed.
    """
    try:
        validate_app_name(name)
        root = find_project_root(cwd)
        config = load_boltra_config(root / "pyproject.toml")
        module, attribute = config.app.split(":")
        main = root.joinpath(*module.split(".")).with_suffix(".py")
        _check_local_path(main, root)
        original = main.read_bytes()
        updated = register_router(original, name, attribute)
        apps = root / "apps"
        destination = apps / name
        _check_local_path(destination, root)
        if (root / "apps.py").exists():
            raise ValueError("apps.py conflicts with the generated apps package")
        if destination.exists():
            raise ValueError(f"app '{name}' already exists")
        if apps.exists() and not apps.is_dir():
            raise ValueError("apps must be a directory")
        initializer = apps / "__init__.py"
        _check_local_path(initializer, root)
        if initializer.exists() and not initializer.is_file():
            raise ValueError("apps/__init__.py must be a regular file")
        router = Template(
            files("boltra.apps").joinpath("templates/router.py.tmpl").read_text("utf-8")
        ).substitute(app_name=name)
    except (ValueError, SyntaxError, OSError, DevConfigError) as exc:
        raise AppError(str(exc)) from exc

    created_files: list[Path] = []
    created_dirs: list[Path] = []
    try:
        if not apps.exists():
            apps.mkdir()
            created_dirs.append(apps)
        destination.mkdir()
        created_dirs.append(destination)
        contents = [(destination / "__init__.py", f'"""{name} app package."""\n')]
        if not initializer.exists():
            contents.insert(0, (initializer, '"""Project API apps."""\n'))
        contents.append((destination / "router.py", router))
        for path, content in contents:
            # Exclusive creation never overwrites files created by another process.
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                created_files.append(path)
                stream.write(content)
        # Detect an editor change before replacing source. Registration is last,
        # so a failed scaffold leaves the application's original source intact.
        if main.read_bytes() != original:
            raise OSError("application source changed during app creation; retry")
        _replace_source(main, updated)
    except OSError as exc:
        for path in reversed(created_files):
            with suppress(OSError):
                path.unlink()
        for path in reversed(created_dirs):
            with suppress(OSError):
                path.rmdir()
        raise AppError(f"cannot create app '{name}': {exc}") from exc
    return destination


def _check_local_path(path: Path, root: Path) -> None:
    """Reject symlinks/junctions and destinations outside the project."""
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"path must stay inside the project: {path}")
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink() or part.is_junction():
            raise ValueError(f"linked paths are not supported: {part}")


def _replace_source(path: Path, content: bytes) -> None:
    """Write beside the source and atomically replace it, retaining permissions."""
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.chmod(path.stat().st_mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            with suppress(OSError):
                temporary.unlink(missing_ok=True)
