# Repository structure

Source is grouped by responsibility. Environments, caches, and build outputs are
ignored local artifacts.

```text
boltra/
├── .github/workflows/
│   ├── ci.yml                    # Python quality/test matrix
│   └── publish.yml               # Python build and publication
├── .pre-commit-config.yaml       # Lint, types, file hygiene
├── benchmarks/README.md          # Future Python benchmark conventions
├── doc/
│   ├── README.md                 # Documentation index
│   ├── user/                     # Installation, quickstart, CLI, settings
│   ├── developer/                # Architecture, files, workflow, tests, release
│   └── plan/                     # Roadmap, changelog, migration ideas
├── src/boltra/
│   ├── __init__.py               # Package version
│   ├── __main__.py               # python -m boltra
│   ├── py.typed                  # Published typing marker
│   ├── cli/
│   │   ├── __init__.py            # Public CLI exports
│   │   ├── cli.py                # Entry point and command handlers
│   │   └── parser.py             # argparse and ParsedCommand
│   ├── apps/
│   │   ├── __init__.py            # add_app / AppError exports
│   │   ├── generator.py          # Scaffold, registration, and rollback
│   │   ├── registration.py       # AST-located source edits
│   │   ├── validation.py         # Import-safe package name rules
│   │   └── templates/router.py.tmpl # APIRouter starter resource
│   ├── project/
│   │   ├── __init__.py            # Public generator exports
│   │   ├── generator.py          # Creation and partial-write cleanup
│   │   ├── validation.py         # Shared name rules
│   │   ├── template_engine.py    # Resource loading/substitution
│   │   └── templates/
│   │       ├── main.py.tmpl       # Direct FastAPI app
│   │       ├── settings.py.tmpl   # Settings/environment support
│   │       ├── pyproject.toml.tmpl # App dependencies/server metadata
│   │       └── env.example.tmpl   # Environment example
│   └── dev/
│       ├── __init__.py            # Public config/server exports
│       ├── config.py             # TOML and project discovery
│       ├── server.py             # Environment selection/Uvicorn launch
│       └── windows.py            # Windows reload bootstrap
├── tests/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── test_cli.py
│   ├── apps/
│   │   ├── __init__.py
│   │   └── test_apps.py           # Registration and filesystem contracts
│   ├── project/
│   │   ├── __init__.py
│   │   ├── test_generator.py
│   │   └── test_settings.py
│   ├── dev/
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_server.py
│   │   └── test_integration.py
│   └── test_package.py
├── .gitattributes                 # Consistent text line endings
├── .gitignore
├── boltra-doc.md                  # Product direction
├── CONTRIBUTING.md               # Contributor and commit conventions
├── LICENSE                       # MIT
├── pyproject.toml                 # Metadata/build/tooling
├── README.md                      # Overview and quickstart
└── uv.lock                       # Locked Python dependencies
```

`__init__.py` files make module/test boundaries explicit. Future command-specific
logic can move into additional `cli/` modules when complexity warrants it; the
current commands are easy to follow in `cli.py`.

## Local artifacts

| Directory | Purpose |
|-----------|---------|
| `.venv/` | Editable contributor environment |
| `.uv/` | Download/test caches and isolated verification environments |
| `dist/`, `build/` | Distribution/build output |
| `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | Tool caches |
| `__pycache__/` | Python bytecode |

These directories do not belong in commits or source archives. The
[file reference](file-reference.md) explains each maintained file in detail.
