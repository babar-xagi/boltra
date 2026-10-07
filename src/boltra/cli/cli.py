"""CLI entry point and command routing; parsing lives in ``parser.py``.

Keep terminal output here. Project generation and server startup expose ordinary
Python functions, so callers and tests can use them without invoking a shell.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from boltra import __version__
from boltra.apps import AppError, add_app
from boltra.cli.parser import parse_argv
from boltra.dev.server import run_dev_server
from boltra.project.generator import ProjectError, create_project

if TYPE_CHECKING:
    from pathlib import Path


def run() -> None:
    """Console-script entry point; translate the command result into an exit code."""
    raise SystemExit(execute(sys.argv[1:]))


def execute(argv: list[str], *, cwd: Path | None = None) -> int:
    """Execute CLI arguments without the program name and return an exit status.

    ``cwd`` allows a caller to select a working directory without changing the
    process-wide directory. It is particularly useful for generators and tests.
    """
    command = parse_argv(argv)

    # The parser returns help and errors as data; only this layer prints them.
    # That keeps output predictable and avoids argparse printing messages twice.
    if command.action == "help":
        sys.stdout.write(command.help_text or "")
        return 0
    if command.action == "version":
        sys.stdout.write(f"{__version__}\n")
        return 0
    if command.action == "new":
        return _new_project(command.name, cwd=cwd)
    if command.action == "dev":
        return run_dev_server(cwd=cwd)
    if command.action == "add_app":
        return _add_app(command.name, cwd=cwd)
    if command.action == "error":
        sys.stderr.write(command.error_message or "error: invalid arguments\n")
        return command.exit_code

    sys.stderr.write(f"error: unknown command action '{command.action}'\n")
    return 1


def _new_project(name: str | None, *, cwd: Path | None = None) -> int:
    """Create a project, convert domain errors, and show actionable next steps."""
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
    sys.stdout.write("  uv sync                    # install app dependencies\n")
    sys.stdout.write("  boltra dev                 # start server with reload\n\n")
    sys.stdout.write("Tip: deactivate another active venv before running uv sync.\n")
    return 0


def _add_app(name: str | None, *, cwd: Path | None = None) -> int:
    """Create a router package and show its immediately available endpoint."""
    if name is None:
        sys.stderr.write("error: app name is required\n")
        return 2
    try:
        directory = add_app(name, cwd=cwd)
    except AppError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
    sys.stdout.write(f"Created app '{name}' in {directory}\n")
    sys.stdout.write(f"Registered endpoint: /{name}/\n")
    sys.stdout.write("Next: boltra dev, then open the endpoint or /docs.\n")
    return 0
