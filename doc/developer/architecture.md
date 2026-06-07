# Architecture

## Overview

Boltra is a **monorepo** combining:

- A **Python package** (`boltra`) — CLI, project tooling, ORM (later), batteries
- A **Rust workspace** (`crates/`) — PyO3 native extensions for hot paths
- **maturin** — builds and ships the Rust extension as `boltra._native`

```text
┌─────────────────────────────────────────────────────────┐
│                     User / Developer                     │
│                    `boltra` CLI (typer)                  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│              Python package (src/boltra/)                │
│  cli/ · native.py · (future: project, orm, apps, …)   │
└─────────────┬───────────────────────┬───────────────────┘
              │                       │
              │ import (optional)     │ pure Python fallback
              ▼                       ▼
┌─────────────────────────┐   ┌──────────────────────────┐
│  boltra._native (PyO3)  │   │  Python implementations  │
│  crates/boltra-core     │   │  (always available)      │
└─────────────────────────┘   └──────────────────────────┘
```

## Design decisions

### uv + maturin + PyO3

| Choice | Why |
|--------|-----|
| **uv** | Fast dependency resolution and reproducible lockfile (`uv.lock`) |
| **maturin** | Standard way to build PyO3 extensions; editable dev builds |
| **PyO3 0.28** | Mature Python ↔ Rust FFI; extension module for performance |

### Native bridge pattern

`boltra.native` is the **single entry point** for checking whether Rust acceleration is active:

```python
from boltra.native import is_available, native_version
```

Rules:

- Try `import boltra._native` once; cache the result
- Respect `BOLTRA_DISABLE_NATIVE` for tests and fallback verification
- Log once at INFO if native is missing; never crash the app

Future ORM code will follow the same pattern: delegate to `_native` when `is_available()`, else use Python.

### CLI layer

Phase 1 uses **Typer** for the `boltra` console script. Subcommands will live in `boltra.cli` and call internal modules (`boltra.project`, `boltra.apps`, etc.) as phases add them.

Entry point (in `pyproject.toml`):

```toml
[project.scripts]
boltra = "boltra.cli.main:run"
```

### Rust performance profile

Release builds use aggressive optimization for future ORM hot paths:

```toml
# Cargo.toml
[profile.release]
lto = "fat"
codegen-units = 1
strip = "symbols"
```

## Module boundaries (current and planned)

| Module | Phase | Responsibility |
|--------|-------|----------------|
| `boltra.cli` | 1 | Command-line interface |
| `boltra.native` | 0 | Rust bridge + fallback |
| `boltra.project` | 2 | Project generator |
| `boltra.dev` | 3 | Dev server wrapper |
| `boltra.apps` | 4+ | App scaffolding |
| `boltra.orm` | 9–21 | Async ORM (Python + Rust) |

Keep **clean boundaries** — CLI should not contain ORM logic; internal packages talk through well-defined APIs.

## Async-first (future)

Public database APIs will be `async`. The CLI may remain sync where appropriate; generated project code and ORM will use `async`/`await` throughout.
