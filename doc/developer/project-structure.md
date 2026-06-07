# Project Structure

Complete map of the Boltra repository as of Phase 2.

```text
boltra/
├── .cargo/
│   └── config.toml              # PYO3_USE_ABI3_FORWARD_COMPATIBILITY for Python 3.14
├── .github/
│   └── workflows/
│       └── ci.yml               # uv + maturin + ruff + mypy + pytest + cargo test
├── .pre-commit-config.yaml      # ruff, mypy, file hygiene hooks
├── benchmarks/
│   └── README.md                # Placeholder for ORM benchmarks (Phase 9+)
├── boltra-doc.md                # Product vision and full specification
├── Cargo.toml                   # Rust workspace root + release profile
├── Cargo.lock                   # Locked Rust dependencies
├── CONTRIBUTING.md              # PR rules and quality gates
├── crates/
│   ├── boltra-cli/
│   │   ├── Cargo.toml           # clap CLI parser crate
│   │   └── src/lib.rs           # Cli, Commands, parse_args(), name validation
│   └── boltra-core/
│       ├── Cargo.toml           # PyO3 cdylib + boltra-cli dependency
│       └── src/lib.rs           # _native module, parse_argv PyO3 bridge
├── doc/
│   ├── README.md                # Documentation index
│   ├── developer/               # Contributor docs (this folder)
│   ├── plan/
│   │   ├── phase.md             # Phased roadmap
│   │   └── CHANGELOG.md         # Shipped changes log
│   └── user/                    # End-user docs
├── LICENSE                      # MIT
├── pyproject.toml               # Python project + maturin + tooling config
├── README.md                    # Project overview
├── src/
│   └── boltra/
│       ├── __init__.py          # Package version, re-exports native helpers
│       ├── _native.pyi          # Type stubs for Rust module (mypy)
│       ├── native.py            # Rust bridge + BOLTRA_DISABLE_NATIVE fallback
│       ├── cli/
│       │   ├── __init__.py      # Exports execute, parse_argv, run
│       │   ├── main.py          # Console entry point
│       │   ├── parser.py        # clap native + argparse fallback
│       │   └── dispatch.py    # Route parsed commands to handlers
│       └── project/
│           ├── __init__.py
│           ├── generator.py     # create_project()
│           └── templates.py     # main.py, settings.py, pyproject.toml
├── tests/
│   ├── __init__.py
│   ├── test_cli.py              # CLI parse + dispatch tests
│   ├── test_native.py           # Native bridge and fallback tests
│   └── test_project.py          # boltra new integration tests
├── uv.lock                      # Locked Python dependencies
└── .gitignore
```

## File reference by layer

### Root config

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package metadata, `[project.scripts]`, maturin config, ruff/mypy/pytest |
| `Cargo.toml` | Workspace members (`boltra-cli`, `boltra-core`), `pyo3` + `clap`, release LTO |
| `uv.lock` | Reproducible Python env via uv |
| `.pre-commit-config.yaml` | Local git hooks |

### Python (`src/boltra/`)

| File | Created | Purpose |
|------|---------|---------|
| `__init__.py` | Phase 0 | `__version__`, `is_available()`, `native_version()` |
| `native.py` | Phase 0 | Lazy import of `boltra._native`, env-based disable |
| `_native.pyi` | Phase 0 | Static types for the maturin-built extension |
| `cli/parser.py` | Phase 2 | `parse_argv()` — clap via PyO3 or argparse fallback |
| `cli/dispatch.py` | Phase 2 | `execute()` — help, version, `new` handler |
| `cli/main.py` | Phase 1 | `run()` console entry point |
| `project/generator.py` | Phase 2 | `create_project()`, collision checks |
| `project/templates.py` | Phase 2 | Generated file templates |

### Rust

| Crate / file | Created | Purpose |
|--------------|---------|---------|
| `boltra-cli/src/lib.rs` | Phase 2 | clap `Cli`, `Commands::New`, `parse_args()` |
| `boltra-core/src/lib.rs` | Phase 0–2 | PyO3 `_native`: `parse_argv`, `cli_help`, `version` |

### Tests (`tests/`)

| File | Covers |
|------|--------|
| `test_native.py` | Extension import, `parse_argv`, env disable, fallback |
| `test_cli.py` | Help, version, clap parse, entry point |
| `test_project.py` | File generation, import, collisions, CLI integration |

### Documentation (`doc/`)

| Path | Audience |
|------|----------|
| `doc/user/` | Installation, CLI usage |
| `doc/developer/` | Architecture, structure, tooling |
| `doc/plan/` | Roadmap and changelog |

## What gets generated at build time

| Output | Tool | Location |
|--------|------|----------|
| `boltra._native*.pyd` / `.so` | maturin | Inside `.venv` site-packages |
| `target/` | cargo | Rust build artifacts (gitignored) |
| `.venv/` | uv | Virtual environment (gitignored) |

## Phases and files

When a new phase lands, update:

1. This file (or add a phase note)
2. `doc/plan/CHANGELOG.md`
3. `doc/user/` if user-facing behavior changes
4. `tests/` for new public APIs
