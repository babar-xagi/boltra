# Architecture

## Runtime boundaries

Boltra is a Python development tool. Its CLI, generator, configuration loader,
and process launcher use the standard library. The package has no declared
runtime dependencies. Generated apps install their own FastAPI, Pydantic-settings,
and Uvicorn dependencies.

The CLI can scaffold before an app environment exists. An app can also run through
ordinary Uvicorn without importing Boltra.

```text
Terminal / python -m boltra
         |
         v
cli/cli.py: run() -> execute(argv)
         |
         v
cli/parser.py: argparse -> ParsedCommand
         |
         +---- help/version/error -> terminal output
         |
         +---- new -> project/generator.py
         |                 +-> validation.py
         |                 +-> template_engine.py -> templates/*
         |
         +---- add app -> apps/generator.py
         |                    +-> validation.py / templates/router.py.tmpl
         |                    +-> registration.py -> configured app source
         |
         +---- dev -> dev/config.py -> dev/server.py
                                      +-> project .venv Python, or uv run
                                      +-> Uvicorn / Windows runner
```

## CLI

The parser does not print or exit the interpreter. Its custom `ArgumentParser`
catches help/errors as internal exceptions and returns a frozen `ParsedCommand`.
`cli.py` owns routing and output. `run()` translates `execute()`'s integer result
into `SystemExit`; tests can invoke `execute()` with a selected working directory.

Project-name rules live in `project/validation.py`. The generator and parser share
that validator, without the project package depending on the CLI. The parser
adapts `ValueError` to argparse's argument error to preserve useful details.

## Generation

`create_project()` validates the name, rejects existing paths/symlinks, creates a
directory, and writes four rendered templates as UTF-8 with LF endings. Failed
writes trigger cleanup of only the attempted generated files and empty directory.
Other files are preserved.

Readable assets live in `project/templates/`. The template engine loads them with
`importlib.resources` and substitutes `$project_name` and `$api_title` through
`string.Template`. Python/JSON braces remain ordinary source, avoiding nested
formatting escapes. Resources work from editable checkouts and installed wheels.

## Modular apps

`apps/generator.py` implements `add app`: shared project discovery/config locates
the configured module, `apps/validation.py` checks import-safe package names, and
`apps/registration.py` parses its source without executing it. A direct top-level
FastAPI constructor is required. AST positions locate import and registration
insertion points; existing source is retained rather than regenerated.

App packages contain `__init__.py` and a packaged `router.py` template. Exclusive
creation prevents overwrites, and errors clean only newly created files/directories.
Source is replaced atomically after all app files exist; a detected intervening
source edit cancels the operation. The generated application imports its own
routers, with no Boltra runtime dependency or directory auto-discovery.

Settings editing and app removal remain separate later milestones.

## Settings

The generated Pydantic settings class resolves explicit arguments, environment
variables, `.env`, then defaults. It resolves `.env` beside itself, caches a
settings object, warns about the default secret, and exports uppercase aliases.
A small fallback supports a first import before dependencies are installed.

Feature flags and database URL are placeholders. They do not activate planned
apps, ORM, auth, or workers.

## Server

The configuration loader walks upward to the nearest `[tool.boltra]` table. It
parses TOML rather than executing a Python settings file, validates app target,
host, and port, and accepts UTF-8 with or without a BOM.

The launcher selects the project venv before `uv run`, prints/flushes the startup
banner, and waits for Uvicorn. Errors are readable, Ctrl+C is handled, and the
absolute virtualenv directory is excluded from reload watching.

Windows executes `dev/windows.py` by file path using the app's Python. Boltra is
not required inside that environment. The runner adapts Uvicorn's internal reload
supervisor to terminate the old worker instead of broadcasting console signals
or hanging. Repeated real reloads act as a compatibility test. Windows development
worker shutdown hooks are not guaranteed.

## Packaging

Hatchling builds `src/boltra/` into one `py3-none-any` wheel with templates and
`py.typed`. Tests build and inspect wheel/source archives, then install the wheel
in a clean environment to exercise the CLI and resources outside the checkout.

Future modules retain these boundaries: CLI code routes commands; domain modules
implement filesystem, database, or application behavior.
