"""Tests for development environment selection and startup handling."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from boltra.cli import execute
from boltra.dev.config import load_boltra_config
from boltra.dev.server import build_uvicorn_command, format_dev_banner, run_dev_server
from boltra.project.generator import create_project


@pytest.mark.parametrize("uv", [None, "uv"])
def test_build_uvicorn_command_prefers_project_venv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, uv: str | None
) -> None:
    """An existing project venv launches directly even when uv is available."""
    project = create_project("demo", cwd=tmp_path)
    config = load_boltra_config(project / "pyproject.toml")
    relative = (
        ".venv/Scripts/python.exe" if sys.platform == "win32" else ".venv/bin/python"
    )
    executable = project / relative
    executable.parent.mkdir(parents=True)
    executable.touch()
    monkeypatch.setattr("boltra.dev.server.shutil.which", lambda _: uv)
    command = build_uvicorn_command(project, config)
    assert command[0] == str(executable)
    if sys.platform == "win32":
        assert Path(command[1]).name == "windows.py"
    else:
        assert command[1:3] == ["-m", "uvicorn"]


def test_dev_missing_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A project without uv or a venv returns guidance without a traceback."""
    project = create_project("demo", cwd=tmp_path)
    monkeypatch.setattr("boltra.dev.server.shutil.which", lambda _: None)
    assert run_dev_server(cwd=project) == 1
    assert "uv sync" in capsys.readouterr().err


def test_dev_process_permission_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A launch permission error is handled like other failed starts."""
    project = create_project("demo", cwd=tmp_path)

    def denied(*args: object, **kwargs: object) -> None:
        raise PermissionError("launch denied")

    monkeypatch.setattr("boltra.dev.server.subprocess.run", denied)
    assert run_dev_server(cwd=project) == 1
    assert "launch denied" in capsys.readouterr().err


def test_dev_ipv6_banner(tmp_path: Path) -> None:
    """IPv6 hosts use valid bracketed browser URLs."""
    project = create_project("demo", cwd=tmp_path)
    path = project / "pyproject.toml"
    path.write_text('[tool.boltra]\nhost = "::1"\n', encoding="utf-8")
    assert "http://[::1]:8000/docs" in format_dev_banner(load_boltra_config(path))


def test_format_dev_banner(tmp_path: Path) -> None:
    """Banner includes URL, docs URL, and mode."""
    create_project("demo", cwd=tmp_path)
    config = load_boltra_config(tmp_path / "demo" / "pyproject.toml")
    banner = format_dev_banner(config)

    assert "fastapi-kit" in banner
    assert "http://127.0.0.1:8000/" in banner
    assert "http://127.0.0.1:8000/docs" in banner
    assert "main:app" in banner


def test_build_uvicorn_command_uses_uv(tmp_path: Path) -> None:
    """Command prefers ``uv run uvicorn`` when uv is on PATH."""
    create_project("demo", cwd=tmp_path)
    project = tmp_path / "demo"
    config = load_boltra_config(project / "pyproject.toml")

    command = build_uvicorn_command(project, config)

    assert command[:2] == ["uv", "run"]
    assert "main:app" in command
    assert command[command.index("--host") + 1] == "127.0.0.1"
    assert command[command.index("--port") + 1] == "8000"
    assert "--reload" in command


def test_parse_argv_dev() -> None:
    """Python parser recognizes ``dev`` subcommand."""
    from boltra.cli.parser import parse_argv

    parsed = parse_argv(["dev"])
    assert parsed.action == "dev"


def test_dev_missing_project(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``boltra dev`` errors outside a Boltra project."""
    code = run_dev_server(cwd=tmp_path)
    err = capsys.readouterr().err

    assert code == 1
    assert "not in a Boltra project" in err


def test_cli_dev_banner_before_uvicorn(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Dispatch prints the dev banner before launching uvicorn."""
    create_project("demo", cwd=tmp_path)
    project = tmp_path / "demo"

    def fake_run(
        command: list[str],
        cwd: Path,
        check: bool,
    ) -> subprocess.CompletedProcess[str]:
        assert command[0] == "uv"
        assert "main:app" in command
        assert cwd == project
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("boltra.dev.server.subprocess.run", fake_run)

    code = execute(["dev"], cwd=project)
    out = capsys.readouterr().out

    assert code == 0
    assert "Boltra dev server" in out
    assert "/docs" in out


def test_cli_dev_ctrl_c_exits_cleanly(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``boltra dev`` handles Ctrl+C without a traceback."""
    create_project("demo", cwd=tmp_path)
    project = tmp_path / "demo"

    def fake_run(
        command: list[str],
        cwd: Path,
        check: bool,
    ) -> subprocess.CompletedProcess[str]:
        assert command[0] == "uv"
        assert cwd == project
        raise KeyboardInterrupt

    monkeypatch.setattr("boltra.dev.server.subprocess.run", fake_run)

    code = execute(["dev"], cwd=project)
    out = capsys.readouterr().out

    assert code == 130
    assert "Stopped Boltra dev server" in out
