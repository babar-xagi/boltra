"""CLI argument parsing — Rust clap (native) with pure-Python fallback."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from typing import Any, Final

from boltra.native import is_available

_PROJECT_NAME_RE: Final = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")


@dataclass(frozen=True, slots=True)
class ParsedCommand:
    """Structured CLI parse result consumed by the dispatcher."""

    action: str
    name: str | None = None
    help_text: str | None = None
    error_message: str | None = None
    exit_code: int = 0


def _dict_to_parsed(data: dict[str, Any]) -> ParsedCommand:
    """Convert a native parser dict into a ``ParsedCommand``."""
    return ParsedCommand(
        action=str(data["action"]),
        name=data.get("name"),
        help_text=data.get("help_text"),
        error_message=data.get("error_message"),
        exit_code=int(data.get("exit_code", 2)),
    )


def validate_project_name(name: str) -> str:
    """Validate a project name using the same rules as the Rust clap parser."""
    if not name:
        msg = "project name cannot be empty"
        raise argparse.ArgumentTypeError(msg)
    if "/" in name or "\\" in name or "." in name:
        msg = f"project name '{name}' must not contain path separators or dots"
        raise argparse.ArgumentTypeError(msg)
    if not _PROJECT_NAME_RE.match(name):
        msg = (
            f"project name '{name}' must start with a letter and contain only "
            "letters, digits, hyphens, and underscores"
        )
        raise argparse.ArgumentTypeError(msg)
    return name


def parse_argv_native(args: list[str]) -> ParsedCommand:
    """Parse argv with the Rust clap parser exposed via PyO3."""
    import boltra._native as _native

    return _dict_to_parsed(_native.parse_argv(args))


def parse_argv_python(args: list[str]) -> ParsedCommand:
    """Pure-Python argparse fallback when the native extension is unavailable."""
    parser = argparse.ArgumentParser(
        prog="boltra",
        description="Boltra — Django-like productivity for FastAPI projects.",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-V", "--version", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    new_parser = subparsers.add_parser("new", help="Create a new FastAPI project.")
    new_parser.add_argument(
        "name",
        type=validate_project_name,
        help="Project name (letters, digits, hyphens, underscores).",
    )
    subparsers.add_parser("dev", help="Run the development server with auto-reload.")

    try:
        ns = parser.parse_args(args)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 2
        if code == 0:
            return ParsedCommand(action="help", help_text=parser.format_help())
        return ParsedCommand(
            action="error",
            error_message="invalid arguments",
            exit_code=code if isinstance(code, int) else 2,
        )

    if ns.help and not ns.command:
        return ParsedCommand(action="help", help_text=parser.format_help())
    if ns.version:
        return ParsedCommand(action="version")
    if ns.command == "new":
        return ParsedCommand(action="new", name=ns.name)
    if ns.command == "dev":
        return ParsedCommand(action="dev")
    if not ns.command:
        return ParsedCommand(action="help", help_text=parser.format_help())

    return ParsedCommand(
        action="error",
        error_message="unknown command",
        exit_code=2,
    )


def parse_argv(args: list[str]) -> ParsedCommand:
    """Parse CLI arguments using clap (native) or argparse (fallback)."""
    if is_available():
        return parse_argv_native(args)
    return parse_argv_python(args)
