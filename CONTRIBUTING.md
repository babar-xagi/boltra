# Contributing to Boltra

Boltra is developed in Python first. Keep generated projects readable, implement
one roadmap milestone at a time, and preserve direct FastAPI usage.

## Set up

Install Python 3.12+ and uv, then run:

```bash
git clone https://github.com/babar-xagi/boltra.git
cd boltra
uv sync --locked --group dev
uv run pre-commit install
```

Read the [architecture](doc/developer/architecture.md),
[file reference](doc/developer/file-reference.md), and [roadmap](doc/plan/phase.md)
before adding a feature. Start CLI work in `src/boltra/cli/cli.py`; project logic
belongs in `project/`, and server logic belongs in `dev/`.

## Required checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run pre-commit run --all-files
uv build
```

The suite includes real HTTP/reload checks and clean-environment wheel checks.
Use `uv run pytest -m "not integration and not packaging"` for a quick local
loop, but run the complete suite before committing.

## Code and documentation

- Type public APIs and write docstrings explaining their contract.
- Comment design choices, environment handling, and error recovery; avoid
  comments that merely restate a line of code.
- Keep terminal output in `cli/cli.py` and return domain errors from other modules.
- Keep generated source in `project/templates/`; update tests when changing it.
- Add behavioral regression tests for fixes and meaningful tests for new behavior.
- Update user docs when commands or settings change, the file reference when
  structure changes, and `doc/plan/CHANGELOG.md` for notable work.
- Identify planned features explicitly; do not describe a future command as shipped.

## Branches and commits

Use a focused branch such as `codex/python-cli-cleanup`. Keep commits concise and
use one relevant emoji with a conventional commit type:

```text
🐍 refactor: simplify Python command routing
🐛 fix: preserve project-name validation errors
📚 docs: explain generated application settings
🧪 test: verify wheel templates in a clean environment
```

Use `!` and a `BREAKING CHANGE:` footer for incompatible public API changes.
Commit bodies should explain the result and meaningful validation. Do not include
secrets, environments, caches, or generated build artifacts.

## Pull requests

Describe the concrete behavior before and after the change, relevant tests, and
any compatibility limits. Keep a PR scoped to a coherent feature or milestone.
