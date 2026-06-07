# Developer Documentation

Technical documentation for contributors working on the Boltra codebase.

## Contents

| Guide | Description |
|-------|-------------|
| [Architecture](architecture.md) | High-level design, Python ↔ Rust split |
| [CLI architecture](cli-architecture.md) | Rust clap parse + Python dispatch |
| [Project generator](project-generator.md) | `boltra new` templates and validation |
| [Dev server](dev-server.md) | `boltra dev` config and uvicorn launcher |
| [Releasing](releasing.md) | GitHub + PyPI publish checklist |
| [Project structure](project-structure.md) | Every folder and key file explained |
| [Python package](python-package.md) | `src/boltra/` modules and APIs |
| [Rust native layer](rust-native.md) | PyO3, maturin, `crates/boltra-core` |
| [Tooling & CI](tooling.md) | uv, ruff, mypy, pytest, pre-commit, GitHub Actions |
| [Development workflow](development-workflow.md) | Day-to-day commands and phase rules |

## Quick start for developers

```bash
uv sync --group dev
uv run pre-commit install
uv run pytest
uv run boltra --help
```

## Principles (from the roadmap)

1. **Async-first** — public database APIs will be `async`
2. **Rust where it wins** — hot paths in Rust; Python always has a fallback
3. **Direct FastAPI** — generated projects use real FastAPI, no hidden wrapper
4. **One phase at a time** — see [`doc/plan/phase.md`](../plan/phase.md)
5. **Benchmark before Rust** — native code must beat Python baseline

## Current phase status

| Phase | Status | Summary |
|-------|--------|---------|
| 0 | Done | Repo layout, uv, maturin, PyO3, CI |
| 1 | Done | `boltra --help`, `boltra --version` CLI |
| 2 | Done | `boltra new`, Rust clap + Python handlers |
| 3 | Done | `boltra dev` dev server |
| 4 | Next | Pydantic settings & `.env` |

Track shipped work in [CHANGELOG](../plan/CHANGELOG.md).

## Related docs

- [User docs](../user/README.md) — installation and CLI for end users
- [boltra-doc.md](../../boltra-doc.md) — full product vision
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — PR rules and quality gates
