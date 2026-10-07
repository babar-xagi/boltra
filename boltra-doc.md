# Boltra product direction

Boltra is a development toolkit specifically for FastAPI: small starting
projects, clear settings, and a CLI that remains useful as applications grow.
The implementation strategy is **Python first**, with correctness, readable code,
and tests before optimization.

## What exists

The current toolkit creates an ordinary FastAPI app with typed environment
settings and launches a reloadable development server. It also creates modular
app packages and explicitly registers their routers. The complete shipped
behavior is documented in the [README](README.md) and [user guides](doc/user/README.md).

Boltra is a development toolkit. It does not implement its own HTTP routing,
validation framework, or ASGI server. FastAPI and Uvicorn provide those parts.

## Design principles

1. Keep `from fastapi import FastAPI` visible in generated applications.
2. Start with four understandable project files; add structure when needed.
3. Build features in Python before considering performance optimization.
4. Keep CLI, generation, settings, and server responsibilities separate.
5. Make future feature installation/removal explicit and predictable.
6. Measure performance instead of promising unverified speedups.
7. Ship tests and examples with public behavior.

## Future direction

With modular app creation implemented, complete safe removal, structured settings
editing, and router discovery. Then implement a Python async ORM in vertical slices:
connections, model metadata, table creation, CRUD, filters, transactions, and
migrations. Admin and authentication should build on a tested foundation.

Workers, Docker/test scaffolding, thin AI integration, security defaults, and
observability follow the core workflow. These are roadmap items, not current APIs.

See the [execution roadmap](doc/plan/phase.md) for milestones and exit criteria.

## Boundaries

There is no project-owned native extension, compiler requirement, or alternate
native API engine in the current implementation. A future optimization proposal
must preserve the Python behavior, include a benchmark, and be evaluated after
the corresponding Python feature is stable. It is not a dependency of the v1 plan.

Payments, GraphQL, multi-tenancy, and a full agent framework remain separate future
proposals. The immediate goal is a reliable, well-documented FastAPI development kit.
