# Python Package

The installable package lives under `src/boltra/`. Boltra uses a `src` layout and a maturin build backend so Python code and the PyO3 extension ship together.

## Package entry: `boltra.__init__`

```python
from boltra.native import is_available, native_version

__version__ = "0.4.0"
__all__ = ["__version__", "is_available", "native_version"]
```

| Symbol | Type | Description |
|--------|------|-------------|
| `__version__` | `str` | Python package version |
| `is_available()` | `() -> bool` | Whether Rust extension is active |
| `native_version()` | `() -> str | None` | Rust extension version or `None` |

## Native bridge: `boltra.native`

The bridge is the only public place Python code uses to check native availability.

1. Return `False` if `BOLTRA_DISABLE_NATIVE` is truthy.
2. On first call, try `import boltra._native`.
3. Cache the result so later checks are cheap.
4. On `ImportError`, log once at INFO and continue on the Python path.

## Type stubs: `boltra._native.pyi`

mypy cannot inspect the compiled extension. The `.pyi` stub documents the exposed native functions:

```python
def is_available() -> bool: ...
def version() -> str: ...
def parse_argv(args: list[str]) -> dict[str, object]: ...
def cli_help() -> str: ...
__version__: str
```

## CLI: `boltra.cli`

Boltra uses a hybrid CLI:

- Rust `clap` parses argv when `boltra._native` is available.
- Python `argparse` mirrors the parser as a fallback.
- Python dispatch executes commands such as `new` and `dev`.

| File | Role |
|------|------|
| `cli/main.py` | Console-script entry point |
| `cli/parser.py` | Native parser bridge plus argparse fallback |
| `cli/dispatch.py` | Routes parsed actions to Python handlers |

Console script:

```toml
[project.scripts]
boltra = "boltra.cli.main:run"
```

## Generated project settings

`boltra new` writes a direct FastAPI project. Its `settings.py` uses `pydantic-settings` when installed, reads `.env`, exposes a cached `settings` object, and keeps uppercase compatibility aliases such as `APP_NAME` and `DEBUG`.

## Dependencies

Boltra itself keeps runtime dependencies minimal. Generated projects declare their own app dependencies, currently `fastapi`, `pydantic-settings`, and `uvicorn[standard]`.

Dev-only tools are in `[dependency-groups] dev`: pytest, ruff, mypy, maturin, pre-commit, and FastAPI for generated-project import tests.

## Adding new modules

1. Create `src/boltra/<module>/` with `__init__.py`.
2. Add public APIs with type hints and docstrings.
3. Wire CLI subcommands in both Rust clap and Python fallback when user-facing.
4. Add tests under `tests/`.
5. Update user docs, developer docs, and the changelog.
