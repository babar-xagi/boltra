# Python Package

The installable package lives under `src/boltra/`. Boltra uses a **src layout** (recommended by PyPA).

## Package entry: `boltra.__init__`

```python
from boltra.native import is_available, native_version

__version__ = "0.1.0"
__all__ = ["__version__", "is_available", "native_version"]
```

Public symbols:

| Symbol | Type | Description |
|--------|------|-------------|
| `__version__` | `str` | Python package version |
| `is_available()` | `() -> bool` | Whether Rust extension is active |
| `native_version()` | `() -> str \| None` | Rust extension version or `None` |

## Native bridge: `boltra.native`

**File:** `src/boltra/native.py`
**Phase:** 0

### `is_available() -> bool`

1. Return `False` if `BOLTRA_DISABLE_NATIVE` is truthy
2. On first call, try `import boltra._native`
3. Cache result; subsequent calls are cheap
4. On `ImportError`, log INFO and return `False`

### `native_version() -> str | None`

Returns `_native.version()` when available, else `None`.

### Environment variable

```text
BOLTRA_DISABLE_NATIVE=1|true|yes|on
```

Used in tests (`tests/test_native.py`) and CI to verify the Python fallback path.

## Type stubs: `boltra._native.pyi`

**File:** `src/boltra/_native.pyi`
**Phase:** 0

mypy cannot inspect the compiled extension. The `.pyi` stub documents:

```python
def is_available() -> bool: ...
def version() -> str: ...
__version__: str
```

## CLI: `boltra.cli`

**Files:** `src/boltra/cli/__init__.py`, `src/boltra/cli/main.py`
**Phase:** 1

### Typer application

```python
app = typer.Typer(
    name="boltra",
    help="Boltra — Django-like productivity for FastAPI projects.",
    no_args_is_help=True,
    add_completion=False,
)
```

### Console script

Registered in `pyproject.toml`:

```toml
[project.scripts]
boltra = "boltra.cli.main:run"
```

`run()` invokes `app()` — this is what executes when you type `boltra` in the shell.

### Version flag

`--version` / `-V` uses Typer's eager callback pattern so it exits before any subcommand runs.

## Dependencies

Runtime (from `pyproject.toml`):

```toml
dependencies = [
    "typer>=0.15",
]
```

Dev-only tools are in `[dependency-groups] dev` (pytest, ruff, mypy, maturin, pre-commit).

## Adding new modules (guidelines)

1. Create `src/boltra/<module>/` with `__init__.py`
2. Add public APIs with type hints and docstrings
3. Wire CLI subcommands in `boltra.cli` — keep CLI thin
4. Add tests under `tests/`
5. Document in `doc/user/` and `doc/developer/`
6. Entry in `doc/plan/CHANGELOG.md`
