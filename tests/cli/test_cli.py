"""Tests for the Boltra CLI (Python parsing and command routing)."""

from __future__ import annotations

import runpy
import sys

import pytest

from boltra import __version__
from boltra.cli import execute
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


def test_parse_argv_new() -> None:
    """Python parser recognizes ``new`` subcommand."""
    parsed = parse_argv(["new", "hello"])
    assert parsed.action == "new"
    assert parsed.name == "hello"


def test_parse_argv_invalid_name() -> None:
    """Invalid project names return an error action."""
    parsed = parse_argv(["new", "1bad"])
    assert parsed.action == "error"
    assert parsed.error_message


def test_run_entry_point(monkeypatch: pytest.MonkeyPatch) -> None:
    """The module entry point uses the CLI and exits with its handler status."""
    monkeypatch.setattr(sys, "argv", ["boltra", "--version"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("boltra", run_name="__main__")
    assert exc.value.code == 0


@pytest.mark.parametrize("command", ["new", "dev"])
def test_python_subcommand_help_once(
    command: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Subcommand help is returned to the dispatcher without printing twice."""
    parsed = parse_argv([command, "--help"])
    assert parsed.action == "help"
    assert f"usage: boltra {command}" in (parsed.help_text or "")
    assert capsys.readouterr().out == ""


def test_python_parser_does_not_print_errors(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The dispatcher owns error output, with the original parser detail."""
    parsed = parse_argv(["new", "1bad"])
    assert parsed.action == "error"
    assert "must start with a letter" in (parsed.error_message or "")
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("name", ["hello\n", "hello\r", "hi there", "école", "../app"])
def test_python_parser_rejects_invalid_names(name: str) -> None:
    """Validation must consume the entire name, including trailing newlines."""
    assert parse_argv(["new", name]).action == "error"


@pytest.mark.parametrize("args", [["unknown"], ["new"], ["dev", "extra"]])
def test_cli_invalid_arguments_once(
    args: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    """Invalid commands produce one error and return the usage exit status."""
    assert execute(args) == 2
    captured = capsys.readouterr()
    assert not captured.out
    assert captured.err.count("error:") == 1


@pytest.mark.parametrize(
    ("args", "action", "name"),
    [
        ([], "help", None),
        (["--help"], "help", None),
        (["new", "--help"], "help", None),
        (["dev", "--help"], "help", None),
        (["--version"], "version", None),
        (["-V"], "version", None),
        (["new", "My-app_123"], "new", "My-app_123"),
        (["dev"], "dev", None),
        (["new", ""], "error", None),
        (["new", "hello\n"], "error", None),
        (["new", "1bad"], "error", None),
        (["new", "app.name"], "error", None),
        (["unknown"], "error", None),
    ],
)
def test_parser_command_contract(
    args: list[str], action: str, name: str | None
) -> None:
    """The parser returns documented actions, arguments, and exit statuses."""
    parsed = parse_argv(args)
    assert parsed.action == action
    assert parsed.name == name
    assert parsed.exit_code == (2 if action == "error" else 0)
