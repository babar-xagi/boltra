# Project Generator (`boltra new`)

Creates a minimal, honest FastAPI project. The generated app stays direct FastAPI; Boltra provides scaffolding and conventions rather than a wrapper runtime.

## Command

```bash
boltra new hello
```

## Generated layout

```text
hello/
|-- main.py          # direct FastAPI app
|-- settings.py      # pydantic-settings based configuration
|-- pyproject.toml   # deps + [tool.boltra] metadata
`-- .env.example    # copy to .env for local overrides
```

No extra folders are created until later phases add apps, ORM, workers, or admin.

## Validation rules

Validation is enforced in both Rust (`crates/boltra-cli`) and Python (`boltra.cli.parser`).

| Rule | Example invalid |
|------|-----------------|
| Non-empty | `""` |
| Starts with ASCII letter | `1app` |
| Only `[a-zA-Z0-9_-]` | `my.app`, `my/app` |
| Target dir must not exist | `hello/` already present |

## Templates

Defined in `src/boltra/project/templates.py`:

- `main_py(name)` creates a FastAPI app and reads title/debug from `settings`.
- `settings_py(name)` creates a typed `Settings` object, `.env` loading, uppercase aliases, and a default `SECRET_KEY` warning.
- `env_example(name)` creates local configuration examples.
- `pyproject_toml(name)` declares `fastapi`, `pydantic-settings`, `uvicorn[standard]`, and `[tool.boltra]`.

## Core API

```python
from pathlib import Path
from boltra.project import create_project

path = create_project("hello", cwd=Path("/tmp"))
```

`ProjectError` is raised on validation failure or existing target directory.

## Test contract

Tests in `tests/test_project.py` cover:

- file generation, including `.env.example`
- generated `main.py` import
- `.env` values loading through generated settings
- existing-directory and invalid-name failures
- CLI integration output

## Success output

```text
Created project 'hello' in /path/to/hello

Next steps:
  cd hello
  uv sync                    # creates a local .venv
  boltra dev                 # start server with reload
```
