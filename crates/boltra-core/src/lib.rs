//! Boltra native extension — PyO3 bridge for CLI (clap) and future ORM hot paths.

use boltra_cli::{help_text, parse_args, CliAction};
use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Return whether the native Rust extension is loaded and active.
#[pyfunction]
fn is_available() -> bool {
    true
}

/// Native extension version (matches the Cargo package version).
#[pyfunction]
fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

/// Parse CLI argv using Rust clap. Pass args **without** the program name.
///
/// Returns a dict with ``action`` in ``help``, ``version``, ``new``, ``dev``, or ``error``.
#[pyfunction]
fn parse_argv(args: Vec<String>) -> PyResult<Py<PyAny>> {
    Python::attach(|py| cli_action_to_dict(py, parse_args(&args)))
}

/// Return full CLI help text rendered by clap.
#[pyfunction]
fn cli_help() -> String {
    help_text()
}

fn cli_action_to_dict(py: Python<'_>, action: CliAction) -> PyResult<Py<PyAny>> {
    let dict = PyDict::new(py);
    match action {
        CliAction::Help { text } => {
            dict.set_item("action", "help")?;
            dict.set_item("help_text", text)?;
        }
        CliAction::Version => {
            dict.set_item("action", "version")?;
        }
        CliAction::New { name } => {
            dict.set_item("action", "new")?;
            dict.set_item("name", name)?;
        }
        CliAction::Dev => {
            dict.set_item("action", "dev")?;
        }
        CliAction::Error { message, exit_code } => {
            dict.set_item("action", "error")?;
            dict.set_item("error_message", message)?;
            dict.set_item("exit_code", exit_code)?;
        }
    }
    Ok(dict.into())
}

/// Python module: `boltra._native`
#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_available, m)?)?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(parse_argv, m)?)?;
    m.add_function(wrap_pyfunction!(cli_help, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::version;

    #[test]
    fn version_is_non_empty() {
        assert!(!version().is_empty());
    }
}
