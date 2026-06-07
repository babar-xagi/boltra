# Releasing Boltra

## Versioning

- Python: `pyproject.toml` → `[project].version`
- Rust workspace: `Cargo.toml` → `[workspace.package].version`
- Package: `src/boltra/__init__.py` → `__version__`

Keep all three in sync. Tag format: `v0.3.0`.

## GitHub

### First-time setup

1. Create a repository on GitHub (e.g. `babar-xagi/boltra`).
2. Push the `main` branch:

   ```bash
   git remote add origin https://github.com/babar-xagi/boltra.git
   git push -u origin main
   ```

### GitHub Release

1. Create a tag: `git tag v0.3.0`
2. Push tag: `git push origin v0.3.0`
3. On GitHub → **Releases** → **Draft a new release** → select tag `v0.3.0`
4. Publish release → triggers `.github/workflows/publish.yml`

## PyPI

Package name: **`boltra`** (verified available).

### One-time PyPI setup

1. Create account at [pypi.org](https://pypi.org)
2. Create API token (scope: entire account or project `boltra`)
3. Add token to GitHub repo → **Settings** → **Secrets** → `PYPI_API_TOKEN`

### Manual publish (local)

```bash
# Build release wheels (Windows example)
uv run maturin build --release

# Upload (requires PyPI token)
$env:MATURIN_PYPI_TOKEN = "<your-token>"
uv run maturin upload --non-interactive dist/*
```

Or with uv:

```bash
uv build
uv publish --token <your-token>
```

### Install from PyPI (after publish)

```bash
pip install boltra
# or
uv add boltra
boltra --version
```

> **Note:** Wheels include the Rust PyO3 extension. Platforms without a matching wheel
> fall back to pure-Python CLI parsing (native acceleration disabled).

## Pre-release checklist

- [ ] `uv run pytest`
- [ ] `uv run ruff check .`
- [ ] `uv run mypy src`
- [ ] `cargo test --workspace`
- [ ] Version bumped in `pyproject.toml`, `Cargo.toml`, `__init__.py`
- [ ] `doc/plan/CHANGELOG.md` updated
- [ ] Tag pushed and GitHub Release published
