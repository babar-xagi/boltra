# CLI Architecture — Rust clap + Python

Boltra uses a **hybrid CLI**: Rust **clap** parses arguments; Python **executes** command logic.

## Flow

```text
sys.argv
    │
    ▼
boltra.cli.main.run()
    │
    ▼
boltra.cli.dispatch.execute(argv)
    │
    ▼
boltra.cli.parser.parse_argv(argv)
    │
    ├─ native available ──► boltra._native.parse_argv()  [Rust clap]
    │
    └─ fallback ──────────► argparse parser             [Python]
    │
    ▼
ParsedCommand { action, name, ... }
    │
    ▼
dispatch → Python handler (e.g. project.generator.create_project)
```

## Rust layer: `crates/boltra-cli`

| File | Role |
|------|------|
| `src/lib.rs` | `Cli` / `Commands` clap structs, `parse_args()`, name validation |

Clap defines:

- `--help` / `-h`
- `--version` / `-V`
- `boltra new <NAME>` with `validate_project_name`

Exposed to Python via PyO3 in `boltra-core`:

```python
import boltra._native as _native
result = _native.parse_argv(["new", "hello"])
# {"action": "new", "name": "hello"}
```

## Python layer: `src/boltra/cli/`

| File | Role |
|------|------|
| `parser.py` | `parse_argv()` — native or argparse fallback; `ParsedCommand` dataclass |
| `dispatch.py` | `execute()` — routes actions to handlers; prints help/version/errors |
| `main.py` | `run()` — console script entry point |

## Command handlers: `src/boltra/project/`

| File | Role |
|------|------|
| `generator.py` | `create_project()` — writes files, checks collisions |
| `templates.py` | `main.py`, `settings.py`, `.env.example`, `pyproject.toml` templates |

`boltra.dev` handles `boltra dev`; Phase 5+ adds more subcommands in **both** clap and Python dispatch.

## Adding a new subcommand

1. Add variant to `Commands` enum in `crates/boltra-cli/src/lib.rs`
2. Map it in `parse_args()` → `CliAction`
3. Expose via existing `parse_argv` PyO3 function (dict keys)
4. Add handler in `boltra/cli/dispatch.py`
5. Mirror parsing in `parse_argv_python()` for fallback
6. Add tests in `tests/test_cli.py` and integration tests as needed
7. Update `doc/user/cli.md` and changelog

## Why clap + Python?

| Layer | Responsibility |
|-------|----------------|
| **clap (Rust)** | Fast, consistent argv parsing; shared validation rules |
| **Python** | File I/O, templates, FastAPI project logic, future ORM/admin |

This matches the project rule: **Rust where it wins**, Python for productivity and always-available fallback.
