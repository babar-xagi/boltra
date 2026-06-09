# Rusjango → Boltra Migration Priority

> **Status:** Active
> **Parent doc:** [`phase.md`](phase.md)
> **Source repo:** [babar-xagi/Rusjango](https://github.com/babar-xagi/Rusjango) (archive after Boltra catches up)

Rusjango proved the product vision (3-file start, modular apps, async ORM, removable batteries).
Boltra is the **long-term home** for that vision — built on **real FastAPI**, not a custom framework wrapper.

This document maps what to **port**, **rewrite**, or **skip** from Rusjango, and in what order.

---

## Strategic Rules

| Rule | Meaning |
|------|---------|
| **Port ideas, not code blindly** | Rusjango CLI/templates are the best reference; routing/ASGI code is not |
| **FastAPI stays visible** | Generated `main.py` always uses `from fastapi import FastAPI` |
| **Pydantic over custom Schema** | Do not port `rusjango.schema` — use Pydantic models in generated apps |
| **APIRouter over custom Router** | App routes use `fastapi.APIRouter`, mounted at `/api/<app>/` |
| **AST over regex** | Rusjango `settings.rs` uses regex; Boltra Phase 7 must use structured editing |
| **Rusjango ORM API as reference** | `Model.create`, `filter`, lookups — same developer ergonomics, new implementation |

---

## Current Gap

| Area | Rusjango (shipped) | Boltra (v0.3.0) |
|------|-------------------|-----------------|
| Project scaffold | ✅ | ✅ Phase 2 |
| Dev server | ✅ | ✅ Phase 3 |
| Pydantic settings + `.env` | partial | ⏳ Phase 4 |
| `add app` / `remove app` | ✅ | ⏳ Phases 5–6 |
| `INSTALLED_APPS` + auto-mount | ✅ | ⏳ Phases 7–8 |
| Async ORM + migrations CLI | ✅ | ⏳ Phases 9–17 |
| PyPI published | ✅ | ❌ (target Phase 8+) |
| Custom routing framework | ✅ | ❌ **intentionally skipped** |

**Target:** Reach Rusjango Phase 3 parity (apps + ORM CLI) by **Boltra Phase 17**, with a better foundation.

---

## Priority Tiers

### P0 — Catch-up sprint (do next)

Ship these immediately after Phase 3. Highest ROI from Rusjango learnings.

| # | Boltra phase | Rusjango source | What to port / build | Notes |
|---|--------------|-----------------|----------------------|-------|
| 1 | **4** — Pydantic settings | `python/rusjango/.../settings.py`, `config.py` | `.env.example`, `pydantic-settings` in template, `SECRET_KEY` warning | Rusjango loader logic → adapt for FastAPI lifespan |
| 2 | **5** — `boltra add app` | `cli/src/add.rs`, `templates/app/` | App scaffold: `apps/<name>/api.py` with `APIRouter`, register in `INSTALLED_APPS` | Mount prefix `/api/<name>/` not Rusjango's internal Router |
| 3 | **6** — `boltra remove app` | `cli/src/remove.rs` | Confirmation `[y/N]`, `--yes` flag, cleanup summary | Same UX as Rusjango — users already expect this |
| 4 | **7** — Settings manager | `cli/src/settings.rs` | **Rewrite** with AST (not regex) for `INSTALLED_APPS` and feature flags | Rusjango regex patterns = anti-pattern for Boltra |

**Exit milestone (P0):** `boltra new demo && boltra add app school && boltra remove app school` works safely.

---

### P1 — Foundation parity with Rusjango Phase 2

| # | Boltra phase | Rusjango source | What to port / build | Notes |
|---|--------------|-----------------|----------------------|-------|
| 5 | **8** — `load_apps` | `python/rusjango/.../apps.py` | `boltra.apps.load_apps(app)` imports `api.router` from each `INSTALLED_APPS` entry | FastAPI `include_router`; no hand-edited `main.py` |
| 6 | — PyPI release | Rusjango `.github/workflows`, `pyproject.toml` | Publish `boltra` to PyPI after Phase 8 | Copy release workflow patterns from Rusjango |

**Exit milestone (P1):** Three apps load without manual imports; `pip install boltra` works.

---

### P2 — ORM parity with Rusjango Phase 3

Reference Rusjango ORM for **public API shape**; implement fresh in `boltra.orm` per [`phase.md`](phase.md) Phases 9–18.

| # | Boltra phase | Rusjango source | What to port / build | Notes |
|---|--------------|-----------------|----------------------|-------|
| 7 | **9** — ORM spec | `docs/05-orm-guide.md`, `orm/model.py`, `orm/query.py` | Write `doc/plan/orm-spec.md` — freeze `create`, `get`, `filter`, lookups | Match Rusjango ergonomics; PostgreSQL-first in Boltra |
| 8 | **10** — Connection | `orm/connection.py` | `asyncpg` pool + settings; SQLite via `aiosqlite` (Rusjango has both) | Boltra spec originally PG-first — add SQLite in Phase 10 or 12 |
| 9 | **11–12** — Models + DDL | `orm/fields.py`, `orm/model.py`, `orm/sql.py` | Field types, `create_table`, registry | Port SQL generation **ideas**; rewrite for injection safety |
| 10 | **13–15** — CRUD + filters | `tests/test_orm.py`, `orm/query.py` | `create`, `get`, `filter(__gte=)`, `update`, `delete` | Use Rusjango tests as **behavior spec** |
| 11 | **16** — `boltra add orm` | `cli/src/orm.rs`, `templates/orm/` | Settings `DATABASE`, `migrations/`, sample model in first app | Add `boltra remove orm` (Rusjango has this — Boltra should too) |
| 12 | **17** — `boltra migrate` | `cli/src/orm.rs` (`migrate` command) | `boltra migrate` creates tables from registered models | Rusjango MVP migrate = table creation; same scope for Boltra MVP |

**Exit milestone (P2):** Full school-app CRUD demo like Rusjango `examples/hello/` — but on FastAPI + Boltra ORM.

---

### P3 — Skip (do not port from Rusjango)

| Rusjango module | Why skip | Boltra replacement |
|-----------------|----------|-------------------|
| `app.py` — `Rusjango` class | Custom framework | `fastapi.FastAPI` |
| `routing.py` | Custom route compiler | FastAPI decorators + `APIRouter` |
| `asgi.py` | Custom ASGI | Starlette (via FastAPI) |
| `schema.py` | Custom Schema | Pydantic `BaseModel` |
| `middleware.py` / `security.py` | Early MVP | Starlette middleware; add in Boltra Phase 29+ hardening |
| `router.rs` (Rust routing stub) | Unproven perf win | Boltra Rust focus: SQL builder + row decode (Phases 19–21) |

---

### P4 — Rusjango roadmap items (already on Boltra plan)

Defer until P0–P2 complete. Rusjango Phase 4+ maps to Boltra batteries track.

| Rusjango (planned) | Boltra phase | Priority after ORM |
|--------------------|--------------|-------------------|
| `add docker` / `add tests` | Phase 28 (Docker + test scaffold) | Medium |
| Admin panel | Phases 22–24 | High (differentiator) |
| Auth (JWT, sessions) | Phases 25–26 | High |
| OpenAPI docs | **Free** with FastAPI | Already solved — Boltra advantage |
| Workers (Redis) | Phase 27 | Medium |
| AI/LLM module | Phase 28 | Low until core stable |
| Enterprise (audit, multi-tenancy) | Phase 32 | Low |

---

## Accelerated Execution Order

Recommended sequence for a solo maintainer (1–3 weeks per Boltra phase):

```text
DONE   Phases 0–3   CLI, new, dev
NEXT   Phase 4      settings + .env          ← Rusjango: config.py patterns
       Phase 5      add app                  ← Rusjango: add.rs + app templates
       Phase 6      remove app               ← Rusjango: remove.rs
       Phase 7      settings manager (AST)  ← Rusjango: settings.rs (rewrite)
       Phase 8      load_apps                ← Rusjango: apps.py (adapt)
       ─── PyPI release recommended here ───
       Phase 9      orm-spec                 ← Rusjango: docs + orm/*
       Phases 10–15 ORM core                ← Rusjango: test_orm.py as spec
       Phase 16     add/remove orm           ← Rusjango: orm.rs + templates
       Phase 17     migrate                  ← Rusjango: migrate command
       ─── Rusjango Phase 3 parity reached ───
       Phases 18–21 ORM hardening + Rust
       Phases 22+   admin, auth, batteries
```

**Estimated time to Rusjango parity:** ~14–20 weeks at 1 phase/week (ORM phases may take 2 weeks each).

---

## Rusjango File → Boltra Target Map

Quick reference when porting.

| Rusjango path | Boltra target | Action |
|---------------|---------------|--------|
| `cli/src/new.rs` | `crates/boltra-cli/` + `src/boltra/project/` | ✅ Done (Phase 2) |
| `cli/src/dev.rs` | `src/boltra/dev/` | ✅ Done (Phase 3) |
| `cli/src/add.rs` | `src/boltra/apps/add.py` (new) | Port in Phase 5 |
| `cli/src/remove.rs` | `src/boltra/apps/remove.py` (new) | Port in Phase 6 |
| `cli/src/settings.rs` | `src/boltra/project/settings_editor.py` (new) | Rewrite AST in Phase 7 |
| `cli/src/orm.rs` | `src/boltra/orm/cli.py` (new) | Port in Phases 16–17 |
| `cli/src/project.rs` | `src/boltra/project/generator.py` | Extend |
| `templates/project/` | `src/boltra/project/templates.py` | Extend |
| `templates/app/` | `src/boltra/apps/templates.py` (new) | Port in Phase 5 |
| `templates/orm/` | `src/boltra/orm/templates.py` (new) | Port in Phase 16 |
| `python/rusjango/.../apps.py` | `src/boltra/apps/loader.py` (new) | Adapt in Phase 8 |
| `python/rusjango/orm/*` | `src/boltra/orm/*` (new) | Rewrite Phases 10–15 |
| `examples/hello/` | `examples/hello/` (new) | Recreate after Phase 17 |
| `docs/03-cli-reference.md` | `doc/user/cli.md` | Merge command docs as features ship |
| `docs/05-orm-guide.md` | `doc/user/orm.md` (new) | Write after Phase 13 |

---

## Rusjango Archive Checklist

When Boltra reaches **P2 exit milestone** (Phase 17):

- [ ] Add archive notice to Rusjango README pointing to Boltra
- [ ] Pin final Rusjango PyPI version with deprecation note
- [ ] Copy `examples/hello/` concept to Boltra `examples/`
- [ ] Close open Rusjango issues with migration links
- [ ] Keep Rusjango repo read-only for reference (do not delete)

---

## Phase Cross-References

Each Boltra phase in [`phase.md`](phase.md) that benefits from Rusjango reference is tagged below.
When starting a phase, read the Rusjango files listed here first.

| Boltra phase | Rusjango reference files |
|--------------|-------------------------|
| 4 | `python/rusjango/src/rusjango/settings.py`, `config.py` |
| 5 | `cli/src/add.rs`, `templates/app/*` |
| 6 | `cli/src/remove.rs` |
| 7 | `cli/src/settings.rs` (rewrite approach) |
| 8 | `python/rusjango/src/rusjango/apps.py` |
| 9 | `docs/05-orm-guide.md`, `docs/internals/orm-internals.md` |
| 10–15 | `python/rusjango/src/rusjango/orm/*`, `tests/test_orm.py` |
| 16–17 | `cli/src/orm.rs`, `templates/orm/*` |

---

## Success Criteria

Migration is **complete** when:

1. Boltra demo project matches Rusjango `examples/hello/` capabilities (apps + ORM CRUD)
2. Generated projects use **FastAPI + Pydantic** — no Rusjango-style wrapper
3. Every Rusjango CLI command has a Boltra equivalent or documented replacement
4. Rusjango repo is archived with a clear pointer to Boltra
5. Boltra is published on PyPI with install docs

Until then: **no new features on Rusjango** — bug fixes only if PyPI users report issues.
