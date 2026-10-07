# Developer guide

Boltra is a Python package under `src/boltra/`. Start with the architecture, then
use the file reference to choose where to make a change.

| Guide | Purpose |
|-------|---------|
| [Architecture](architecture.md) | Command flow, boundaries, templates, and server environments |
| [Repository structure](project-structure.md) | Complete maintained directory layout |
| [File reference](file-reference.md) | Every source file's functions, responsibilities, and tests |
| [Development workflow](development-workflow.md) | Setup, daily commands, changes, and commits |
| [Testing](testing.md) | Unit, settings, HTTP/reload, package, and coverage checks |
| [Verification results](verification.md) | Recorded local results and their limits |
| [Releasing](releasing.md) | Version, build, inspect, tag, and publish |

## Set up

```bash
uv sync --locked --group dev
uv run boltra --help
uv run pytest
```

Hatchling builds a platform-independent wheel; uv manages the editable Python
environment. No native toolchain is part of the build.

## Read the implementation

1. `cli/cli.py` — starts and routes commands.
2. `cli/parser.py` — turns arguments into `ParsedCommand` data.
3. `project/generator.py` — creates projects and handles collisions/errors.
4. `project/template_engine.py` and `templates/` — define generated output.
5. `dev/config.py` — locates and validates project configuration.
6. `dev/server.py` — selects an environment and launches Uvicorn.
7. `dev/windows.py` — handles Windows reload compatibility.
8. `apps/generator.py`, `registration.py`, and `validation.py` — create modular
   apps, register routers through AST-located edits, and enforce package-name rules.

Paths above are inside `src/boltra/`. The [roadmap](../plan/phase.md) identifies
safe app removal, router auto-discovery, and the Python ORM as future work.
