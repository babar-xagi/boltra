# Boltra

**Django-like productivity for FastAPI projects.**

Boltra is a FastAPI development kit for building modern backend systems faster. It generates direct FastAPI code and adds structure, CLI automation, apps, ORM, admin, auth, workers, and **Rust-powered performance modules** — without hiding FastAPI.

```bash
boltra --help
boltra --version
boltra new myapp
cd myapp && uv sync && boltra dev

# Coming in Phase 5+
boltra add orm
```

## Status

Early development. See [`doc/plan/phase.md`](doc/plan/phase.md) for the phased roadmap.

| Track | Phases | Focus |
|-------|--------|-------|
| Foundation | 0–8 | CLI, project generator, apps, settings |
| ORM Core | 9–18 | From-scratch async ORM (Python) |
| ORM Rust | 19–21 | SQL builder, row decoder, pool helpers |
| Batteries | 22–28 | Admin, auth, worker, AI, Docker, tests |
| Hardening | 29–32 | Observability, security, benchmarks |
| V1 | 33 | Stable release |

## Stack

| Layer | Tool | Role |
|-------|------|------|
| Python | **uv** | Fast package manager and virtualenv |
| Python ↔ Rust | **maturin** + **PyO3** | Native extension build and FFI |
| Rust | **cargo** | Hot-path acceleration (SQL, row decode) |
| Quality | ruff, mypy, pytest, pre-commit | Lint, types, tests |

## Requirements

- Python ≥ 3.12
- [uv](https://docs.astral.sh/uv/) (package manager)
- Rust ≥ 1.85 (maturin compiles `boltra._native` on install)

## Development

```bash
# Install Python (uv manages the venv automatically)
uv sync --group dev

# Rebuild the PyO3 extension after Rust changes
uv run maturin develop --uv

# Run quality checks
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest

# Verify Python fallback when native is disabled
BOLTRA_DISABLE_NATIVE=1 uv run pytest

# Install pre-commit hooks
uv run pre-commit install
```

### Native extension

The Rust crate `crates/boltra-core` exposes `boltra._native` via PyO3. Python code uses `boltra.native.is_available()` and always has a fallback path.

```python
import boltra

boltra.is_available()      # True when PyO3 extension is loaded
boltra.native_version()    # "0.4.0"
```

Disable native acceleration (for testing or unsupported platforms):

```bash
BOLTRA_DISABLE_NATIVE=1 uv run pytest
```

## Repository layout

```text
boltra/
├── src/boltra/              # Python package
│   ├── native.py            # Rust bridge + fallback
│   └── _native.pyi          # Type stubs for PyO3 module
├── crates/boltra-core/      # PyO3 extension (maturin)
├── tests/
├── benchmarks/
├── doc/
│   ├── user/                # end-user guides
│   ├── developer/           # contributor docs
│   └── plan/
├── pyproject.toml           # maturin build backend
├── Cargo.toml               # Rust workspace (release LTO enabled)
└── uv.lock
```

## Documentation

| Audience | Start here |
|----------|------------|
| **Users** | [doc/user/](doc/user/README.md) — install, CLI |
| **Developers** | [doc/developer/](doc/developer/README.md) — architecture, files, workflow |
| **Roadmap** | [doc/plan/phase.md](doc/plan/phase.md) |
| **Rusjango migration** | [doc/plan/rusjango-migration.md](doc/plan/rusjango-migration.md) |
| **Changelog** | [doc/plan/CHANGELOG.md](doc/plan/CHANGELOG.md) |

- [Project vision](boltra-doc.md)
- [Contributing](CONTRIBUTING.md)

## License

MIT — see [LICENSE](LICENSE).
