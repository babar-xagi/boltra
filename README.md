# Boltra

**One development toolkit for Python APIs.**

Boltra is a general-purpose Python API development kit. Its goal is to give
projects a consistent workflow for scaffolding, configuration, development
commands, and optional tooling across different API frameworks.

Framework choice belongs to the application. Boltra's direction includes
**FastAPI, Flask, Django-based APIs, Django Bolt, TurboAPI, and future Python API
frameworks**. The toolkit should preserve each framework's normal code and
conventions while sharing the project-development workflow around it.

> **Current release:** the 0.5.0 source implements FastAPI project generation and
> development serving. Other framework integrations and framework-selection
> adapters are planned. The compatibility table below distinguishes shipped
> behavior from the architecture's intended direction.

Boltra itself is written in Python and ships as a platform-independent wheel.
Its CLI uses the standard library and its build does not require a native compiler.

## 📖 Contents

- [Framework compatibility](#-framework-compatibility)
- [Architecture and framework selection](#-architecture-and-framework-selection)
- [Implemented capabilities](#-implemented-capabilities)
- [Quick start](#-quick-start-fastapi)
- [Generated project and configuration](#-project-layout-and-configuration)
- [Documentation](#-documentation)
- [Development and quality checks](#-development-and-quality-checks)

## 🧩 Framework compatibility

A framework integration means appropriate templates, dependencies, app discovery,
settings conventions, and development-server handling. Similar route syntax alone
does not establish a tested integration.

| Framework / ecosystem | Intended integration | Status in 0.5.0 |
|-----------------------|----------------------|-----------------|
| FastAPI | Direct FastAPI app, typed settings, Uvicorn development workflow | **Implemented** |
| Flask | Flask app/app-factory templates and its WSGI/development workflow | Planned |
| Django | Django project/settings conventions and management commands | Planned |
| Django REST Framework / Django Ninja | Django-aware API scaffolding and feature hooks | Planned |
| Django Bolt | Django-aware templates and Bolt's own server workflow | Planned |
| TurboAPI | TurboAPI templates and its framework-specific runtime workflow | Planned |
| Other Python API frameworks | Additional adapters using the shared toolkit contract | Future extension direction |

**Verified framework details:** [TurboAPI](https://github.com/justrach/turboAPI)
provides a Python API with a Zig HTTP core. It is more precise to describe it as
Python-facing with a Zig-backed HTTP runtime than as entirely implemented in Zig.
[Django Bolt](https://github.com/dj-bolt/django-bolt) is a separate Django API
framework with a Rust/Actix Web server.

Boltra's Python implementation remains independent of those internal runtimes.
A future adapter must still respect the selected framework's dependency, Python,
and server requirements. Compatibility with TurboAPI or Django Bolt has not yet
been tested or shipped in Boltra.

## 🏗️ Architecture and framework selection

The intended architecture separates **shared project tooling** from
**framework-specific adapters**:

```text
Application chooses its API framework
                 |
                 v
Boltra shared workflow
CLI · project files · configuration · environment handling
                 |
                 v
Framework adapter (planned extension boundary)
Templates · dependencies · settings conventions · server commands
                 |
        +--------+--------+---------+------------+-----------+
        |        |        |         |            |           |
     FastAPI   Flask    Django   Django Bolt   TurboAPI   Future adapters
```

The shared pieces already live in separate `cli/`, `project/`, and `dev/` modules.
The current templates are FastAPI-specific and the current server launcher uses
Uvicorn. An adapter registry and actual framework-selection dispatch still need
to be implemented before additional modes can run.

The design goal is straightforward: a FastAPI project selects the FastAPI adapter;
a Flask project selects the Flask adapter; Django-based and custom-runtime projects
select their corresponding adapters. Each adapter supplies the appropriate project
files and runtime commands without hiding the underlying framework.

### Current working configuration

The generated FastAPI project contains:

```toml
[tool.boltra]
mode = "fastapi-kit"
app = "main:app"
settings = "settings.py"
host = "127.0.0.1"
port = 8000
```

In **0.5.0, `mode` is an informational label**, not a framework selector. Changing
it to `flask-kit` does not generate a Flask application or change the server.

### Proposed framework-selection configuration

The following illustrates the future adapter design. **It is a proposal, not a
working Flask configuration or a supported command in 0.5.0.**

```toml
# Conceptual example for a future Flask adapter.
[tool.boltra]
framework = "flask"
mode = "flask-kit"
app = "main:app"
host = "127.0.0.1"
port = 8000
```

Once adapters exist, the selected framework should determine templates,
dependencies, app loading, and server behavior. Unsupported choices should produce
an explicit error. The final configuration schema and CLI selection syntax will
be documented when implemented.

Read the [framework adapter design](doc/developer/framework-adapters.md) for
responsibilities, compatibility criteria, and implementation boundaries.

## ✅ Implemented capabilities

| Capability | Available behavior |
|------------|--------------------|
| `boltra new <name>` | Generates a direct FastAPI app, settings, dependencies, and `.env.example` |
| `boltra dev` | Finds the project, starts Uvicorn, and reloads Python-source changes |
| Typed settings | Loads environment variables and `.env` through Pydantic settings |
| Project validation | Rejects invalid names/existing destinations and handles write failures |
| Server configuration | Reads app target, host, and port from `[tool.boltra]` |
| Windows development reload | Uses a Python compatibility runner for worker restart |
| Help and version | Supports `--help`, `--version`, and `python -m boltra` |
| Distribution checks | Verifies the pure Python wheel, templates, typing marker, and clean install |

Additional framework adapters, app management, ORM, admin, auth, workers, and AI
are planned. See the [roadmap](doc/plan/phase.md) for milestones.

## 🚀 Quick start: FastAPI

Requirements for the implemented workflow: **Python 3.12+** and **uv**.
Install this checkout as a separate CLI tool:

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

On PowerShell, `Copy-Item .env.example .env` also copies the example.
Set your own `SECRET_KEY` in `.env`; the generated default triggers a warning.

Open [the application](http://127.0.0.1:8000/) and
[interactive API documentation](http://127.0.0.1:8000/docs).

The home endpoint returns:

```json
{"message": "Hello from FastAPI + Boltra Kit"}
```

To extend the app, add an ordinary FastAPI route to `main.py`:

```python
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

The server reloads the change. Visit `/health` or call it through `/docs`.
See the [complete quickstart](doc/user/quickstart.md) for a working school API example.

## 📁 Project layout and configuration

The current scaffold starts with four files:

```text
school_api/
├── main.py          # FastAPI application and routes
├── settings.py      # Typed settings and environment loading
├── pyproject.toml   # App dependencies and Boltra server metadata
└── .env.example     # Example local environment variables
```

The application declares its own FastAPI, Pydantic-settings, and Uvicorn
dependencies. Boltra is a development tool and is not added as an app runtime
dependency. The launcher prefers the app's `.venv`, with `uv run` as a fallback.

Set the API title and local values in `.env`:

```dotenv
API_TITLE=School API
DEBUG=true
SECRET_KEY=replace-with-your-own-random-secret
ALLOWED_HOSTS=["localhost","127.0.0.1"]
```

Change `[tool.boltra].port` to use another port, or set `app = "backend.main:app"`
for a packaged application. Restart the command after changing `.env` or
`pyproject.toml`; automatic reload watches Python source files.

`ALLOWED_HOSTS`, database configuration, and reserved feature flags are settings
data at this stage. They do not activate host middleware, an ORM, or auth modules.
The [settings guide](doc/user/settings.md) explains actual behavior and defaults.

Windows development reload terminates the old worker, so application shutdown
hooks are not guaranteed during these restarts. Use the framework's normal
production-server setup for deployments; for the current FastAPI workflow, run
ordinary Uvicorn without reload.

## 📚 Documentation

| Audience / task | Guide |
|-----------------|-------|
| Install the CLI | [Installation](doc/user/installation.md) |
| Create and extend an app | [Complete quickstart](doc/user/quickstart.md) |
| Commands, errors, exit statuses | [CLI reference](doc/user/cli.md) |
| Environment values and caching | [Settings reference](doc/user/settings.md) |
| Contributor starting point | [Developer guide](doc/developer/README.md) |
| Understand individual source files | [File-by-file reference](doc/developer/file-reference.md) |
| Understand the directory layout | [Repository structure](doc/developer/project-structure.md) |
| Multi-framework implementation direction | [Framework adapter design](doc/developer/framework-adapters.md) |
| Recorded validation | [Verification report](doc/developer/verification.md) |
| Future implementation | [Python-first roadmap](doc/plan/phase.md) |

## 🛠️ Development and quality checks

```bash
uv sync --locked --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run pytest --cov=boltra --cov-report=term-missing
uv build
```

The recorded local verification covers Python 3.12, 3.13, and 3.14 on Windows,
with **109 tests per version** and **91% Python statement coverage**. These checks
verify the implemented FastAPI workflow and package, not the planned adapters.
See the [verification report](doc/developer/verification.md) for scope and limits.

Source is organized by responsibility:

```text
src/boltra/
├── cli/             # Entry point, command routing, and argument parsing
├── project/         # Generation, validation, and packaged template assets
└── dev/             # Configuration, environment selection, and server launch
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for checks and commit conventions.

## License

[MIT](LICENSE) — Boltra Contributors.
