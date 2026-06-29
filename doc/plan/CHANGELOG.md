# Changelog

All notable changes to Boltra are documented here. Entries follow
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the phased roadmap
in [`phase.md`](phase.md).

## [Unreleased]

## [0.4.0] - 2026-06-29

### Added - Phase 4 (Settings & `.env`)

- Generated projects now include `.env.example`
- Generated `settings.py` exposes a typed `Settings` object and cached `settings`
  instance
- `main.py` now reads API title and debug mode from generated settings
- Generated projects declare `pydantic-settings` alongside FastAPI and uvicorn
- Project generator tests cover `.env` loading through generated settings

### Fixed

- `boltra dev` now exits cleanly on Ctrl+C instead of printing a traceback

## [0.3.1] - 2026-06-09

### Fixed

- PyPI wheels now use **abi3-py312**; one wheel per platform supports Python
  **3.12, 3.13, and 3.14+**
- Publish workflow builds with Python 3.14 on Linux, Windows, and macOS
- CI matrix extended to Python 3.13
- Switched PyPI upload from deprecated `maturin upload` to `uv publish`

## [0.3.0] - 2026-06-06

### Added - Phase 3 (Dev Server)

- **`boltra dev`** reads `[tool.boltra]` from `pyproject.toml`, runs uvicorn
  with `--reload`
- `src/boltra/dev/` config loader (`tomllib`) and server launcher
- Uses `uv run uvicorn` (falls back to project `.venv` Python)
- Prints mode, app path, URL (`/`), and docs URL (`/docs`)
- Rust clap `dev` subcommand and Python dispatch handler
- Integration test: serves `/` and `/docs`
- User docs updated for `boltra dev`
- `doc/plan/rusjango-migration.md` feature porting priority from Rusjango to
  Boltra (P0-P4)
- Rusjango migration summary section in `doc/plan/phase.md`

### Fixed

- Generated `pyproject.toml` no longer depends on unpublished `boltra` (fixes
  `uv sync` in new projects)
- Added `requires-python = ">=3.12"` to generated projects
- Next-steps message notes `deactivate` when parent venv is active

## [0.2.0] - 2026-06-06

### Added - Phase 2 (Project Generator)

- **`boltra new <name>`** generates `main.py`, `settings.py`, `pyproject.toml`
- Direct FastAPI `main.py` (no wrapper) per product spec
- Project name validation; refuses to overwrite existing directories
- Success message with next steps (`cd`, `uv sync`, uvicorn)
- **Rust clap + Python hybrid CLI:**
  - `crates/boltra-cli` clap parser and validation
  - `boltra._native.parse_argv()` PyO3 bridge
  - `boltra.cli.parser` / `dispatch` Python execution and argparse fallback
- `src/boltra/project/` generator and templates
- Integration tests: file creation, import check, collision handling
- Developer docs: `cli-architecture.md`, `project-generator.md`
- User docs: `boltra new` in `doc/user/cli.md`

### Changed

- Removed **typer** dependency; CLI now uses clap (Rust) + argparse (fallback)
- CLI entry point calls `execute(sys.argv[1:])` instead of Typer app

## [0.1.0] - 2026-06-06

### Added - Phase 1 (Minimal CLI Package)

- `boltra --help` and `boltra --version` / `boltra -V` via Typer
- Console script entry point: `boltra = boltra.cli.main:run`
- `src/boltra/cli/` module (`main.py`, `__init__.py`)
- `typer` runtime dependency
- CLI tests in `tests/test_cli.py`
- Documentation structure:
  - `doc/README.md` documentation index
  - `doc/user/` installation and CLI guides for end users
  - `doc/developer/` architecture, project structure, tooling, workflow

### Added - Phase 0 (Repository & Engineering Standards)

- Monorepo layout: `src/boltra/`, `crates/`, `tests/`, `benchmarks/`, `doc/`
- Python package (`boltra` v0.1.0) with `boltra.native` bridge
- **PyO3 + maturin** native extension (`boltra._native` from
  `crates/boltra-core`)
- **uv** package manager (`uv sync --group dev`, `uv.lock`)
- Rust release profile: LTO + single codegen unit for hot-path performance
- `BOLTRA_DISABLE_NATIVE` env flag for Python fallback testing
- Tooling: Ruff (lint + format), pytest, mypy, pre-commit
- GitHub Actions CI: uv + maturin build on Linux/Windows, Python 3.12/3.14
- `README.md`, `LICENSE` (MIT), `CONTRIBUTING.md`

[Unreleased]: https://github.com/babar-xagi/boltra/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/babar-xagi/boltra/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/babar-xagi/boltra/releases/tag/v0.3.1
[0.3.0]: https://github.com/babar-xagi/boltra/releases/tag/v0.3.0
[0.2.0]: https://github.com/babar-xagi/boltra/releases/tag/v0.2.0
[0.1.0]: https://github.com/babar-xagi/boltra/releases/tag/v0.1.0
