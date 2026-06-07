"""Dispatch parsed CLI commands to Python handlers."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from boltra import __version__
from boltra.cli.parser import ParsedCommand, parse_argv
from boltra.dev.server import run_dev_server
from boltra.project.generator import ProjectError, create_project

if TYPE_CHECKING:
    from pathlib import Path


def execute(argv: list[str], *, cwd: Path | None = None) -> int:
    """Parse ``argv`` and run the matching command handler."""
    parsed = parse_argv(argv)
    return _dispatch(parsed, cwd=cwd)


def _dispatch(parsed: ParsedCommand, *, cwd: Path | None = None) -> int:
    """Route a parsed command to its handler."""
    if parsed.action == "help":
        sys.stdout.write(parsed.help_text or "")
        if parsed.help_text and not parsed.help_text.endswith("\n"):
            sys.stdout.write("\n")
        return 0

    if parsed.action == "version":
        sys.stdout.write(f"{__version__}\n")
        return 0

    if parsed.action == "new":
        return _handle_new(parsed.name, cwd=cwd)

    if parsed.action == "dev":
        return run_dev_server(cwd=cwd)

    if parsed.action == "error":
        sys.stderr.write(parsed.error_message or "error\n")
        if parsed.error_message and not parsed.error_message.endswith("\n"):
            sys.stderr.write("\n")
        return parsed.exit_code

    sys.stderr.write(f"unknown action: {parsed.action}\n")
    return 1


def _handle_new(name: str | None, *, cwd: Path | None = None) -> int:
    """Run the ``boltra new`` project generator."""
    if name is None:
        sys.stderr.write("error: project name is required\n")
        return 2

    try:
        project_dir = create_project(name, cwd=cwd)
    except ProjectError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1

    sys.stdout.write(f"Created project '{name}' in {project_dir}\n\n")
    sys.stdout.write("Next steps:\n")
    sys.stdout.write(f"  cd {name}\n")
    sys.stdout.write("  uv sync                    # creates a local .venv\n")
    sys.stdout.write("  boltra dev                 # start server with reload\n")
    sys.stdout.write("\n")
    sys.stdout.write(
        "Tip: if another venv is active, run `deactivate` first "
        "or open a new terminal.\n"
    )
    return 0
