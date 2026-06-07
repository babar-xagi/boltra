# Tooling & CI

## Package manager: uv

| Command | Purpose |
|---------|---------|
| `uv sync --group dev` | Install deps + build PyO3 extension |
| `uv run <cmd>` | Run tool inside project venv |
| `uv lock` | Refresh `uv.lock` after dependency changes |
| `uv run maturin develop --uv` | Incremental native extension rebuild |

Lockfile: `uv.lock` — commit this for reproducible CI and contributor setups.

## Python quality tools

Configured in `pyproject.toml`.

| Tool | Command | Config section |
|------|---------|----------------|
| **Ruff** (lint) | `uv run ruff check .` | `[tool.ruff]`, `[tool.ruff.lint]` |
| **Ruff** (format) | `uv run ruff format --check .` | `[tool.ruff.format]` |
| **mypy** | `uv run mypy src` | `[tool.mypy]` |
| **pytest** | `uv run pytest` | `[tool.pytest.ini_options]` |

### mypy notes

- `mypy_path = "src"` for src layout
- `boltra._native` typed via `_native.pyi` stub
- `strict = true` on all package code

## Pre-commit

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

Hooks (`.pre-commit-config.yaml`):

- ruff + ruff-format
- mypy (src only)
- trailing whitespace, EOF, yaml/toml checks, large files

## Rust tooling

| Command | Purpose |
|---------|---------|
| `cargo test --workspace` | Run Rust unit tests |
| `cargo build --release` | Optimized build (LTO enabled) |
| `cargo clippy` | Lint (optional, not in CI yet) |

Build artifacts: `target/` (gitignored).

## GitHub Actions CI

**File:** `.github/workflows/ci.yml`

Matrix:

- OS: `ubuntu-latest`, `windows-latest`
- Python: `3.12`, `3.14` (Windows skips 3.12 to keep matrix lean)

Steps per job:

1. Checkout
2. Install Rust (`dtolnay/rust-toolchain@stable`)
3. Install uv (`astral-sh/setup-uv@v5`)
4. `uv python install <version>`
5. `uv sync --group dev` (with `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1`)
6. `uv run ruff check .`
7. `uv run ruff format --check .`
8. `uv run mypy src`
9. `uv run pytest`
10. `uv run pytest -k native_disabled` with `BOLTRA_DISABLE_NATIVE=1`
11. `cargo test --workspace`

## Quality gates (every PR)

From `CONTRIBUTING.md` and `doc/plan/phase.md`:

- [ ] Unit tests for new logic
- [ ] Type hints on public APIs
- [ ] Ruff lint + format clean
- [ ] mypy clean
- [ ] Docstrings on public symbols
- [ ] No TODO without issue link
- [ ] Changelog entry in `doc/plan/CHANGELOG.md`

ORM/Rust phases additionally require benchmarks and fallback tests.
