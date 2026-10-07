# Installation

## Requirements

- Python **3.12 or newer**; local verification covers 3.12, 3.13, and 3.14.
- uv is recommended for tool installation and generated-project dependencies.

Boltra's own distribution is a pure Python `py3-none-any` wheel. It does not build
an extension or require a compiler. Generated applications install their own
FastAPI, Pydantic settings, and Uvicorn dependencies.

## Install this checkout as a CLI tool

```bash
git clone https://github.com/babar-xagi/boltra.git
cd boltra
uv tool install .
boltra --version
boltra --help
```

The source version prints `0.5.0`. A tool installation has its own environment,
so switching into a generated app does not make the Boltra command disappear.
The source changes here must be published before a registry install can select
this version; the commands above install the checkout directly.

After changing local source, rebuild the installed tool with:

```bash
uv tool install --reinstall .
```

## Install using Python's package installer

Inside your chosen Python environment, from the checkout:

```bash
python -m pip install .
python -m boltra --help
```

Use `python -m boltra` when the console-script directory is not on your PATH.

## Contributor installation

```bash
uv sync --locked --group dev
uv run boltra --version
uv run pytest
```

This creates an editable `.venv` for working on Boltra. For creating and running
apps in another directory, the separate tool installation is convenient. See the
[development workflow](../developer/development-workflow.md) for details.

## Install a built wheel

```bash
uv build
python -m pip install dist/boltra-0.5.0-py3-none-any.whl
```

The same wheel serves all supported operating systems and Python versions.

## Troubleshooting

| Symptom | Action |
|---------|--------|
| `boltra` command unavailable | Check the tool installation/PATH, or use `python -m boltra` in the installed environment |
| Unsupported Python | Select Python 3.12+; `uv python install 3.12` installs a suitable interpreter |
| Project has no dependencies installed | Run `uv sync` in the generated project |
| Another venv is active | Deactivate it or use a fresh terminal before syncing the app |
| Port already in use | Change `[tool.boltra].port` and restart the dev command |
| Default secret warning | Set `SECRET_KEY` in the generated `.env` |

For the complete application workflow, continue to the [quickstart](quickstart.md).
