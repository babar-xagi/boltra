# Development Workflow

Day-to-day guide for contributing to Boltra.

## First-time setup

```bash
git clone <repo>
cd boltra
uv sync --group dev
uv run pre-commit install
```

Verify:

```bash
uv run pytest -v
uv run boltra --help
uv run boltra --version
```

## Daily loop

```bash
# 1. Create a branch
git checkout -b phase-N/short-description

# 2. Edit code (Python and/or Rust)

# 3. If you changed Rust:
uv run maturin develop --uv

# 4. Run checks
uv run ruff check .
uv run ruff format .
uv run mypy src
uv run pytest -v

# 5. Pre-commit (optional but recommended)
uv run pre-commit run --all-files
```

## Phase-based development

Boltra ships in **phases**. Before coding:

1. Read the current phase in [`doc/plan/phase.md`](../plan/phase.md)
2. Implement **only** that phase's deliverables
3. Meet **exit criteria** before moving on
4. Update [`doc/plan/CHANGELOG.md`](../plan/CHANGELOG.md)
5. Update docs:
   - `doc/user/` — if end users see new behavior
   - `doc/developer/` — if architecture or files change

### Phase 0 — done

Repo layout, uv, maturin, PyO3, CI, pre-commit.

### Phase 1 — done

`boltra --help`, `boltra --version`, CLI entry point, tests.

### Phase 2 — done

`boltra new <name>` — Rust clap parses, Python generates project files.

### Phase 3 — next

`boltra dev` — uvicorn dev server with reload.

## Adding a feature checklist

- [ ] Code in correct module (`cli`, `native`, future `project`, etc.)
- [ ] Type hints + docstrings on public API
- [ ] Tests in `tests/`
- [ ] `uv lock` if dependencies changed
- [ ] User doc update (`doc/user/`)
- [ ] Developer doc update (`doc/developer/`)
- [ ] Changelog entry (`doc/plan/CHANGELOG.md`)
- [ ] Manual smoke test recorded in PR description

Example smoke tests:

```bash
uv run boltra --version
# Expected: 0.2.0

uv run boltra new demo
# Expected: creates demo/ with main.py, settings.py, pyproject.toml

cd demo && uv run python -c "from main import app; print(app.title)"
# Expected: Demo API
```

## Rust + Python changes

When touching both layers:

1. Edit `crates/boltra-core/src/lib.rs`
2. Update `src/boltra/_native.pyi` if Python API changes
3. Update `src/boltra/native.py` if bridge logic changes
4. `uv run maturin develop --uv`
5. Run `tests/test_native.py` and `BOLTRA_DISABLE_NATIVE=1 uv run pytest`

## Dependency changes

```bash
# Add a runtime dependency — edit pyproject.toml [project] dependencies
# Add a dev dependency — edit [dependency-groups] dev
uv lock
uv sync --group dev
```

## Documentation changes

| Change type | Update |
|-------------|--------|
| New CLI command | `doc/user/cli.md` |
| New install step | `doc/user/installation.md` |
| New file/module | `doc/developer/project-structure.md` |
| Architecture shift | `doc/developer/architecture.md` |
| Anything shipped | `doc/plan/CHANGELOG.md` |

## Getting help

- Product spec: [`boltra-doc.md`](../../boltra-doc.md)
- Roadmap: [`doc/plan/phase.md`](../plan/phase.md)
- PR rules: [`CONTRIBUTING.md`](../../CONTRIBUTING.md)
