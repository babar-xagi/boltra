"""Parse commands with Python's standard-library ``argparse``."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any, NoReturn

from boltra.apps.validation import validate_app_name
from boltra.project.validation import validate_project_name


class _ParserExit(Exception):
    """Carry argparse output back to the dispatcher without printing it."""

    def __init__(self, code: int, text: str) -> None:
        self.code = code
        self.text = text


class _ArgumentParser(argparse.ArgumentParser):
    """Return terminal messages to the CLI instead of printing or exiting."""

    def print_help(self, file: Any = None) -> NoReturn:
        raise _ParserExit(0, self.format_help())

    def error(self, message: str) -> NoReturn:
        raise _ParserExit(2, f"{self.format_usage()}{self.prog}: error: {message}\n")


@dataclass(frozen=True, slots=True)
class ParsedCommand:
    """Structured CLI parse result consumed by the dispatcher."""

    action: str
    name: str | None = None
    help_text: str | None = None
    error_message: str | None = None
    exit_code: int = 0


def _project_name(value: str) -> str:
    """Adapt a domain validation error to argparse without losing its message."""
    try:
        return validate_project_name(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _app_name(value: str) -> str:
    """Use the same import-safe app-name rules as the app generator."""
    try:
        return validate_app_name(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def parse_argv(args: list[str]) -> ParsedCommand:
    """Parse arguments without a program name, returning a command or message."""
    parser = _ArgumentParser(
        prog="boltra",
        description="Boltra — Django-like productivity for FastAPI projects.",
    )
    parser.add_argument("-V", "--version", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    new_parser = subparsers.add_parser("new", help="Create a new FastAPI project.")
    new_parser.add_argument(
        "name",
        type=_project_name,
        help="Project name (letters, digits, hyphens, underscores).",
    )
    subparsers.add_parser("dev", help="Run the development server with auto-reload.")
    add_parser = subparsers.add_parser("add", help="Add a component to this project.")
    components = add_parser.add_subparsers(dest="component", required=True)
    app_parser = components.add_parser(
        "app", help="Create and register a FastAPI router."
    )
    app_parser.add_argument(
        "name", type=_app_name, help="Lowercase Python package name."
    )

    try:
        ns = parser.parse_args(args)
    except _ParserExit as exc:
        if exc.code == 0:
            return ParsedCommand(action="help", help_text=exc.text)
        return ParsedCommand(
            action="error",
            error_message=exc.text,
            exit_code=exc.code,
        )

    if ns.version:
        return ParsedCommand(action="version")
    if ns.command == "new":
        return ParsedCommand(action="new", name=ns.name)
    if ns.command == "dev":
        return ParsedCommand(action="dev")
    if ns.command == "add":
        return ParsedCommand(action="add_app", name=ns.name)
    # No subcommand means general help; argparse already rejected unknown names.
    return ParsedCommand(action="help", help_text=parser.format_help())
