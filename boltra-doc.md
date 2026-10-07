# Boltra product direction

Boltra is a general-purpose Python API development kit. Its goal is a consistent
project-development workflow across frameworks, with readable scaffolding,
configuration, development commands, and optional tooling.

Applications should retain their chosen framework's normal APIs and conventions.
The direction covers FastAPI, Flask, Django-based APIs, Django Bolt, TurboAPI,
and future framework adapters. The toolkit is developed in Python first.

## Implemented foundation

Version 0.5.0 generates direct FastAPI applications with typed environment settings
and launches a reloadable Uvicorn development server. Other framework adapters
and selector dispatch are not implemented yet. Current behavior is documented
in the [README](README.md) and [user guides](doc/user/README.md).

Boltra's core is a development toolkit. It delegates routing, validation, and
serving to the selected framework/runtime rather than defining a replacement
HTTP framework. Today that delegation is specifically FastAPI and Uvicorn.

## Design principles

1. Keep the selected framework's ordinary imports and conventions visible.
2. Separate shared workflow from framework-specific templates and runtime adapters.
3. Keep starter projects small and add features when needed.
4. Implement correct Python behavior before optimization.
5. Make future feature installation/removal explicit and predictable.
6. Document compatibility per adapter and verify it with integration tests.
7. Ship examples that distinguish current capabilities from proposals.

## Framework-selection direction

A future framework selector should choose appropriate templates, dependencies,
settings conventions, and development commands. A FastAPI project should use the
FastAPI adapter; a Flask project should use the Flask adapter; Django-based and
custom-runtime projects should use their corresponding adapters.

The current `mode` field is a descriptive label. Changing it does not switch
frameworks. The [adapter design](doc/developer/framework-adapters.md) records the
proposed contract, runtime differences, and checks needed before additional modes
can be called supported.

## Future features

After defining the adapter boundary, extend shared project tooling and implement
modular application management. ORM, admin, authentication, workers, Docker/test
scaffolding, thin AI integration, security, and observability remain roadmap work.
Framework capabilities differ: Django integrations should respect Django's existing
settings, ORM, admin, and application conventions.

See the [execution roadmap](doc/plan/phase.md) for current milestones. Optional
optimizations must preserve Python functionality and be justified by benchmarks.
Payments, GraphQL, multi-tenancy, and a full agent framework remain future proposals.
