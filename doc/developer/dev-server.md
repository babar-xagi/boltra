# Dev Server (`boltra dev`)

Phase 3 — runs the generated FastAPI app with uvicorn reload.

## Flow

```text
boltra dev
    → find_project_root()     # pyproject.toml with [tool.boltra]
    → load_boltra_config()    # app, mode, settings, host, port
    → print banner (URL, docs, mode)
    → uv run uvicorn main:app --host <host> --port <port> --reload
```

## Modules

| File | Role |
|------|------|
| `src/boltra/dev/config.py` | `tomllib` loader, `find_project_root()` |
| `src/boltra/dev/server.py` | Banner, command builder, `run_dev_server()` |
| `src/boltra/cli/dispatch.py` | Routes `action == "dev"` to `run_dev_server()` |

## `[tool.boltra]` fields

| Key | Default | Used by dev |
|-----|---------|-------------|
| `app` | `main:app` | uvicorn target |
| `mode` | `fastapi-kit` | printed in banner |
| `settings` | `settings.py` | not used until Phase 4+ |
| `host` | `127.0.0.1` | uvicorn bind host |
| `port` | `8000` | uvicorn bind port |

## Environment selection

1. **`uv run uvicorn`** when `uv` is on PATH (recommended)
2. **`.venv/bin/python -m uvicorn`** as fallback
3. Error if neither is available — user must run `uv sync` first

## Rust clap

```rust
Commands::Dev  →  CliAction::Dev  →  Python action "dev"
```

## Tests

- Unit: config load, banner, command builder, missing project error
- Integration (`@pytest.mark.integration`): starts server, hits `/` and `/docs`
