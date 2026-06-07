# User Documentation

Guides for installing and using Boltra as an end user.

## Contents

| Guide | Description |
|-------|-------------|
| [Installation](installation.md) | Requirements, install with uv, verify setup |
| [CLI Reference](cli.md) | Commands, flags, and examples |

## What Boltra does today

Boltra is in early development. Currently available:

- **`boltra --help`** / **`boltra --version`** — CLI usage and version
- **`boltra new <name>`** — create a minimal FastAPI project
- **`boltra dev`** — run uvicorn with reload (reads `[tool.boltra]`)
- **Rust clap + Python** — clap parses argv in Rust; Python runs command logic
- **Rust native extension** — PyO3 bridge (ORM acceleration comes later)

Coming soon (see [roadmap](../plan/phase.md)):

```bash
boltra add app X    # Phase 5+ — apps, ORM, admin, …
```

## Getting help

- [Project vision](../../boltra-doc.md) — what Boltra aims to be
- [Changelog](../plan/CHANGELOG.md) — what has shipped
- [Contributing](../../CONTRIBUTING.md) — report issues or contribute
