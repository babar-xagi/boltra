# Python-first execution roadmap

Build each feature in Python: specify behavior, implement a useful vertical
slice, test it, and document it before expanding scope.

## Current status

| Capability | Status |
|------------|--------|
| Python package, CLI, quality tooling | Implemented |
| Four-file FastAPI project generation | Implemented |
| Typed settings and `.env.example` | Implemented |
| Dev server, custom app/host/port, reload | Implemented |
| Pure Python distribution and documented modules | Implemented |
| App creation and explicit router registration (Phase 5) | Implemented |
| Safe app removal (Phase 6) | Next |
| Structured settings and router discovery | Planned |
| ORM and other batteries | Planned |

Validation is recorded in [the verification report](../developer/verification.md).
The source version is 0.5.0; package publication is a separate release action.

## Foundation

| Phase | Deliverable | Exit check |
|-------|-------------|------------|
| 0 | Repository, package, quality/CI | Lint/types/tests/build configured |
| 1 | Help/version and console entry | CLI and `python -m boltra` work |
| 2 | Minimal generator | Imports, collisions, failed-write behavior verified |
| 3 | Development server | Real HTTP/OpenAPI and repeated reloads |
| 4 | Pydantic settings and `.env` | Both settings paths, precedence, warnings tested |
| 5 | `boltra add app <name>` | APIRouter scaffold gives a reachable route |
| 6 | Safe `boltra remove app` | Confirmation and no orphan imports/settings |
| 7 | Structured settings editor | Idempotent updates without fragile regex editing |
| 8 | Router auto-discovery | Three apps load without manual router imports |

Phases 0–5 are implemented. Finish 6–8 before starting ORM implementation.

## Python ORM

| Phase | Deliverable | Exit check |
|-------|-------------|------------|
| 9 | API/dialect/lifecycle spec | Clear create/get/filter/error contracts |
| 10 | Async PostgreSQL pool | Real DB lifecycle/concurrency/shutdown tests |
| 11 | Model registry/basic fields | Metadata/validation without database I/O |
| 12 | Table creation/DDL | Model-defined table exists in DB test |
| 13 | Create/get by primary key | Roundtrip and injection tests |
| 14 | Filters/order/pagination | Lookups and compiler behavior tested |
| 15 | Update/delete | Instance and filtered operations verified |
| 16 | CLI/lifespan integration | Fresh app supports a model-backed API |
| 17 | Python migration files and schema history | Schema changes/history verified; implemented in Python |
| 18 | Transactions, retries, API review | Stable Python API and benchmarks |
| 19 | Python ORM benchmarks | Documented workloads/results/profiling |

Use asyncpg for PostgreSQL first; SQLite can follow as a separately tested backend.
Design exceptions and migrations before exposing an ORM API. No ORM code is
implemented yet. Do not silently wrap another ORM under a new API.

## Batteries and release

| Phase | Focus |
|-------|-------|
| 20–22 | Admin design, registration, backend, minimal UI |
| 23–24 | Authentication and role permissions |
| 25–26 | Background jobs, Docker, and application test scaffolding |
| 27 | Thin provider/chat AI integration |
| 28–29 | Security defaults and observability |
| 30 | Benchmarks, guides, example application |
| 31 | Public beta and feedback/bug fixes |
| 32 | Stable 1.0 and frozen supported APIs |

Admin depends on a tested ORM. Payments, GraphQL, multi-tenancy, and a separate
HTTP engine remain future proposals.

## Quality gate

- Behavioral tests and relevant filesystem/HTTP/database integration.
- Public types/docstrings and comments for non-obvious design choices.
- Ruff, strict mypy, complete tests, and clean installed-package behavior.
- User examples, file-reference updates, and a changelog entry.
- Benchmarks before performance claims; profile the Python implementation first.

Ship one coherent milestone at a time. Optional optimizations must not make
Python functionality or installation depend on a native toolchain.
