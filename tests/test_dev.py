"""Tests for ``boltra dev`` and project configuration loading."""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from boltra.cli.dispatch import execute
from boltra.dev.config import find_project_root, load_boltra_config
from boltra.dev.server import build_uvicorn_command, format_dev_banner, run_dev_server
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


def test_find_project_root(tmp_path: Path) -> None:
    """``find_project_root`` locates the project from a child directory."""
    project = create_project("demo", cwd=tmp_path)
    nested = project / "subdir"
    nested.mkdir()

    assert find_project_root(nested) == project


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

    assert command[:3] == ["uv", "run", "uvicorn"]
    assert command[3] == "main:app"
    assert "--reload" in command


def test_parse_argv_dev() -> None:
    """Clap / native parser recognizes ``dev`` subcommand."""
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
        assert "uvicorn" in command
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


@pytest.mark.integration
def test_dev_server_serves_routes(tmp_path: Path) -> None:
    """``boltra dev`` serves ``/`` and ``/docs`` (Phase 3 exit criteria)."""
    if shutil_which("uv") is None:
        pytest.skip("uv not installed")

    create_project("demo", cwd=tmp_path)
    project = tmp_path / "demo"

    sync = subprocess.run(
        ["uv", "sync"],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    if sync.returncode != 0:
        pytest.skip(f"uv sync failed: {sync.stderr}")

    proc = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "from boltra.dev.server import run_dev_server; "
            "raise SystemExit(run_dev_server())",
        ],
        cwd=project,
    )

    try:
        _wait_for_url("http://127.0.0.1:8000/", timeout=30.0)
        _wait_for_url("http://127.0.0.1:8000/docs", timeout=5.0)
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def shutil_which(cmd: str) -> str | None:
    """Thin wrapper to avoid importing shutil at module level in skip helper."""
    import shutil

    return shutil.which(cmd)


def _wait_for_url(url: str, *, timeout: float) -> None:
    """Poll ``url`` until HTTP 200 or timeout."""
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            time.sleep(0.5)
    msg = f"timed out waiting for {url}"
    if last_error is not None:
        msg = f"{msg}: {last_error}"
    raise AssertionError(msg)
