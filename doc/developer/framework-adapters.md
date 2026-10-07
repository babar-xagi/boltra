# Framework adapter design

**Status: proposed architecture.** The current source implements FastAPI templates
and Uvicorn development serving. There is no adapter registry, framework-selection
CLI flag, Flask launcher, or Django/TurboAPI/Bolt integration yet.

## Product goal

Boltra is a general-purpose Python API development kit. Shared tooling should
support application teams choosing FastAPI, Flask, Django-based APIs, Django Bolt,
TurboAPI, or future frameworks. Applications retain their framework's ordinary
routing, validation, settings, and deployment conventions.

## Current implementation boundaries

| Existing module | Current behavior | Adapter evolution |
|-----------------|------------------|-------------------|
| `cli/cli.py` | Routes new/dev/help/version | Resolve framework choice before domain work |
| `cli/parser.py` | Parses existing commands | Add selection only after a tested schema exists |
| `project/validation.py` | Validates project names | Remain shared across adapters |
| `project/generator.py` | Creates files and handles cleanup | Obtain a file manifest from the chosen adapter |
| `project/template_engine.py` | Renders FastAPI assets | Load adapter-specific resource sets |
| `dev/config.py` | Loads app/host/port plus metadata labels | Validate supported framework selections |
| `dev/server.py` | Builds Uvicorn commands | Delegate launch to the adapter's runtime strategy |

These seams make extension possible, but the adapter behavior itself still needs
implementation. `mode` currently appears in the banner and does not dispatch a
framework. Changing its string cannot convert the generated application.

## Proposed adapter responsibilities

A framework adapter should define:

1. **Identity and compatibility:** stable identifier, Python/dependency versions,
   supported framework releases, and optional capabilities.
2. **Project manifest:** starter files, framework imports, and dependency declarations.
3. **Settings conventions:** Pydantic settings, Flask configuration, or Django
   settings as appropriate; preserve native framework practices.
4. **Application discovery:** module targets, Flask factories, Django management
   context, or a framework's own application object.
5. **Development runtime:** ASGI, WSGI, framework management command, or dedicated
   server. Do not send every framework through Uvicorn.
6. **Feature hooks:** framework-appropriate routes, app registration, testing,
   and optional modules. Capability differences must be explicit.
7. **Acceptance checks:** clean installation, scaffold import, real HTTP response,
   settings loading, dev reload/shutdown behavior, and useful errors.

A conceptual core-to-adapter contract has three operations: produce a project file
manifest, validate runtime configuration, and build/launch a development command.
The concrete Python interface is not frozen and should be specified before code.

## Configuration direction

A future selector should clearly identify a framework, separately from descriptive
mode labels. For example, the proposed `framework = "fastapi"` or
`framework = "flask"` would choose an adapter. These keys are illustrative and
are not selectors implemented in version 0.5.0.

Unsupported frameworks must fail explicitly once dispatch exists. Avoid accepting
a Flask label while launching a FastAPI/ASGI command. Existing `fastapi-kit`
projects need a documented migration/default when selectors become available.

## Framework-specific considerations

| Framework | Runtime considerations to verify |
|-----------|----------------------------------|
| FastAPI | Existing templates, Pydantic settings, and Uvicorn path remain tested |
| Flask | WSGI, app instances/factories, Flask configuration and dev commands |
| Django / DRF / Ninja | Django settings/apps, management commands, existing ORM and API conventions |
| Django Bolt | Django conventions plus Bolt's own server command and capability checks |
| TurboAPI | Its Python interface, Zig-backed runtime, Python requirements, and server workflow |

Flask's official [deployment guide](https://flask.palletsprojects.com/en/stable/deploying/)
describes its WSGI application/server model. Django documents both
[WSGI and ASGI deployment](https://docs.djangoproject.com/en/stable/howto/deployment/).

[TurboAPI's repository](https://github.com/justrach/turboAPI) identifies a Python
framework with a Zig HTTP core and a dedicated runtime workflow.
[Django Bolt's repository](https://github.com/dj-bolt/django-bolt) describes its
Django integration and Rust/Actix Web server. These are separate projects, not
Boltra dependencies or evidence of an existing Boltra integration. Details were
checked on October 7, 2026; adapter implementation must recheck supported releases.

Boltra's own core remains Python. A selected framework can have separate runtime
or native dependency requirements without changing the toolkit's implementation.

## Suggested implementation order

1. Specify the selector, adapter contract, errors, and compatibility matrix.
2. Place the existing FastAPI behavior behind the contract without regressions.
3. Implement and test Flask with its appropriate runtime path.
4. Add Django-based adapters, accounting for their existing settings/ORM ecosystem.
5. Evaluate Django Bolt and TurboAPI against their actual runtime requirements.
6. Document a tested extension mechanism for additional frameworks.

An adapter becomes "supported" only after scaffold, configuration, launch, and
integration tests pass. Documentation should keep planned and implemented modes
separate until then.
