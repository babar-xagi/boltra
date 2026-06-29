"""Integration tests for boltra new project generation."""

from __future__ import annotations

import importlib.util
import sys
import warnings
from pathlib import Path
from types import ModuleType

import pytest

from boltra.cli.dispatch import execute
from boltra.project.generator import ProjectError, create_project


def _import_generated_module(
    module_name: str,
    module_path: Path,
    project_dir: Path,
) -> ModuleType:
    """Import a generated project file with the project on sys.path."""
    original_path = list(sys.path)
    sys.path.insert(0, str(project_dir))
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = original_path


def test_create_project_files(tmp_path: Path) -> None:
    """create_project writes the generated FastAPI project files."""
    project_dir = create_project("hello", cwd=tmp_path)

    assert project_dir == tmp_path / "hello"
    assert (project_dir / "main.py").is_file()
    assert (project_dir / "settings.py").is_file()
    assert (project_dir / "pyproject.toml").is_file()
    assert (project_dir / ".env.example").is_file()

    main_source = (project_dir / "main.py").read_text(encoding="utf-8")
    assert "from fastapi import FastAPI" in main_source
    assert "from settings import settings" in main_source
    assert "title=settings.api_title" in main_source

    settings_source = (project_dir / "settings.py").read_text(encoding="utf-8")
    assert "class Settings" in settings_source
    assert "pydantic_settings" in settings_source
    assert 'app_name: str = "hello"' in settings_source
    assert "SECRET_KEY is still using the generated default" in settings_source

    env_source = (project_dir / ".env.example").read_text(encoding="utf-8")
    assert "APP_NAME=hello" in env_source
    assert "API_TITLE=Hello API" in env_source
    assert "SECRET_KEY=change-this-secret-key" in env_source

    pyproject_source = (project_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.12"' in pyproject_source
    assert '"pydantic-settings>=2.6"' in pyproject_source
    assert '"boltra"' not in pyproject_source


def test_generated_project_imports(tmp_path: Path) -> None:
    """Generated main.py imports without error."""
    project_dir = create_project("myapp", cwd=tmp_path)
    main_file = project_dir / "main.py"

    module = _import_generated_module("generated_main", main_file, project_dir)

    assert hasattr(module, "app")
    assert module.app.title == "Myapp API"  # type: ignore[attr-defined]

    sys.modules.pop("generated_main", None)
    sys.modules.pop("settings", None)


def test_generated_settings_load_env_file(tmp_path: Path) -> None:
    """Generated settings.py loads values from .env."""
    project_dir = create_project("myapp", cwd=tmp_path)
    (project_dir / ".env").write_text(
        "\n".join(
            [
                "APP_NAME=myapp",
                "API_TITLE=Env Loaded API",
                "DEBUG=false",
                "SECRET_KEY=local-secret",
                'ALLOWED_HOSTS=["example.com","api.example.com"]',
                "AUTH_ENABLED=true",
            ]
        ),
        encoding="utf-8",
    )

    module = _import_generated_module(
        "generated_settings_env",
        project_dir / "settings.py",
        project_dir,
    )

    assert module.settings.api_title == "Env Loaded API"
    assert module.settings.debug is False
    assert module.settings.secret_key == "local-secret"
    assert module.settings.allowed_hosts == ["example.com", "api.example.com"]
    assert module.AUTH == {"ENABLED": True}

    sys.modules.pop("generated_settings_env", None)


def test_cli_new_integration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """boltra new hello creates a project and prints next steps."""
    code = execute(["new", "hello"], cwd=tmp_path)
    out = capsys.readouterr().out

    assert code == 0
    assert (tmp_path / "hello" / "main.py").exists()
    assert (tmp_path / "hello" / ".env.example").exists()
    assert "Next steps" in out
    assert "cd hello" in out


def test_reject_existing_directory(tmp_path: Path) -> None:
    """Generation fails when the target directory already exists."""
    (tmp_path / "hello").mkdir()
    with pytest.raises(ProjectError, match="already exists"):
        create_project("hello", cwd=tmp_path)


def test_reject_invalid_name(tmp_path: Path) -> None:
    """Generation fails for invalid project names."""
    with pytest.raises(ProjectError):
        create_project("1bad", cwd=tmp_path)


def test_cli_new_existing_dir_errors(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """CLI reports an error when the directory already exists."""
    (tmp_path / "hello").mkdir()
    code = execute(["new", "hello"], cwd=tmp_path)
    err = capsys.readouterr().err

    assert code == 1
    assert "already exists" in err
