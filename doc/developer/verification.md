# Python-only verification report

Verified on October 7, 2026, against the local source version **0.5.0**.
This report replaces the previous native-build audit: current implementation,
build configuration, tests, and distributions are Python-only.

## Results

| Check | Result |
|-------|--------|
| Complete suite, Python 3.12.14 | 156 passed, 1 skipped |
| Complete suite, Python 3.13.15 | 156 passed, 1 skipped |
| Complete suite, Python 3.14.7 | 156 passed, 1 skipped |
| Python statement coverage (3.14) | 94% |
| Ruff lint and formatting | Passed |
| Generated Python-template lint/format | Passed |
| Strict mypy | Passed |
| Configured pre-commit hooks | Passed |
| Pure Python wheel/source archive | Built and inspected |
| Wheel installation in fresh environment | CLI, module entry point, and template resources passed |
| Local documentation links | No broken targets |

The complete suite includes unit/regression checks, real HTTP/reload integration,
and three packaging checks. Tests were executed on Windows. Linux/macOS execution
is configured in CI; this report does not claim remote CI has run.

This run includes Phase 5 app scaffolding. The skipped case requires creating a
real filesystem symbolic link; the local Windows account lacks that permission.
Name/collision/source-edit checks and all failure-recovery tests ran successfully.

## What was exercised

- CLI help, version, argument validation, single error/help output, and exit status.
- Project generation, generated imports/JSON route, existing destinations,
  filesystem errors, and partial-write cleanup.
- Pydantic and first-import fallback settings: precedence, explicit overrides,
  booleans, independent lists, caching, and default-secret warnings.
- Project discovery, TOML/encoding/type/app-path validation, environment selection,
  host/port, IPv6 URLs, launch errors, and Ctrl+C handling.
- Real generated app dependency sync; home JSON, Swagger/OpenAPI, `.env` title,
  two app endpoints/OpenAPI tags, a third app added during live serving, and two
  consecutive Python-source reloads.
- App package generation, direct/aliased/annotated FastAPI instances, custom
  module/attribute targets, BOM/CRLF/comments, Unicode string preservation,
  invalid names, duplicate imports, existing files, and unsupported app factories.
- Failed writes/replacements clean only created files and preserve original
  source. A detected concurrent source edit is retained and cancels generation.
- A `py3-none-any` wheel containing template resources, `py.typed`, and the correct
  console entry point, with no project-owned compiled/native artifact.
- A source archive limited to maintained files, excluding environments, cache
  apps, obsolete native source, and bytecode.
- Clean installed-package use outside the checkout without application libraries:
  both `python -I -m boltra` and the console script can scaffold a project.
  The installed console script can also create/register an app using packaged
  router resources before FastAPI dependencies are installed.

The source-archive test found that nested cached `.env.example` files could bypass
broad ignore patterns. An explicit maintained-file allowlist fixed that issue;
the corrected archive passed verification.

## Coverage and compatibility limits

Coverage measures the main test process. The Windows runner and generated app
execute in separate environments; their behavior is verified by integration
rather than included in that statement percentage.

Windows development reload uses Uvicorn's internal supervisor API to terminate
only the old worker, avoiding the console-signal hang previously reproduced.
Worker lifespan shutdown hooks are not guaranteed during Windows development
reload/shutdown. Use ordinary Uvicorn without reload for production.

No package was published by this verification. Build outputs are local artifacts;
release/publishing is a separate action.

## Repeat the checks

```bash
uv sync --locked --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run pytest --cov=boltra --cov-report=term-missing
uv run pre-commit run --all-files
uv build
```

See [testing](testing.md) for targeted commands and sandbox/temp-path guidance.
