"""Integration tests for ``boltra new`` project generation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from boltra.cli.dispatch import execute
from boltra.project.generator import ProjectError, create_project


def test_create_project_files(tmp_path: Path) -> None:
    """``create_project`` writes main.py, settings.py, and pyproject.toml."""
    project_dir = create_project("hello", cwd=tmp_path)

    assert project_dir == tmp_path / "hello"
    assert (project_dir / "main.py").is_file()
    assert (project_dir / "settings.py").is_file()
    assert (project_dir / "pyproject.toml").is_file()

    main_source = (project_dir / "main.py").read_text(encoding="utf-8")
    assert "from fastapi import FastAPI" in main_source
    assert 'title="Hello API"' in main_source

    settings_source = (project_dir / "settings.py").read_text(encoding="utf-8")
    assert 'APP_NAME = "hello"' in settings_source

    pyproject_source = (project_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.12"' in pyproject_source
    assert '"boltra"' not in pyproject_source


def test_generated_project_imports(tmp_path: Path) -> None:
    """Generated ``main.py`` imports without error."""
    project_dir = create_project("myapp", cwd=tmp_path)
    main_file = project_dir / "main.py"

    spec = importlib.util.spec_from_file_location("generated_main", main_file)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["generated_main"] = module
    spec.loader.exec_module(module)

    assert hasattr(module, "app")
    assert module.app.title == "Myapp API"  # type: ignore[attr-defined]

    sys.modules.pop("generated_main", None)


def test_cli_new_integration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``boltra new hello`` creates a project and prints next steps."""
    code = execute(["new", "hello"], cwd=tmp_path)
    out = capsys.readouterr().out

    assert code == 0
    assert (tmp_path / "hello" / "main.py").exists()
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
