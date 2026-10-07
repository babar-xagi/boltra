"""Tests for project discovery and development-server configuration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from boltra.dev.config import DevConfigError, find_project_root, load_boltra_config
from boltra.project.generator import create_project


def test_load_boltra_config(tmp_path: Path) -> None:
    """``load_boltra_config`` reads ``[tool.boltra]`` from pyproject.toml."""
    create_project("demo", cwd=tmp_path)
    config = load_boltra_config(tmp_path / "demo" / "pyproject.toml")

    assert config.app == "main:app"
    assert config.mode == "fastapi-kit"
    assert config.settings == "settings.py"
    assert config.host == "127.0.0.1"
    assert config.port == 8000


def test_load_boltra_config_custom_host_port(tmp_path: Path) -> None:
    """``load_boltra_config`` reads optional host and port values."""
    project = create_project("demo", cwd=tmp_path)
    pyproject = project / "pyproject.toml"
    source = pyproject.read_text(encoding="utf-8")
    source = source.replace('host = "127.0.0.1"', 'host = "0.0.0.0"')
    source = source.replace("port = 8000", "port = 8765")
    pyproject.write_text(source, encoding="utf-8")

    config = load_boltra_config(pyproject)

    assert config.host == "0.0.0.0"
    assert config.port == 8765


def test_load_boltra_config_rejects_invalid_port(tmp_path: Path) -> None:
    """``load_boltra_config`` rejects ports outside TCP range."""
    project = create_project("demo", cwd=tmp_path)
    pyproject = project / "pyproject.toml"
    source = pyproject.read_text(encoding="utf-8")
    pyproject.write_text(
        source.replace("port = 8000", "port = 70000"), encoding="utf-8"
    )

    with pytest.raises(DevConfigError, match="port"):
        load_boltra_config(pyproject)


def test_load_boltra_config_accepts_utf8_bom(tmp_path: Path) -> None:
    """``load_boltra_config`` accepts pyproject files saved with a UTF-8 BOM."""
    project = create_project("demo", cwd=tmp_path)
    pyproject = project / "pyproject.toml"
    source = pyproject.read_text(encoding="utf-8")
    pyproject.write_text(f"\ufeff{source}", encoding="utf-8")

    config = load_boltra_config(pyproject)

    assert config.app == "main:app"
    assert find_project_root(project) == project


def test_load_boltra_config_dotted_app(tmp_path: Path) -> None:
    """Uvicorn import targets may use a module inside a Python package."""
    project = create_project("demo", cwd=tmp_path)
    path = project / "pyproject.toml"
    path.write_text('[tool.boltra]\napp = "backend.main:app"\n', encoding="utf-8")
    assert load_boltra_config(path).app == "backend.main:app"


def test_load_boltra_config_invalid_encoding(tmp_path: Path) -> None:
    """Invalid UTF-8 is a configuration error, rather than an uncaught crash."""
    path = tmp_path / "pyproject.toml"
    path.write_bytes(b"[tool.boltra]\napp = \xff\n")
    with pytest.raises(DevConfigError):
        load_boltra_config(path)
    with pytest.raises(DevConfigError):
        find_project_root(tmp_path)


@pytest.mark.parametrize("port", ["true", '"8000"', "0", "-1", "65536"])
def test_load_boltra_config_invalid_port_types(tmp_path: Path, port: str) -> None:
    """Invalid port values fail with a readable config error."""
    path = tmp_path / "pyproject.toml"
    path.write_text(f"[tool.boltra]\nport = {port}\n", encoding="utf-8")
    with pytest.raises(DevConfigError, match="port"):
        load_boltra_config(path)


@pytest.mark.parametrize("host", ['""', '" "', "123", "true"])
def test_load_boltra_config_invalid_host(tmp_path: Path, host: str) -> None:
    """Empty and non-string hosts fail validation."""
    path = tmp_path / "pyproject.toml"
    path.write_text(f"[tool.boltra]\nhost = {host}\n", encoding="utf-8")
    with pytest.raises(DevConfigError, match="host"):
        load_boltra_config(path)


@pytest.mark.parametrize(
    "content",
    ["[tool.boltra", "tool = false", "[tool]\nboltra = false", "[tool.boltra]"],
)
def test_invalid_project_config(tmp_path: Path, content: str) -> None:
    """Malformed TOML and missing configuration tables produce domain errors."""
    path = tmp_path / "pyproject.toml"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(DevConfigError):
        load_boltra_config(path)
    with pytest.raises(DevConfigError):
        find_project_root(tmp_path)


@pytest.mark.parametrize("app", ["main:app\n", "main", "main:", "../main:app"])
def test_invalid_app_target(tmp_path: Path, app: str) -> None:
    """Malformed import paths are rejected before Uvicorn is launched."""

    path = tmp_path / "pyproject.toml"
    path.write_text(f"[tool.boltra]\napp = {json.dumps(app)}\n", encoding="utf-8")
    with pytest.raises(DevConfigError, match="app path"):
        load_boltra_config(path)


def test_missing_config_file(tmp_path: Path) -> None:
    """Unreadable configuration is exposed as a domain-specific error."""
    with pytest.raises(DevConfigError, match="cannot read"):
        load_boltra_config(tmp_path / "missing.toml")


def test_find_project_root(tmp_path: Path) -> None:
    """``find_project_root`` locates the project from a child directory."""
    project = create_project("demo", cwd=tmp_path)
    nested = project / "subdir"
    nested.mkdir()

    assert find_project_root(nested) == project
