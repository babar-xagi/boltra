# Development workflow

## Set up

Install Python 3.12+ and uv, then run from the checkout:

```bash
uv sync --locked --group dev
uv run pre-commit install
uv run boltra --help
uv run pytest
```

uv creates an editable `.venv` using Hatchling. Python source changes are
available immediately; there is no extension rebuild.

## Daily loop

```bash
git switch -c codex/my-feature
uv run pytest -m "not integration and not packaging"
uv run ruff check .
uv run ruff format .
uv run mypy src
```

Before committing:

```bash
uv run pytest
uv run ruff format --check .
uv run pre-commit run --all-files
uv build
```

Use the [file reference](file-reference.md) to locate domain logic and the
[testing guide](testing.md) for targeted checks.

## CLI changes

Add arguments in `cli/parser.py` and routing/output in `cli/cli.py`. Expose real
behavior through domain functions rather than filesystem/database code in the
parser. Test status, terminal output, and the resulting operation.

## Generated-code changes

Edit `project/templates/` assets. `template_engine.py` substitutes placeholders;
`generator.py` handles destination creation/cleanup. Run project/settings and
packaging tests because assets must work from installed wheels too.

For manual scaffolding into an existing parent directory:

```bash
uv run python -c "from pathlib import Path; from boltra.project import create_project; create_project('demo', cwd=Path('/tmp'))"
```

On Windows, use a path such as `Path('D:/sandbox')` for an existing parent.
For the complete app workflow, install a separate tool with `uv tool install .`
and follow the [quickstart](../user/quickstart.md).

## Dependencies

Edit `pyproject.toml` and run:

```bash
uv lock
uv sync --group dev
```

Commit the manifest/lock together. The CLI currently has no declared runtime
dependencies; generated apps declare their dependencies in the template.

## Documentation

| Change | Update |
|--------|--------|
| Command, flag, error | User CLI guide and README |
| Generated settings | User settings guide and file reference |
| Module/file layout | File reference and directory map |
| Runtime architecture | Architecture and user behavior |
| Notable change | Changelog |
| Verification run | Verification report |

## Commits

Use one relevant emoji with a conventional type:

```text
🐍 refactor: simplify Python project validation
📚 docs: explain every generator template
🧪 test: verify wheel installation without app dependencies
```

Explain the result and meaningful validation in the body. For incompatible APIs,
use `!` and a `BREAKING CHANGE:` footer. See [CONTRIBUTING.md](../../CONTRIBUTING.md).
