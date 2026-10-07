# Testing and quality checks

## Complete verification

```bash
uv sync --locked --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run pre-commit run --all-files
uv build
```

Python 3.12, 3.13, and 3.14 are supported. CI is configured on Linux, Windows,
and macOS. The [verification report](verification.md) separates actual local
execution from configured remote checks.

## Targeted checks

```bash
uv run pytest tests/cli
uv run pytest tests/project
uv run pytest tests/apps
uv run pytest tests/dev/test_config.py tests/dev/test_server.py
uv run pytest -m integration
uv run pytest -m packaging
```

For a fast edit loop:

```bash
uv run pytest -m "not integration and not packaging"
```

Run the complete suite before committing.

## Test behavior

CLI tests call `execute` and `parse_argv`, checking messages, arguments, exit
statuses, and side effects. Generator tests create temporary projects, import
generated modules, and simulate collisions/write failures.

Settings tests import fresh generated modules with Pydantic installed and with
its import unavailable. They verify explicit/environment/file precedence,
booleans, overrides, independent lists, caching, and default-secret warnings.

App tests exercise package-name rules, collisions, packaged modules, source
preservation, unsupported targets, source-write failures, concurrent editor
changes, and rollback without losing existing files. A real filesystem-link
test skips when the OS does not permit creating a symbolic link.

The HTTP integration test generates/syncs an app using the current interpreter,
starts the actual launcher, checks home JSON, Swagger/OpenAPI, and `.env` title,
then checks two registered app endpoints and their OpenAPI tags, adds a third app
while the server is running, and verifies two successive source-code reloads.
Windows uses a hidden separate
console to isolate signals from pytest. Server logs are captured for diagnosis.

Packaging tests build/inspect wheel and source archives, reject unwanted native
or cache artifacts, check templates/typing/entry-point files, and install the
wheel into a clean environment. They run `python -I -m boltra` and its console
script outside the checkout, without installing app dependencies.
The installed CLI also creates and registers an app without FastAPI installed;
scaffolding never executes generated application code.

## Coverage

```bash
uv run pytest --cov=boltra --cov-report=term-missing
```

Coverage measures the main test process. Generated modules and the Windows runner
execute under separate files/environments, so behavioral integration checks remain
necessary alongside the percentage.

## Restricted environments

Tests need temporary files, process access, and dependency downloads for fresh
app/build environments. Select a writable temp/cache path when necessary:

```powershell
$env:UV_CACHE_DIR = "D:/boltra/.uv/cache"
uv run pytest --basetemp=D:/boltra/.uv/pytest-run -p no:cacheprovider
```

Pytest owns `--basetemp` and may clear it on rerun; do not use a directory holding
work you need to preserve.
