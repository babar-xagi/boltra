# File-by-file implementation guide

Paths are relative to the repository root. Use this guide to locate the behavior
you want to understand or change. Public functions have types/docstrings; comments
explain design choices, environment handling, and recovery paths.

## Package entry files

### `src/boltra/__init__.py`

Defines `__version__ = "0.5.0"` and exposes it through `__all__`. It has no heavy
imports, so package metadata is accessible before app dependencies are installed.
Keep it aligned with the version in `pyproject.toml`.

```python
import boltra
print(boltra.__version__)
```

### `src/boltra/__main__.py`

Calls the CLI's `run()` under the main-module guard. This implements
`python -m boltra --help`, sharing the installed console script's behavior.

### `src/boltra/py.typed`

An empty PEP 561 marker identifies the installed package as typed. The
wheel-content test checks that it is included.

## CLI folder

### `src/boltra/cli/__init__.py`

Exports `run`, `execute`, `parse_argv`, and `ParsedCommand`. Import from this
package to access the CLI functions without relying on internal file names.

### `src/boltra/cli/cli.py`

This file implements the CLI entry point, routing, and terminal output:

- `run()` reads `sys.argv[1:]` and exits with the returned command status.
- `execute(argv, cwd=None)` parses input and routes help/version/new/dev/error.
- `_new_project(name, cwd=None)` calls the generator, converts `ProjectError` to
  a readable error, and prints the next-step instructions.

The optional `cwd` is passed to generation/discovery, without changing the
process-wide directory. Success returns `0`, usage errors return `2`, and domain
failures return `1`. Dev returns the launcher/server status.

```python
from pathlib import Path
from boltra.cli import execute

status = execute(["new", "demo"], cwd=Path("/tmp"))
```

Add arguments in `parser.py`, then route their action here. Keep filesystem or
database implementation in its domain module. Tests: `tests/cli/test_cli.py` plus
the corresponding project/server integration suite.

### `src/boltra/cli/parser.py`

Defines standard-library argparse options: help/version, `new <name>`, and `dev`.
`ParsedCommand` is a frozen dataclass with action, optional name, help/error text,
and exit status.

`_ArgumentParser` raises `_ParserExit` for help/errors. `parse_argv` catches that
internal exception and returns data without printing or exiting. `_project_name`
converts the shared validator's `ValueError` into `ArgumentTypeError`, preserving
its original message.

```python
from boltra.cli import parse_argv

parsed = parse_argv(["new", "school_api"])
assert parsed.action == "new"
assert parsed.name == "school_api"
```

Tests cover global/subcommand help, one error message, valid/invalid inputs,
version, and the action/status contract.

## Project folder

### `src/boltra/project/__init__.py`

Exports `create_project` and `ProjectError`, the scaffolding API independent of
the terminal interface.

### `src/boltra/project/validation.py`

`validate_project_name(name)` returns a valid slug or raises `ValueError`. Names
start with an ASCII letter and then contain letters, digits, `_`, or `-`. Empty
names, dots, separators, and other characters are rejected. `fullmatch` checks
the whole input, including trailing newlines.

The parser and generator share this function to avoid divergent rules.

### `src/boltra/project/generator.py`

`create_project(name, cwd=None)` returns the absolute new directory. It:

1. Validates the project name.
2. Resolves the parent and rejects an existing destination or symlink.
3. Creates the directory without inventing missing parent directories.
4. Renders four templates and writes UTF-8 with LF line endings.
5. On failure, cleans only attempted generated files and the empty directory
   when possible.

`ProjectError` wraps validation, creation, and write failures. Each destination
is recorded before its write because a failed write can leave a partial file.
Cleanup does not recursively delete unrelated content.
Tests: `tests/project/test_generator.py`.

### `src/boltra/project/template_engine.py`

`display_title(name)` converts a slug into a readable API title. `_render` loads
a packaged asset with `importlib.resources` and applies `string.Template`.
`main_py`, `settings_py`, `pyproject_toml`, and `env_example` select the four assets.

Only `$project_name` and `$api_title` are template placeholders. Python dictionary
and JSON braces are normal source. Edit the assets to change generated output,
then verify both project behavior and installed-wheel resources.

### `src/boltra/project/templates/main.py.tmpl`

Creates an ordinary FastAPI application using the settings object's title/debug
flag. Implements `GET /` returning the starter greeting, with a return type and
comments showing where users extend the app.

### `src/boltra/project/templates/settings.py.tmpl`

Defines `Settings(BaseSettings)`, an absolute `.env` path, defaults, cached
`get_settings()`, and module-level `settings`. Warns about the unchanged generated
secret and exports uppercase aliases.

Pydantic handles normal use. The first-import fallback reads simple environment
pairs, respects explicit/environment/file precedence, parses boolean/list/optional
values, and copies lists per instance. Reserved flags are configuration only;
they do not activate future batteries.
Tests: `tests/project/test_settings.py` exercises both backends.

### `src/boltra/project/templates/pyproject.toml.tmpl`

Declares Python 3.12+, FastAPI, Pydantic settings, and Uvicorn. Defines the
`[tool.boltra]` mode, app target, settings path, host, and port. Does not add Boltra
as an application runtime dependency.

### `src/boltra/project/templates/env.example.tmpl`

Documents scalar/list environment defaults and reserved feature flags. Rendered
as `.env.example`; users copy it to `.env` and replace the generated secret.

## Development-server folder

### `src/boltra/dev/__init__.py`

Exports the config dataclass, discovery/loading functions, command builder,
server launcher, and error types. Internal files retain their distinct responsibilities.

### `src/boltra/dev/config.py`

`BoltraProjectConfig` is a frozen dataclass containing app, mode, settings path,
host, and port. `has_tool_boltra` checks for a usable configuration table;
`find_project_root` walks upward to the nearest matching TOML file.

`load_boltra_config` parses TOML and wraps read, encoding, and syntax failures in
`DevConfigError`. `_read_pyproject_text` accepts UTF-8 with/without a BOM.
`_load_host` requires a non-empty string. `_load_port` rejects booleans, strings,
and integers outside 1–65535. App syntax accepts dotted modules/attributes.

```python
from pathlib import Path
from boltra.dev import find_project_root, load_boltra_config

root = find_project_root(Path("/path/to/app/subdirectory"))
config = load_boltra_config(root / "pyproject.toml")
```

Tests: `tests/dev/test_config.py` checks defaults/custom values, malformed TOML,
wrong types/import paths, encoding, and parent discovery.

### `src/boltra/dev/server.py`

`_find_venv_python` selects `.venv/Scripts/python.exe` on Windows or
`.venv/bin/python` elsewhere. `build_uvicorn_command` returns an argument list,
preferring the local venv and falling back to uv. It excludes the absolute venv
path from file watching and selects the Windows runner when necessary.

`format_dev_banner` formats URLs and labels, including bracketed IPv6 URLs.
`run_dev_server` combines discovery, validation, environment selection, banner,
and `subprocess.run`. It flushes the banner before child logs, handles Ctrl+C,
reports launch errors, and returns the child status.
Tests: `tests/dev/test_server.py` and the HTTP integration test.

### `src/boltra/dev/windows.py`

An internal script executed by the app's Python, importing Uvicorn from that
application environment. `_stop_worker` terminates/joins the old worker;
`_restart` creates a replacement; `_shutdown` stops the worker and delegates
remaining cleanup to Uvicorn's original shutdown.

Only the main-script guard patches the reload supervisor and runs Uvicorn's CLI.
Importing the module does not patch the supervisor. This workaround uses an
internal Uvicorn API and is covered by real repeated reloads. Windows development
worker shutdown hooks are not guaranteed to run.

## Tests

| File | Behavior |
|------|----------|
| `tests/cli/test_cli.py` | Commands, help, version, validation, errors/status |
| `tests/project/test_generator.py` | Output/imports, JSON home, `.env`, collisions, failed-write cleanup |
| `tests/project/test_settings.py` | Both backends, precedence, overrides, cache, booleans, warnings/list isolation |
| `tests/dev/test_config.py` | TOML/discovery and config validation |
| `tests/dev/test_server.py` | Environment selection, URLs, launch errors, Ctrl+C |
| `tests/dev/test_integration.py` | Dependency sync, real home/docs/OpenAPI, two reloads |
| `tests/test_package.py` | Pure wheel/source archive, templates, typing, clean installed CLI |

Test `__init__.py` files make the mirrored folders explicit packages.

## Root configuration and automation

| File | Responsibility |
|------|----------------|
| `pyproject.toml` | Version/metadata, console entry point, Hatchling target, dev dependencies, Ruff/mypy/pytest |
| `uv.lock` | Reproducible locked Python dependencies |
| `.pre-commit-config.yaml` | Ruff, mypy, whitespace/EOF/YAML/TOML/large-file checks |
| `.github/workflows/ci.yml` | Python 3.12–3.14 quality/tests/build matrix on Linux, Windows, macOS |
| `.github/workflows/publish.yml` | Tagged/manual validation, Python build, artifact upload, PyPI publish |
| `.gitignore` | Environments, bytecode, secrets, tool caches, distribution output |
| `.gitattributes` | Consistent LF text files across operating systems |

`doc/README.md` indexes documentation. `boltra-doc.md` records product direction;
`doc/plan/phase.md` is the execution roadmap.
