# Boltra Development Plan — Phased Roadmap

> **Status:** Active
> **Parent doc:** [`boltra-doc.md`](../../boltra-doc.md)
> **ORM decision:** From-scratch, async-first Python + Rust-powered acceleration
> **Rusjango migration:** [`rusjango-migration.md`](rusjango-migration.md) — priority map from archived Rusjango work

This document is the **execution plan**. Each phase is small, shippable, and gated by quality checks before the next phase starts.

---

## Rusjango Migration Priority (Summary)

Boltra is the **primary project**. Rusjango ([babar-xagi/Rusjango](https://github.com/babar-xagi/Rusjango)) is reference only — archive after Boltra catches up.

| Priority | Boltra phases | Goal |
|----------|---------------|------|
| **P0 — next** | 4 → 5 → 6 → 7 | Settings, `add app`, `remove app`, AST settings editor |
| **P1** | 8 + PyPI | `load_apps`, publish to PyPI |
| **P2** | 9 → 17 | ORM core + `add orm` + `migrate` (Rusjango Phase 3 parity) |
| **P3 — skip** | — | Rusjango custom routing, Schema, ASGI — use FastAPI/Pydantic |
| **P4 — later** | 22+ | Admin, auth, Docker, workers, AI |

Full file-level porting guide: [`rusjango-migration.md`](rusjango-migration.md).

---

## How to Use This Plan

1. **One phase at a time** — do not start Phase N+1 until Phase N meets its exit criteria.
2. **No feature creep inside a phase** — if something belongs to a later phase, write it down and defer it.
3. **Tests before merge** — every phase adds or extends tests; no untested public API.
4. **Benchmark when touching hot paths** — especially ORM query compilation and row decoding.
5. **Document what ships** — each phase updates a short changelog entry in `doc/plan/CHANGELOG.md` (create when Phase 0 completes).

---

## Development Principles

| Principle | Meaning |
|-----------|---------|
| **Slow but impactful** | Fewer phases shipped, each one clearly useful |
| **Async-first** | Public APIs are `async`; no sync-by-default database calls |
| **Rust where it wins** | SQL builder and row decoder in Rust; Python always has fallback |
| **Direct FastAPI** | Generated projects use real FastAPI — no hidden wrapper |
| **Removable batteries** | Every `boltra add X` has a safe path to remove |
| **Clean boundaries** | CLI, project, apps, ORM, admin — separate internal modules |
| **Optimize later, correctly first** | Correctness + clarity before micro-optimizations |

---

## Quality Gates (Every Phase)

Before marking any phase **done**, all of the following must pass:

- [ ] **Unit tests** for new logic (target: ≥ 90% coverage on new code)
- [ ] **Integration test** if the phase touches CLI, filesystem, or database
- [ ] **Type hints** on all public functions and classes (`mypy` or `pyright` clean)
- [ ] **Ruff** lint + format with zero warnings
- [ ] **Docstring** on every public API symbol
- [ ] **No TODO without issue link** in merged code
- [ ] **Manual smoke test** recorded in phase notes (command + expected output)

ORM and Rust phases additionally require:

- [ ] **Benchmark baseline** saved under `benchmarks/results/`
- [ ] **Python fallback path** tested when Rust extension is disabled

---

## Phase Map (Overview)

```text
FOUNDATION (Phases 0–8)     CLI, project gen, apps, settings
        ↓
ORM CORE (Phases 9–18)      From-scratch async ORM, Python layers
        ↓
ORM RUST (Phases 19–21)     SQL builder, row decoder, pool helpers
        ↓
BATTERIES (Phases 22–28)    Admin, auth, worker, AI, Docker, tests
        ↓
HARDENING (Phases 29–32)    Observability, security, benchmarks, beta
        ↓
V1 (Phase 33)               Stable release
```

Estimated pace: **1–3 weeks per phase** depending on complexity. ORM phases may take longer — that is expected.

---

# FOUNDATION TRACK

## Phase 0 — Repository & Engineering Standards

**Goal:** A repo that is ready for consistent, high-quality contributions.

**Deliverables:**

- Monorepo layout:

  ```text
  boltra/
  ├── src/boltra/          # main Python package
  ├── crates/              # Rust workspace (empty stub for now)
  ├── tests/
  ├── benchmarks/
  ├── doc/
  │   └── plan/
  │       └── phase.md     # this file
  ├── pyproject.toml
  ├── Cargo.toml           # workspace root
  ├── README.md
  ├── LICENSE              # MIT recommended
  └── CONTRIBUTING.md
  ```

- Tooling configured: `ruff`, `pytest`, `mypy`, `pre-commit`
- CI workflow: lint + test on push
- `doc/plan/CHANGELOG.md` stub

**Exit criteria:** `pytest` runs (even if zero tests). CI green on empty package.

**Do not:** Implement CLI or ORM yet.

---

## Phase 1 — Minimal CLI Package

**Goal:** Installable `boltra` command with help output.

**Deliverables:**

- `boltra --help`, `boltra --version`
- Package entry point in `pyproject.toml`
- Basic CLI structure using `typer` or `click`

**Exit criteria:** `pip install -e .` then `boltra --help` works.

---

## Phase 2 — Project Generator (`boltra new`)

**Goal:** Generate a minimal, honest FastAPI project.

**Deliverables:**

- `boltra new <name>` creates:

  ```text
  <name>/
  ├── main.py
  ├── settings.py
  └── pyproject.toml
  ```

- Direct FastAPI `main.py` (no wrapper)
- Name validation, no overwrite of existing directory
- Success message with next steps

**Exit criteria:** Generated project imports without error. Integration test creates temp project.

**Do not:** Add apps, ORM, or extra folders.

---

## Phase 3 — Dev Server (`boltra dev`)

**Goal:** One command to run the generated app.

**Deliverables:**

- Reads `[tool.boltra]` from `pyproject.toml`
- Runs `uvicorn main:app --reload`
- Prints URL, docs URL, mode

**Exit criteria:** `boltra new demo && cd demo && boltra dev` serves `/` and `/docs`.

---

## Phase 4 — Pydantic Settings & `.env`

**Goal:** Production-ready configuration from day one.

**Deliverables:**

- Generated `settings.py` uses `pydantic-settings`
- `.env.example` in project template
- `SECRET_KEY` warning when default value used

**Exit criteria:** Settings load from `.env` in integration test.

---

## Phase 5 — App System (`boltra add app`)

**Goal:** Django-like modular apps with FastAPI routers.

**Deliverables:**

- `boltra add app <name>` creates `apps/<name>/api.py` with `APIRouter`
- Updates `INSTALLED_APPS` in settings
- Updates `main.py` to include router (until Phase 8)

**Exit criteria:** New route reachable after add. Test covers generation.

---

## Phase 6 — Remove App (`boltra remove app`)

**Goal:** Safe, reversible-feeling removal of apps.

**Deliverables:**

- Confirmation prompt `[y/N]`
- Removes folder, settings entry, router import
- Summary of changes printed

**Exit criteria:** After remove, app routes 404 and no orphan imports.

---

## Phase 7 — Settings Manager (Internal)

**Goal:** Reliable programmatic settings updates for CLI.

**Deliverables:**

- Safe read/write of `INSTALLED_APPS` and feature flags
- AST-based or structured editing (no fragile regex)
- Idempotent operations

**Exit criteria:** Adding same app twice does not duplicate entries. Unit tests for editor.

---

## Phase 8 — Router Auto-Discovery (`load_apps`)

**Goal:** Stop hand-editing `main.py` for every app.

**Deliverables:**

- `boltra.apps.load_apps(app)` reads `INSTALLED_APPS`, imports `api.router`
- Generated `main.py` template uses `load_apps`
- Clear error if router missing

**Exit criteria:** Three apps load without manual imports. Integration test.

**Foundation track complete** when Phase 8 exits. Only then start ORM Phase 9.

---

# ORM TRACK — From-Scratch, Async-First (Python Core)

> ORM is built in **thin vertical slices**: each phase adds one capability end-to-end
> (model → SQL → execute → return instance), not a whole layer at once.

## Phase 9 — ORM Design Specification

**Goal:** Written spec before any ORM code. Prevents rework.

**Deliverables:**

- `doc/plan/orm-spec.md` covering:
  - Public API (`Model`, fields, `QuerySet` method names)
  - SQL dialect rules (PostgreSQL first)
  - Async connection lifecycle diagram
  - Rust boundary interface (what crosses the FFI line)
  - Migration file format (design only)
  - Error types and exception hierarchy
  - Naming conventions for tables and columns
- Review checklist signed off (self-review or peer)

**Exit criteria:** Spec document complete. No open questions on `create` / `filter` API shape.

**Do not:** Write implementation code.

---

## Phase 10 — Async Connection Layer

**Goal:** Stable PostgreSQL connection pool — no ORM queries yet.

**Deliverables:**

- `boltra.orm.connection` module
- `asyncpg` pool: create, acquire, release, close
- Settings integration: `DATABASE.URL`, `POOL_SIZE`
- Health check: `await connection.is_ready()`
- SQLite stub interface (raise `NotImplementedError` until later)

**Exit criteria:**

- Integration test against real PostgreSQL (Docker or service)
- Pool handles 100 concurrent acquire/release without leak
- Clean shutdown on app lifespan events

**Do not:** Model classes or query builder.

---

## Phase 11 — Model Registry & Field Types (Python)

**Goal:** Declare models; map to SQL table metadata.

**Deliverables:**

- `Model` base class with `__tablename__` convention
- Fields: `Integer`, `String`, `Boolean`, `DateTime`
- Field options: `primary_key`, `null`, `default`, `max_length`
- Model registry: table name → model class
- Schema introspection: `Model.table_schema()` → column definitions

**Exit criteria:**

- Unit tests for field validation and table metadata
- No database I/O yet — metadata only

---

## Phase 12 — DDL & Table Creation (Python SQL)

**Goal:** Create tables from models — first end-to-end SQL.

**Deliverables:**

- `await Model.create_table()` — `CREATE TABLE IF NOT EXISTS`
- Python-based SQL generation for DDL (simple, readable)
- `await Model.drop_table()` for tests only

**Exit criteria:**

- Integration test: define `Student` model → create table → table exists in PG

**Do not:** Rust SQL builder yet. DDL volume is low; Python is fine.

---

## Phase 13 — Insert & Get (Write + Read by PK)

**Goal:** First full CRUD vertical slice.

**Deliverables:**

- `await Student.create(name="Ali", age=20)` → returns instance with `id`
- `await Student.get(id=1)` → instance or raise `DoesNotExist`
- Parameterized queries only — no string interpolation of values
- `boltra.orm.exceptions`: `DoesNotExist`, `MultipleObjectsReturned`

**Exit criteria:**

- Integration test: create → get → values match
- SQL injection test with malicious string field

---

## Phase 14 — Filter QuerySet (Read)

**Goal:** Django-style filtering — the most used ORM surface.

**Deliverables:**

- `await Student.filter(age__gte=18).all()`
- Lookups: `exact`, `gte`, `lte`, `gt`, `lt`, `in`, `isnull`
- Chainable: `.filter().order_by("name").limit(10).offset(0)`
- `.first()`, `.count()`, `.exists()`
- Python query compiler: filter dict → SQL `WHERE` clause

**Exit criteria:**

- Integration tests for each lookup type
- Compiler unit tests with snapshot SQL strings
- `.all()` on 1000 rows completes without loading duplicates

**Do not:** Joins, relationships, aggregates.

---

## Phase 15 — Update & Delete (Write)

**Goal:** Complete basic CRUD.

**Deliverables:**

- `await student.update(age=21)` and `await Student.filter(...).update(...)`
- `await student.delete()` and `await Student.filter(...).delete()`
- `save()` on dirty instance (optional if update covers it — pick one, document it)

**Exit criteria:**

- Integration tests: update changes DB; delete removes row
- Filter-update and filter-delete tested

---

## Phase 16 — CLI Integration (`boltra add orm`)

**Goal:** Users add ORM to a Boltra project via CLI.

**Deliverables:**

- `boltra add orm` updates settings, adds `migrations/` folder, sample model in first app
- Connection init on app startup (lifespan hook)
- `boltra doctor` checks DB connectivity

**Exit criteria:**

- Fresh project + add orm + create table + hit API using model works end-to-end

---

## Phase 17 — Boltra-Native Migrations (MVP)

**Goal:** Track schema changes without Alembic.

**Deliverables:**

- Migration file format: numbered, JSON or Python DSL
- `boltra makemigrations` — diff model metadata vs DB
- `boltra migrate` — apply pending migrations
- `boltra_migration_history` table

**Exit criteria:**

- Test: add field to model → makemigrations → migrate → column exists
- Downgrade not required in MVP (document as limitation)

**Do not:** Auto-merge conflicts, multi-db migrations.

---

## Phase 18 — ORM Hardening & Public API Freeze (Pre-Rust)

**Goal:** Stabilize Python-only ORM before Rust acceleration.

**Deliverables:**

- Connection retry and timeout settings
- Query logging hook (debug mode)
- Transaction context manager: `async with db.transaction():`
- API review: freeze method names documented in orm-spec
- Benchmark baseline: create, get, filter-100, filter-1000 rows

**Exit criteria:**

- Benchmark results committed to `benchmarks/results/orm-python-baseline.json`
- No API renames after this phase without deprecation policy

**ORM Python core complete** when Phase 18 exits. Start Rust track.

---

# ORM TRACK — Rust-Powered Acceleration

> Rule: **benchmark first, Rust second.** Each Rust module must beat Python baseline
> on the target workload or it does not ship.

## Phase 19 — Rust Workspace & PyO3 Bridge

**Goal:** Build and import Rust extensions from Python reliably.

**Deliverables:**

- `crates/boltra-native/` with PyO3
- Maturin or setuptools-rust build pipeline
- CI builds wheels for Linux, macOS, Windows
- `boltra.orm._native` module with `is_available()` check
- Fallback: if import fails, ORM uses Python path silently (log info once)

**Exit criteria:**

- `pip install -e .` builds Rust on supported platforms
- Test passes with `BOLTRA_DISABLE_NATIVE=1`

---

## Phase 20 — Rust SQL Query Builder

**Goal:** Replace Python query compiler hot path for `filter`, `order_by`, `limit`.

**Deliverables:**

- Rust accepts: table name, columns, filter AST (JSON or structured dict)
- Returns: `(sql_string, param_list)` — parameterized always
- Python compiler delegates when native available
- Identifiers quoted safely; dialect: PostgreSQL

**Exit criteria:**

- Correctness: same results as Python compiler on 50+ query snapshots
- Speed: ≥ 2× faster compilation on benchmark suite vs Phase 18 baseline
- Fuzz test or property test on SQL injection resistance

**Do not:** Change public Python API.

---

## Phase 21 — Rust Row Decoder

**Goal:** Fast mapping from asyncpg records to model instances.

**Deliverables:**

- Rust decoder: column names + raw values → dict matching model fields
- Batch decode for `.all()` result sets
- Type coercion: int, str, bool, datetime

**Exit criteria:**

- Correctness: byte-identical instances vs Python decoder
- Speed: ≥ 2× on 1000-row fetch benchmark
- Memory: no measurable leak over 10k iterations

---

# BATTERIES TRACK

> Do not start admin until **ORM Phase 16** is complete.
> Do not start auth until **ORM Phase 13** (User model) is planned in orm-spec.

## Phase 22 — Admin Design & Registration API

**Goal:** Spec + `@register(Model)` decorator — no UI yet.

**Deliverables:**

- `doc/plan/admin-spec.md`
- `boltra.admin.register` stores list_display, search_fields, filters
- Model introspection from ORM metadata

**Exit criteria:** Registration unit tests. No frontend.

---

## Phase 23 — Admin Backend (CRUD API)

**Goal:** HTTP API for admin operations.

**Deliverables:**

- Admin router: list, retrieve, create, update, delete per registered model
- Pagination using ORM QuerySet
- Protected by auth stub (open in dev, flagged in spec)

**Exit criteria:** API tests for full CRUD on one model.

---

## Phase 24 — Admin Frontend MVP

**Goal:** Browser UI for data management.

**Deliverables:**

- Server-rendered HTML (Jinja2) or lightweight HTMX — avoid heavy SPA in v1
- Login, list, form, delete confirm
- Dark / light mode

**Exit criteria:** Manual smoke: create, edit, delete row in browser.

---

## Phase 25 — Auth MVP

**Goal:** User model, register, login, JWT, current user helper.

**Deliverables:**

- `boltra add auth` generates accounts app
- Password hashing: Argon2id
- JWT access token; refresh token optional in MVP
- `get_current_user` FastAPI dependency

**Exit criteria:** Protected route returns 401 without token, 200 with valid token.

---

## Phase 26 — Permissions MVP

**Goal:** Role-based route protection.

**Deliverables:**

- `@require_role("admin")` dependency
- Roles stored on User model
- Admin routes require admin role

**Exit criteria:** Role tests pass for admin vs non-admin.

---

## Phase 27 — Worker, Docker, Tests

**Goal:** Background jobs and deploy scaffolding.

**Deliverables:**

- `boltra add worker` — Redis broker, `@task` decorator, basic retry
- `boltra add docker` — Dockerfile, compose with PG + Redis
- `boltra add tests` — pytest + httpx AsyncClient + DB fixtures

**Exit criteria:** Task runs in worker process. Docker compose brings up app + PG.

**Defer:** AI module, payments — Phase 28+ or plugins.

---

## Phase 28 — AI Module MVP (Thin)

**Goal:** Minimal LLM integration — not a full agent framework.

**Deliverables:**

- `boltra add ai` — provider abstraction, one chat route, prompt file
- Streaming optional

**Exit criteria:** Chat route returns LLM response in integration test (mocked provider).

---

# HARDENING & RELEASE TRACK

## Phase 29 — Security Defaults

**Goal:** Safer generated projects.

**Deliverables:**

- CORS helper, secure headers middleware
- Rate limit on auth routes
- Startup fails on default `SECRET_KEY` when `DEBUG=False`
- `boltra check --security`

**Exit criteria:** Security check catches known bad configs in tests.

---

## Phase 30 — Observability

**Goal:** Production visibility.

**Deliverables:**

- Structured JSON logging
- Request ID middleware
- `/health/live` and `/health/ready`
- Slow query log when ORM debug enabled

**Exit criteria:** Health endpoints tested. Logs parse as JSON.

---

## Phase 31 — Benchmark Suite & Docs

**Goal:** Published numbers and learning path.

**Deliverables:**

- `boltra bench` command
- Compare: raw FastAPI, Boltra ORM Python path, Boltra ORM Rust path
- Quickstart docs for: new project, apps, ORM, admin, auth
- One example project: **school API** in Docker

**Exit criteria:** Benchmark README with reproducible commands. Example runs in CI.

---

## Phase 32 — Public Beta

**Goal:** Real users, feedback loop.

**Deliverables:**

- PyPI publish (or TestPyPI)
- Issue templates, roadmap in README
- Bug fix window — no new features unless critical

**Exit criteria:** Package installable from PyPI. Docs site live.

---

## Phase 33 — Version 1.0

**Goal:** Stable, trustworthy FastAPI kit with production-capable ORM.

**v1.0 must include:**

- `boltra new`, `boltra dev`, app add/remove, `load_apps`
- From-scratch async ORM: CRUD, filter, migrations, transactions
- Rust SQL builder + row decoder (with Python fallback)
- Admin MVP, auth MVP, permissions MVP
- Docker, tests, health, security defaults
- Docs + school API example + benchmarks

**v1.0 explicitly excludes:**

- Native API engine (research only)
- Full AI agent framework
- Payments (plugin later)
- Multi-tenancy, GraphQL

**Exit criteria:** Semantic version `1.0.0` tagged. CHANGELOG complete. API frozen per deprecation policy.

---

## Dependency Graph (Quick Reference)

```text
Phase 0–8   (Foundation)
              ↓
Phase 9     (ORM spec)
              ↓
Phase 10–18 (ORM Python core) ──→ Phase 19–21 (Rust ORM)
              ↓                           ↓
Phase 16    (boltra add orm) ←─────────────┘
              ↓
Phase 22–24 (Admin)
              ↓
Phase 25–26 (Auth + permissions)
              ↓
Phase 27–28 (Worker, Docker, AI thin)
              ↓
Phase 29–33 (Hardening → v1.0)
```

---

## What Not to Do (Global)

- Do not wrap SQLAlchemy, SQLModel, or Tortoise ORM
- Do not build the native API engine before v1.0
- Do not add Rust modules without benchmark proof
- Do not skip tests to “move faster”
- Do not expand scope mid-phase — open an issue and schedule next phase
- Do not generate bloated default projects — minimal first, add via CLI

---

## Current Phase

| Field | Value |
|-------|-------|
| **Active phase** | Phase 0 — not started |
| **Next action** | Initialize repo layout and tooling |
| **Blocked by** | Nothing |

Update this table when each phase completes.
