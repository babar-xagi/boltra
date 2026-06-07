"""Tests for the Boltra CLI (Rust clap parse + Python dispatch)."""

from __future__ import annotations

import sys

import pytest

from boltra import __version__
from boltra.cli.dispatch import execute
from boltra.cli.parser import parse_argv


def test_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    """``boltra --help`` prints usage information."""
    code = execute(["--help"])
    out = capsys.readouterr().out
    assert code == 0
    assert "boltra" in out.lower()
    assert "new" in out
    assert "dev" in out


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    """``boltra --version`` prints the package version."""
    code = execute(["--version"])
    assert code == 0
    assert capsys.readouterr().out.strip() == __version__


def test_cli_version_short_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """``boltra -V`` is an alias for ``--version``."""
    code = execute(["-V"])
    assert code == 0
    assert capsys.readouterr().out.strip() == __version__


def test_cli_no_args_shows_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Running ``boltra`` with no arguments shows help."""
    code = execute([])
    out = capsys.readouterr().out
    assert code == 0
    assert "boltra" in out.lower()


def test_parse_argv_new_native() -> None:
    """Rust clap parser recognizes ``new`` subcommand."""
    parsed = parse_argv(["new", "hello"])
    assert parsed.action == "new"
    assert parsed.name == "hello"


def test_parse_argv_invalid_name() -> None:
    """Invalid project names return an error action."""
    parsed = parse_argv(["new", "1bad"])
    assert parsed.action == "error"
    assert parsed.error_message


def test_run_entry_point(monkeypatch: pytest.MonkeyPatch) -> None:
    """Console entry point ``run()`` exits with the handler status code."""
    from boltra.cli.main import run

    monkeypatch.setattr(sys, "argv", ["boltra", "--version"])
    with pytest.raises(SystemExit) as exc:
        run()
    assert exc.value.code == 0
