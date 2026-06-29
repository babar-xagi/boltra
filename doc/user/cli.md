# CLI Reference

Boltra provides a command-line interface for scaffolding and managing FastAPI projects.

## Invocation

```bash
boltra [OPTIONS] COMMAND [ARGS]...
```

When developing from source, prefix with `uv run`:

```bash
uv run boltra --help
```

## Global options

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | | Show help message and exit |
| `--version` | `-V` | Print version and exit |

## Commands (current)

### `boltra --help`

Shows CLI name, tagline, and available commands. Native builds parse this with Rust clap; fallback builds use Python argparse.

```bash
boltra --help
```

### `boltra --version`

Prints the installed Boltra version, for example `0.4.0`.

```bash
boltra --version
boltra -V
```

### `boltra new <name>`

Creates a minimal FastAPI project with direct FastAPI code, typed settings, and an `.env.example` file.

```bash
boltra new hello
```

Generated layout:

```text
hello/
|-- main.py
|-- settings.py
|-- pyproject.toml
`-- .env.example
```

Rules:

- Name must start with a letter
- Only letters, digits, hyphens, and underscores allowed
- Existing directories are never overwritten

The generated `settings.py` loads environment variables and `.env` values through `pydantic-settings` when installed, with a small import fallback for first-run friendliness.

Example output:

```text
Created project 'hello' in /path/to/hello

Next steps:
  cd hello
  uv sync                    # creates a local .venv
  boltra dev                 # start server with reload
```

### `boltra dev`

Runs the FastAPI development server with auto-reload. It must be run inside a Boltra project with `[tool.boltra]` in `pyproject.toml`.

```bash
cd hello
uv sync
boltra dev
```

Reads from `pyproject.toml`:

```toml
[tool.boltra]
mode = "fastapi-kit"
app = "main:app"
settings = "settings.py"
```

Prints mode, app path, URL, and docs URL, then runs:

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Open:

- App: http://127.0.0.1:8000/
- Swagger docs: http://127.0.0.1:8000/docs

### `boltra` (no arguments)

With no subcommand, shows help.

## Commands (planned)

| Command | Phase | Description |
|---------|-------|-------------|
| `boltra add app <name>` | 5 | Add an app module |
| `boltra remove app <name>` | 6 | Remove an app module safely |
| `boltra doctor` | early hardening | Check project configuration and environment health |
| `boltra add orm` | 9+ | Add async ORM |
| `boltra add admin` | 22+ | Add admin dashboard |

See the [phased roadmap](../plan/phase.md) for the full schedule.

## Environment variables

| Variable | Values | Effect |
|----------|--------|--------|
| `BOLTRA_DISABLE_NATIVE` | `1`, `true`, `yes`, `on` | Disable Rust native extension; use Python fallback |

This is mainly for testing and unsupported platforms. End users normally do not need to set it.
