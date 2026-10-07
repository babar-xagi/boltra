# Changelog

All notable changes to Boltra are documented here. Entries follow
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the phased roadmap
in [`phase.md`](phase.md).

## [Unreleased] — 0.5.0

### Changed

- Clarified Boltra's general-purpose, multi-framework direction and separated
  current FastAPI support from planned Flask, Django-based, Django Bolt, TurboAPI,
  and future integrations. Added a framework adapter design and verified sources.

- Migrated the package to pure Python: argparse CLI, Hatchling build backend,
  platform-independent wheel, and no project-owned native extension/toolchain.
- Moved CLI implementation to `cli/cli.py` and shared name validation to
  `project/validation.py`; removed old native APIs and internal CLI entry modules.
- Extracted generated code into readable packaged template assets.
- Organized tests by CLI, project, and dev-server responsibility.
- Rewrote README/user/developer guides with examples and a detailed file reference.
- Replaced native CI/publication steps with Python quality/test/build workflows.

### Fixed

- Reject trailing-newline project names and preserve validation details.
- Return subcommand help/errors once, with the correct message and exit status.
- Honor fallback settings list/boolean overrides and reject invalid booleans.
- Accept packaged app targets and handle invalid UTF-8 configuration.
- Format IPv6 URLs and handle filesystem/process-launch failures cleanly.
- Clean partial generated files without deleting unrelated content.
- Make Windows development reload restart only its worker, avoiding signal hangs.

### Added

- `python -m boltra` and the published `py.typed` marker.
- Installed-wheel, resource, and source-archive verification tests.
- Pydantic/Uvicorn/coverage development dependencies and real repeated-reload tests.

Older entries below describe the historical implementations of those releases.

## [0.4.0] - 2026-06-29

### Added - Phase 4 (Settings & `.env`)

- Generated projects now include `.env.example`
- Generated `settings.py` exposes a typed `Settings` object and cached `settings`
  instance
- `main.py` now reads API title and debug mode from generated settings
- Generated projects declare `pydantic-settings` alongside FastAPI and uvicorn
- Project generator tests cover `.env` loading through generated settings
- Generated projects now include explicit `host` and `port` defaults for
  `boltra dev`

### Fixed

- `boltra dev` now exits cleanly on Ctrl+C instead of printing a traceback
- `boltra dev` now reads optional `host` and `port` values from
  `[tool.boltra]`
- Generated home routes now return a normal JSON dict instead of malformed
  double-brace template output
- `pyproject.toml` files saved with a UTF-8 BOM are accepted by project
  detection and dev-server config loading

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
