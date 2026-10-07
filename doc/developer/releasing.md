# Releasing the Python package

## Version and compatibility

Keep `[project].version` in `pyproject.toml` aligned with `__version__` in
`src/boltra/__init__.py`. Update the changelog and examples before tagging.

Version 0.5.0 moves to Python-only builds. The old native helper API and internal
`cli.main` / `cli.dispatch` modules are removed. Import CLI functions from
`boltra.cli`. Command names remain `new`, `dev`, help, and version.

## Validate and build

```bash
uv sync --locked --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run pre-commit run --all-files
uv build
```

Outputs:

```text
dist/boltra-0.5.0-py3-none-any.whl
dist/boltra-0.5.0.tar.gz
```

One wheel covers supported platforms. Packaging tests verify its tag, typing
marker, templates, entry point, and clean installation. Source archive checks
reject unwanted development caches and native artifacts.

## Wheel smoke test

```bash
uv venv /tmp/boltra-release-check
uv pip install --python /tmp/boltra-release-check/bin/python dist/boltra-0.5.0-py3-none-any.whl
/tmp/boltra-release-check/bin/python -m boltra --version
```

On Windows, use a temporary path and `Scripts/python.exe` instead of `bin/python`.
Do not commit release-check environments.

## Publish

The workflow runs on `v*` tags or manual dispatch. It validates, builds, saves
artifacts, and publishes using the configured `PYPI_API_TOKEN` secret. There is
no native compilation or platform wheel matrix.

When the maintainer is ready to publish a verified release:

```bash
git tag v0.5.0
git push origin v0.5.0
```

For manual publication with credentials provided through the environment:

```bash
uv publish dist/*
```

A commit/build does not publish anything. Keep credentials out of source and
commit messages.
