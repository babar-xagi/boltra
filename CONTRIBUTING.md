# Contributing to Boltra

Thank you for your interest in Boltra. This project follows a **phased roadmap** — please read [`doc/plan/phase.md`](doc/plan/phase.md) before opening a PR.

## Stack

- **uv** — Python package manager (not pip directly)
- **maturin** + **PyO3** — Rust native extensions (`boltra._native`)
- **cargo** — Rust workspace under `crates/`

## Getting started

1. Fork and clone the repository.
2. Install [uv](https://docs.astral.sh/uv/) and Rust (≥ 1.85).
3. Sync dependencies (maturin builds the PyO3 extension automatically):

   ```bash
   uv sync --group dev
   uv run pre-commit install
   ```

4. After editing Rust code, rebuild the extension:

   ```bash
   uv run maturin develop --uv
   ```

## Quality gates

Every PR must pass:

| Check | Command |
|-------|---------|
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format --check .` |
| Types | `uv run mypy src` |
| Tests | `uv run pytest` |
| Native fallback | `BOLTRA_DISABLE_NATIVE=1 uv run pytest` |
| Rust unit tests | `cargo test --workspace` |
| Pre-commit | `uv run pre-commit run --all-files` |

Additional rules:

- **Type hints** on all public functions and classes.
- **Docstrings** on every public API symbol.
- **No TODO without an issue link** in merged code.
- **Tests** for all new public logic (target ≥ 90% coverage on new code).
- **Benchmark before Rust** — hot-path Rust code must beat the Python baseline.
- **Python fallback** — every native feature needs a working pure-Python path.

## Branch and commit style

- Branch names: `phase-N/short-description` or `fix/short-description`
- Commits: imperative mood, e.g. `Add typer CLI skeleton for Phase 1`
- Keep PRs focused on a single phase deliverable when possible.

## Phase workflow

1. Check the current phase exit criteria in `doc/plan/phase.md`.
2. Implement only what that phase specifies.
3. Add a changelog entry under `doc/plan/CHANGELOG.md`.
4. Record a manual smoke test in your PR description (command + expected output).

## Documentation

When you ship a phase, update:

- [`doc/plan/CHANGELOG.md`](doc/plan/CHANGELOG.md) — what changed
- [`doc/user/`](doc/user/README.md) — if end users see new behavior
- [`doc/developer/`](doc/developer/README.md) — if files, architecture, or workflow change

## Questions

Open a GitHub issue with the `question` label, or refer to [`boltra-doc.md`](boltra-doc.md) and [`doc/developer/`](doc/developer/README.md) for architecture decisions.
