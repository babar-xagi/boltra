# Installation

## Requirements

| Tool | Minimum version | Purpose |
|------|-----------------|---------|
| Python | 3.12+ | Runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Package manager (recommended) |
| Rust | 1.85+ | Builds the PyO3 native extension |

> **Note:** Boltra uses **maturin** to compile a Rust extension (`boltra._native`) during install. Rust is required for a full install with native acceleration.

## Install from source (development)

```bash
git clone <your-repo-url>
cd boltra
uv sync --group dev
```

This will:

1. Create a `.venv` virtual environment
2. Install Python dependencies (including `typer` for the CLI)
3. Build the PyO3 extension via maturin

## Verify installation

```bash
# CLI
uv run boltra --help
uv run boltra --version

# Native extension (optional — should print True and a version)
uv run python -c "import boltra; print(boltra.is_available(), boltra.native_version())"
```

Expected output:

```text
$ uv run boltra --version
0.1.0

$ uv run python -c "import boltra; print(boltra.is_available(), boltra.native_version())"
True 0.1.0
```

## Install the CLI globally (optional)

After `uv sync`, the `boltra` command is available inside the project venv:

```bash
# Windows
.venv\Scripts\boltra --help

# macOS / Linux
.venv/bin/boltra --help
```

To use `boltra` outside the project, activate the venv first or install the package into your environment with `uv pip install .`.

## Python 3.14

If you use Python 3.14, the build uses ABI forward compatibility (`PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1`) because PyO3 may not officially list 3.14 yet. This is configured automatically in `.cargo/config.toml`.

## Generated projects (`boltra new`)

A new project only depends on **FastAPI** and **uvicorn** — not `boltra` itself.
That keeps `uv sync` working before Boltra is published to PyPI.

```bash
cd hello
uv sync
boltra dev
```

If you see a `VIRTUAL_ENV does not match` warning, another venv is still active.
Run `deactivate` (or open a fresh terminal) before `uv sync` in the new project.

To link a local Boltra checkout later:

```bash
uv add boltra --path ../path/to/boltra
```

## Without native extension

If Rust is not installed or the extension fails to build, you can still use the Python package. Set:

```bash
# Windows PowerShell
$env:BOLTRA_DISABLE_NATIVE="1"

# macOS / Linux
export BOLTRA_DISABLE_NATIVE=1
```

Boltra will use pure-Python fallbacks. Native acceleration for ORM hot paths is added in later phases.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `boltra: command not found` | Run via `uv run boltra` or activate `.venv` |
| PyO3 build fails on 3.14 | Ensure `.cargo/config.toml` exists; set `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` |
| Slow rebuild after Rust edits | Run `uv run maturin develop --uv` for incremental dev builds |
