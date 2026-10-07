# Rusjango ideas carried forward

Boltra preserves useful project-development ideas while using direct FastAPI
applications and a Python-first implementation.

| Idea | Boltra destination | Status |
|------|--------------------|--------|
| Small starter | Generator and readable templates | Implemented |
| One-command server | Config, launcher, Windows runner | Implemented |
| Typed environment settings | Generated `settings.py` | Implemented |
| App add/remove | Future apps and CLI handlers | Planned |
| Installed-app configuration | Structured editor/router discovery | Planned |
| Async model/query ergonomics | Future Python ORM specification | Planned |
| Optional admin/auth/workers | Future Python modules/scaffolding | Planned |

## Rewrite deliberately

- Use `fastapi.APIRouter`, not a custom router/compiler.
- Use Pydantic models/settings, not a custom schema engine.
- Use structured editing rather than regex mutation of user-owned Python files.
- Treat previous behavior/API ideas as specifications; do not copy code blindly.
- Keep validation/generation in domain modules instead of the CLI.
- Specify migrations and exceptions before exposing an ORM API.

## Order

1. Complete app creation/removal, settings editing, router discovery.
2. Specify and test the Python ORM in vertical slices.
3. Recreate an example school API using FastAPI and that ORM.
4. Add admin/auth and document the migration path.

Archiving/deprecating other projects is a separate maintainer decision. Current
scope is documented in [the roadmap](phase.md).
