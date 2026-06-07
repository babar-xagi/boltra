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

Shows CLI name, tagline, and available options. Parsed by **Rust clap**, executed in Python.

```bash
boltra --help
```

### `boltra --version`

Prints the installed Boltra version (e.g. `0.1.0`).

```bash
boltra --version
boltra -V
```

### `boltra new <name>`

Creates a minimal FastAPI project with direct FastAPI code (no wrapper).

```bash
boltra new hello
```

Generated layout:

```text
hello/
├── main.py
├── settings.py
└── pyproject.toml
```

Rules:

- Name must start with a letter
- Only letters, digits, hyphens, and underscores allowed
- Will not overwrite an existing directory

Example output:

```text
Created project 'hello' in /path/to/hello

Next steps:
  cd hello
  uv sync
  uv run uvicorn main:app --reload
```

### `boltra dev`

Runs the FastAPI development server with auto-reload. Must be run inside a
Boltra project (directory with `[tool.boltra]` in `pyproject.toml`).

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
| `boltra add app <name>` | 4+ | Add an app module |
| `boltra add orm` | 9+ | Add async ORM |
| `boltra add admin` | 22+ | Add admin dashboard |

See the [phased roadmap](../plan/phase.md) for the full schedule.

## Examples

```bash
# Check version after install
boltra --version

# Confirm CLI is wired correctly
boltra --help
```

## Environment variables

| Variable | Values | Effect |
|----------|--------|--------|
| `BOLTRA_DISABLE_NATIVE` | `1`, `true`, `yes`, `on` | Disable Rust native extension; use Python fallback |

This is mainly for testing and unsupported platforms. End users normally do not need to set it.
