# Rust Native Layer

Boltra uses **PyO3** and **maturin** to ship a native Python extension for performance-critical code.

## Crate: `boltra-core`

**Path:** `crates/boltra-core/`
**Python module name:** `boltra._native`
**Phase:** 0 (stub); ORM hot paths added in Phases 19–21

### `Cargo.toml` highlights

```toml
[lib]
name = "boltra_native"
crate-type = ["cdylib"]

[dependencies]
pyo3.workspace = true
```

`cdylib` produces a shared library that Python loads as an extension module.

### `lib.rs` — PyO3 module

```rust
#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_available, m)?)?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
```

Exported to Python:

| Function | Returns | Purpose |
|----------|---------|---------|
| `is_available()` | `bool` | Always `true` when extension is loaded |
| `version()` | `str` | Crate version from `Cargo.toml` |

Future phases will add SQL compilation, row decoding, etc. here.

## Workspace: root `Cargo.toml`

```toml
[workspace]
members = ["crates/boltra-core"]

[workspace.dependencies]
pyo3 = { version = "0.28", features = ["extension-module"] }

[profile.release]
lto = "fat"
codegen-units = 1
strip = "symbols"

[profile.dev]
opt-level = 1
```

- **`extension-module`** — correct linking when loaded by CPython
- **Release LTO** — maximize runtime speed for hot paths
- **dev opt-level 1** — faster dev builds with some optimization

## maturin configuration

In `pyproject.toml`:

```toml
[build-system]
requires = ["maturin>=1.8,<2"]
build-backend = "maturin"

[tool.maturin]
manifest-path = "crates/boltra-core/Cargo.toml"
module-name = "boltra._native"
python-source = "src"
features = ["pyo3/extension-module"]
```

- **`python-source = "src"`** — bundles pure Python (`boltra` package) with the Rust extension in one wheel
- **`module-name`** — must match `#[pymodule] fn _native` in `lib.rs`

## Python 3.14 compatibility

PyO3 may not officially support the newest Python yet. `.cargo/config.toml` sets:

```toml
[env]
PYO3_USE_ABI3_FORWARD_COMPATIBILITY = "1"
```

CI sets the same env var when running `uv sync`.

## Development workflow

```bash
# Full reinstall (after pyproject or dependency changes)
uv sync --group dev

# Fast iterative rebuild after editing .rs files
uv run maturin develop --uv

# Rust unit tests only
cargo test --workspace
```

## Fallback contract

Every feature that calls into `_native` **must**:

1. Check `boltra.native.is_available()` first
2. Implement a pure-Python path when native is off
3. Have tests for both paths (`BOLTRA_DISABLE_NATIVE=1`)

## Planned Rust modules (roadmap)

| Phase | Module | Responsibility |
|-------|--------|----------------|
| 19 | PyO3 bridge | CI wheels, `is_available()` (mostly done) |
| 20 | SQL query builder | `filter`, `order_by`, `limit` compilation |
| 21 | Row decoder | Fast row → dict/model decoding |

Benchmark baselines go under `benchmarks/results/` before Rust ships.
