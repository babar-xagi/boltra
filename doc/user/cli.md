# CLI reference

## Invocation

```bash
boltra [OPTIONS] COMMAND [ARGS]
python -m boltra [OPTIONS] COMMAND [ARGS]
```

Both entry points use `boltra/cli/cli.py`. During contributor development, use
`uv run boltra ...` from the Boltra checkout.

## Help and version

```bash
boltra
boltra --help
boltra -h
boltra --version
boltra -V
boltra new --help
boltra dev --help
boltra add app --help
```

No arguments show general help. Subcommand help describes only that command.
The current checkout prints version `0.5.0`.

## `boltra new <name>`

Create a minimal FastAPI application:

```bash
boltra new hello
```

Produces `hello/main.py`, `hello/settings.py`, `hello/pyproject.toml`, and
`hello/.env.example`. Names must start with an ASCII letter and contain only
letters, digits, hyphens, or underscores. Examples: `hello`, `SchoolAPI`, `school_api`.
Names containing dots, path separators, spaces, or trailing newlines are invalid.

An existing destination is never overwritten. Filesystem failures produce a
readable error; failed writes attempt to remove only the generated partial files.
Unrelated files are preserved.

Next steps:

```bash
cd hello
uv sync
cp .env.example .env
boltra dev
```

## `boltra add app <name>`

Create a modular FastAPI app and register its router:

```bash
boltra add app students
```

Creates `apps/students/__init__.py` and `apps/students/router.py`, plus the shared
`apps/__init__.py` if needed. Updates the configured application's source with
an explicit router import and `include_router()` call. `/students/` responds with
`{"app": "students", "status": "ok"}` and appears in OpenAPI.

Names must be lowercase ASCII Python package identifiers, starting with a letter;
keywords and Windows device names are rejected. Existing apps are preserved.
The command works from project subdirectories. It requires a source module with
a direct top-level FastAPI instance; factories and nested attributes are unsupported.
Settings and dependencies are unchanged. See [modular apps](apps.md) for supported
layouts, examples, conflicts, and failed-write recovery.

## `boltra dev`

Find the nearest parent directory containing a non-empty `[tool.boltra]` table,
read its settings, and launch Uvicorn with automatic Python-source reload.
The command works from a project subdirectory as well as its root.

```toml
[tool.boltra]
mode = "fastapi-kit"
app = "main:app"
settings = "settings.py"
host = "127.0.0.1"
port = 8000
```

| Key | Default | Behavior |
|-----|---------|----------|
| `app` | `main:app` | Uvicorn target; dotted modules and attributes are supported |
| `host` | `127.0.0.1` | Non-empty bind host |
| `port` | `8000` | Integer from 1 to 65535; boolean/string values are rejected |
| `mode` | `fastapi-kit` | Label printed in the startup banner |
| `settings` | `settings.py` | Project metadata; generated `main.py` imports settings directly |

The launcher prefers the project's `.venv` Python. If no venv exists and uv is
available, it launches through `uv run`. Otherwise it asks you to run `uv sync`.
The virtualenv is excluded from reload watching.

Startup prints the app URL, documentation URL, mode, and import target. IPv6
hosts are shown as bracketed URLs, for example `http://[::1]:8000/docs`.
Configuration accepts UTF-8 with or without a BOM.

Restart after changing `.env` or `pyproject.toml`. On Windows, a Python runner
avoids unreliable console reload signals by terminating the old worker.
Development shutdown hooks are not guaranteed on Windows; production should
run ordinary Uvicorn without reload.

## Exit statuses

| Status | Meaning |
|--------|---------|
| `0` | Successful command, help, or version |
| `1` | Generation/configuration/environment/launch failure |
| `2` | Invalid CLI usage or arguments |
| `130` | Ctrl+C handled by the Boltra launcher |

The dev command otherwise returns its server subprocess's exit status.

## Programmatic use

```python
from pathlib import Path
from boltra.cli import execute, parse_argv

command = parse_argv(["new", "hello"])
assert command.action == "new"
exit_code = execute(["new", "hello"], cwd=Path("/tmp"))
```

For application code, use the generator directly:

```python
from pathlib import Path
from boltra.project import create_project

project = create_project("hello", cwd=Path("/tmp"))
```

## Planned commands

`remove app`, router auto-discovery, ORM/migrations, admin, auth,
workers, and AI are roadmap items. The current parser does not accept them.
See the [roadmap](../plan/phase.md).
