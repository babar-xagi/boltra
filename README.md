# Boltra

**A Python development toolkit for FastAPI.**

Boltra is a Python development toolkit that creates small, readable FastAPI
projects and runs them with one command. Boltra is designed specifically for
FastAPI applications. Generated applications use ordinary
`FastAPI()` code, so you can extend them with the FastAPI APIs you already know.

The current source version is **0.5.0**. Boltra is in early development and ships
as a **pure Python package**. Its CLI uses the standard library; installing Boltra
does not require a compiler or native build toolchain.

## 📖 Contents

- [Implemented features](#-implemented-features)
- [Quick start](#-quick-start)
- [Generated project and configuration](#-project-layout-and-configuration)
- [Documentation](#-documentation)
- [Development](#-develop-boltra)

## 🧩 Implemented features

| Feature | What it does |
|---------|--------------|
| `boltra new <name>` | Creates a direct FastAPI app, settings, dependencies, and `.env.example` |
| `boltra dev` | Discovers the project, launches Uvicorn, and reloads Python changes |
| Typed settings | Reads environment variables and `.env` with Pydantic settings |
| Project validation | Rejects invalid names and existing destinations; reports write failures |
| Configurable server | Reads app target, host, and port from `[tool.boltra]` |
| Windows reload support | Uses a Python compatibility runner for reliable worker restart |
| Help and version | Supports `--help`, `--version`, and `python -m boltra` |

App add/remove, router discovery, ORM, admin, authentication, workers, and AI are
**planned**. They are not available commands yet. See the [roadmap](doc/plan/phase.md).

## 🚀 Quick start

Requirements: **Python 3.12+** and **uv**. These commands install this checkout as
a separate CLI tool, keeping Boltra independent of your generated app's environment.

```bash
git clone https://github.com/babar-xagi/boltra.git
cd boltra
uv tool install .

boltra new school_api
cd school_api
uv sync
cp .env.example .env
boltra dev
```

On PowerShell, `Copy-Item .env.example .env` also copies the environment example.
Set your own `SECRET_KEY` in `.env`. The generated default triggers a warning.

Open the app at [localhost:8000](http://127.0.0.1:8000/) and interactive API docs
at [localhost:8000/docs](http://127.0.0.1:8000/docs).

The home endpoint returns:

```json
{"message": "Hello from FastAPI + Boltra Kit"}
```

For other installation options and troubleshooting, read the
[installation guide](doc/user/installation.md).

## 📁 Project layout and configuration

```text
school_api/
├── main.py          # Your ordinary FastAPI application
├── settings.py      # Typed settings and environment loading
├── pyproject.toml   # App dependencies and development-server configuration
└── .env.example     # Example local environment variables
```

The app depends on FastAPI, Pydantic settings, and Uvicorn. Boltra itself is a CLI
tool and is not added as an app runtime dependency.

For example, add this route to `main.py` while `boltra dev` is running:

```python
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

The server reloads the change. Open `/health` or try it from `/docs`.

Change the server port in the generated `pyproject.toml`:

```toml
[tool.boltra]
mode = "fastapi-kit"
app = "main:app"
settings = "settings.py"
host = "127.0.0.1"
port = 8080
```

Restart `boltra dev` after changing `.env` or server configuration. Automatic
reload watches Python source files, not environment/configuration changes.

## 📚 Documentation

| Audience | Guide |
|----------|-------|
| Getting started | [Complete quickstart](doc/user/quickstart.md) |
| CLI users | [Commands, options, errors, and examples](doc/user/cli.md) |
| App developers | [Settings reference](doc/user/settings.md) |
| Contributors | [Developer guide](doc/developer/README.md) |
| Understanding the code | [Detailed file-by-file reference](doc/developer/file-reference.md) |
| Understanding the layout | [Repository structure](doc/developer/project-structure.md) |
| Validation results | [Verification report](doc/developer/verification.md) |
| Future work | [Python-first roadmap](doc/plan/phase.md) |

## 🛠️ Develop Boltra

```bash
uv sync --locked --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run pytest --cov=boltra --cov-report=term-missing
uv build
```

Source code is organized by responsibility:

```text
src/boltra/
├── cli/             # cli.py: entry point and command routing; parser.py: arguments
├── project/         # Generator, shared validation, and readable template assets
└── dev/             # Project configuration, server launcher, and Windows runner
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for checks and commit conventions.
Windows development reload terminates the old worker; application shutdown hooks
are not guaranteed during these restarts. Use normal Uvicorn without reload for
production serving.

## License

[MIT](LICENSE) — Boltra Contributors.
