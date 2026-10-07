# Generated application settings

`boltra new` writes a readable `settings.py` with a typed `Settings` class and
cached `settings` object. Normal use relies on `pydantic-settings`, installed by
the generated project's `uv sync`.

## Load order

Values resolve in this order:

1. Explicit `Settings(...)` arguments.
2. Process environment variables.
3. The `.env` next to `settings.py`.
4. Defaults declared in the class.

The `.env` path is absolute relative to the settings file, so importing the app
from another working directory does not change which environment file is read.
Extra environment keys are ignored.

```dotenv
API_TITLE=My School API
DEBUG=false
SECRET_KEY=my-local-secret
ALLOWED_HOSTS=["example.com","api.example.com"]
```

Use JSON arrays for list values. Common boolean forms include `true/false`,
`1/0`, `yes/no`, and `on/off`; invalid values are rejected.

## Current fields

| Field / environment key | Default | Current use |
|-------------------------|---------|-------------|
| `app_name` / `APP_NAME` | Project slug | Application metadata |
| `api_title` / `API_TITLE` | Human-readable project title | FastAPI and OpenAPI title |
| `debug` / `DEBUG` | `true` | FastAPI debug flag |
| `secret_key` / `SECRET_KEY` | `change-this-secret-key` | Warns when the generated default remains |
| `allowed_hosts` / `ALLOWED_HOSTS` | localhost and 127.0.0.1 | Stored configuration; no host middleware yet |
| `installed_apps` / `INSTALLED_APPS` | Empty list | Reserved for future discovery; `add app` registers routers directly |
| `database_url` / `DATABASE_URL` | None | Reserved configuration; no database connection yet |
| Feature flags | `false` | Reserved for auth, admin, AI, workers, and payments |
| `boltra_mode` / `BOLTRA_MODE` | `fastapi-kit` | Toolkit metadata |
| `api_engine` / `API_ENGINE` | `fastapi` | Toolkit metadata |

The feature keys are `AUTH_ENABLED`, `ADMIN_ENABLED`, `AI_ENABLED`,
`WORKER_ENABLED`, and `PAYMENTS_ENABLED`. Setting them does not install or activate
those planned modules. Server host/port live in `[tool.boltra]`, not this class.

## Use settings in your routes

```python
from settings import settings

@app.get("/about")
async def about() -> dict[str, str]:
    return {"name": settings.app_name}
```

For an independent settings object:

```python
from settings import Settings

custom = Settings(debug=False, allowed_hosts=["example.com"])
```

The generated `get_settings()` function uses `lru_cache`. Repeated calls return
the same object. To request a fresh object programmatically:

```python
get_settings.cache_clear()
fresh = get_settings()
```

Existing references to the previous module-level `settings` object are not
replaced by clearing the cache. Restart the development server after changing
`.env` to reload settings throughout the application.

## Uppercase aliases

The file also exposes `APP_NAME`, `API_TITLE`, `DEBUG`, `SECRET_KEY`,
`ALLOWED_HOSTS`, `INSTALLED_APPS`, `DATABASE`, feature dictionaries, and `BOLTRA`.
These aliases preserve a familiar settings-file style. Prefer the typed
`settings` object in new code.

## First-import fallback

Before dependencies are installed, the generated file can still import using a
small Python fallback. It reads simple `KEY=VALUE` environment files and parses
basic scalar/list values. It is not a replacement for the full Pydantic validator.
Run `uv sync` before normal application development.

Both paths are covered by settings tests for precedence, explicit overrides,
boolean parsing, independent list defaults, caching, and default-secret warnings.
