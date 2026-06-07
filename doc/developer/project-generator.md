# Project Generator (`boltra new`)

Phase 2 deliverable — creates a minimal, honest FastAPI project.

## Command

```bash
boltra new hello
```

## Generated layout

```text
hello/
├── main.py          # direct FastAPI — no Boltra wrapper
├── settings.py      # Django-like settings module
└── pyproject.toml   # deps + [tool.boltra] metadata
```

No extra folders (no `apps/`, `orm/`, etc.) until later phases.

## Validation rules

Enforced in **both** Rust (`crates/boltra-cli`) and Python (`boltra.cli.parser`):

| Rule | Example invalid |
|------|-----------------|
| Non-empty | `""` |
| Starts with ASCII letter | `1app` |
| Only `[a-zA-Z0-9_-]` | `my.app`, `my/app` |
| Target dir must not exist | `hello/` already present |

## Templates

Defined in `src/boltra/project/templates.py`:

- **`main_py(name)`** — FastAPI app with `GET /` route; title from `display_title()`
- **`settings_py(name)`** — `APP_NAME`, `DEBUG`, `BOLTRA` block per `boltra-doc.md`
- **`pyproject_toml(name)`** — `fastapi`, `uvicorn[standard]`; `requires-python >=3.12`
  (no `boltra` dep until PyPI publish — generated `main.py` uses plain FastAPI)

## Core API

```python
from boltra.project import create_project, ProjectError

path = create_project("hello", cwd=Path("/tmp"))
```

Raises `ProjectError` on validation failure or existing directory.

## Integration test contract

Exit criteria (Phase 2):

1. `boltra new hello` creates three files
2. Generated `main.py` imports without error (`from fastapi import FastAPI`)
3. `app.title` matches display title

Tests: `tests/test_project.py`

## Success output

```text
Created project 'hello' in /path/to/hello

Next steps:
  cd hello
  uv sync
  uv run uvicorn main:app --reload
```

Phase 3 replaces the manual uvicorn line with `boltra dev`.
