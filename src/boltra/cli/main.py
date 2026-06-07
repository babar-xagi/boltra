"""Boltra CLI entry point — Rust clap parses, Python executes."""

from __future__ import annotations

import sys

from boltra.cli.dispatch import execute


def run() -> None:
    """Console script entry point for ``boltra``."""
    raise SystemExit(execute(sys.argv[1:]))


if __name__ == "__main__":
    run()
