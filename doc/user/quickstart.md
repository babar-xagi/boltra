# Build your first app

This guide uses the CLI installed from the [installation guide](installation.md).
The example creates a small school API and adds a normal FastAPI route.

## 1. Create and install the application

```bash
boltra new school_api
cd school_api
uv sync
cp .env.example .env
```

On PowerShell, the copy command can also be `Copy-Item .env.example .env`.
Boltra prints the new directory and next steps. It creates these files:

| File | Your responsibility |
|------|---------------------|
| `main.py` | Add routes and application behavior |
| `settings.py` | Define typed settings and read the cached `settings` object |
| `pyproject.toml` | Manage app dependencies and server configuration |
| `.env.example` | Maintain an example configuration; copy it to an untracked `.env` |

The app does not depend on Boltra at runtime. The CLI manages the project, while
FastAPI, Pydantic settings, and Uvicorn run the application.

## 2. Set local configuration

Edit `.env`:

```dotenv
APP_NAME=school_api
API_TITLE=School API
DEBUG=true
SECRET_KEY=replace-with-your-own-random-secret
ALLOWED_HOSTS=["localhost","127.0.0.1"]
```

The default secret causes a warning. `ALLOWED_HOSTS` is configuration data at this
stage; it does not install host-checking middleware. See the
[settings reference](settings.md) for what each setting currently does.

## 3. Run the server

```bash
boltra dev
```

Open `http://127.0.0.1:8000/` for the greeting and
`http://127.0.0.1:8000/docs` for Swagger UI. The OpenAPI title is `School API`.

To inspect the greeting from PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/
```

Or use curl in your shell:

```bash
curl http://127.0.0.1:8000/
```

Expected JSON:

```json
{"message": "Hello from FastAPI + Boltra Kit"}
```

## 4. Add an endpoint

Append this to `main.py`:

```python
@app.get("/students")
async def list_students() -> list[dict[str, str | int]]:
    return [
        {"id": 1, "name": "Ali"},
        {"id": 2, "name": "Sara"},
    ]
```

The development server reloads your Python change. Visit `/students`, or use
`/docs` to call it. The example uses in-memory data; no ORM is implemented yet.

## 5. Change the port or application module

Edit `pyproject.toml` and restart `boltra dev`:

```toml
[tool.boltra]
mode = "fastapi-kit"
app = "main:app"
settings = "settings.py"
host = "127.0.0.1"
port = 8080
```

For a packaged application, use a target such as `backend.main:app`. The target
is a Python module and attribute that Uvicorn can import.

Changes to `.env` and `pyproject.toml` require restarting the command. Python
source changes reload automatically. Stop the server with Ctrl+C.

## 6. Extend with FastAPI

Use FastAPI routers, dependencies, Pydantic schemas, and middleware directly.
The current toolkit does not provide `boltra add app`, ORM, admin, or auth commands.
Their intended order is documented in the [roadmap](../plan/phase.md).

For production serving, use ordinary Uvicorn without reload. On Windows,
development restarts terminate the old worker, so shutdown hooks are not guaranteed.
