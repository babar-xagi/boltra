//! Clap-based CLI parser for Boltra.
//!
//! Parses argv in Rust for speed and consistency; Python executes command logic.

use clap::{CommandFactory, Parser, Subcommand};
use std::ffi::OsString;

/// Top-level Boltra CLI definition (mirrored by the Python fallback parser).
#[derive(Debug, Parser, Clone, PartialEq, Eq)]
#[command(
    name = "boltra",
    about = "Boltra — Django-like productivity for FastAPI projects.",
    version,
    arg_required_else_help = true
)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Option<Commands>,
}

/// Supported subcommands. Extended in later phases (`add`, …).
#[derive(Debug, Subcommand, Clone, PartialEq, Eq)]
pub enum Commands {
    /// Create a new FastAPI project.
    New {
        /// Project name (letters, digits, hyphens, underscores).
        #[arg(value_name = "NAME", value_parser = validate_project_name)]
        name: String,
    },
    /// Run the development server with auto-reload.
    Dev,
}

/// Parsed CLI action returned to Python for dispatch.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CliAction {
    Help { text: String },
    Version,
    New { name: String },
    Dev,
    Error { message: String, exit_code: i32 },
}

/// Validate a project name: ASCII letter first, then letters/digits/`_`/`-`.
pub fn validate_project_name(name: &str) -> Result<String, String> {
    if name.is_empty() {
        return Err("project name cannot be empty".to_string());
    }
    if name.contains(['/', '\\', '.']) {
        return Err(format!(
            "project name '{name}' must not contain path separators or dots"
        ));
    }
    let mut chars = name.chars();
    let first = chars.next().unwrap();
    if !first.is_ascii_alphabetic() {
        return Err(format!(
            "project name '{name}' must start with an ASCII letter"
        ));
    }
    if !chars.all(|c| c.is_ascii_alphanumeric() || c == '_' || c == '-') {
        return Err(format!(
            "project name '{name}' may only contain letters, digits, hyphens, and underscores"
        ));
    }
    Ok(name.to_string())
}

/// Parse CLI arguments. Pass argv **without** the program name.
pub fn parse_args(args: &[String]) -> CliAction {
    let argv: Vec<OsString> = std::iter::once(OsString::from("boltra"))
        .chain(args.iter().map(OsString::from))
        .collect();

    match Cli::try_parse_from(&argv) {
        Ok(cli) => match cli.command {
            Some(Commands::New { name }) => CliAction::New { name },
            Some(Commands::Dev) => CliAction::Dev,
            None => CliAction::Help {
                text: Cli::command().render_help().to_string(),
            },
        },
        Err(err) => {
            if err.kind() == clap::error::ErrorKind::DisplayVersion {
                return CliAction::Version;
            }
            if err.kind() == clap::error::ErrorKind::DisplayHelp
                || err.kind() == clap::error::ErrorKind::DisplayHelpOnMissingArgumentOrSubcommand
            {
                return CliAction::Help {
                    text: err.to_string(),
                };
            }
            CliAction::Error {
                message: err.to_string(),
                exit_code: err.exit_code(),
            }
        }
    }
}

/// Full help text for the CLI (used by Python fallback).
pub fn help_text() -> String {
    Cli::command().render_help().to_string()
}

#[cfg(test)]
mod tests {
    use super::{parse_args, CliAction, validate_project_name};

    #[test]
    fn validate_accepts_hello() {
        assert_eq!(validate_project_name("hello").unwrap(), "hello");
    }

    #[test]
    fn validate_rejects_empty() {
        assert!(validate_project_name("").is_err());
    }

    #[test]
    fn validate_rejects_starts_with_digit() {
        assert!(validate_project_name("1app").is_err());
    }

    #[test]
    fn parse_version_flag() {
        assert_eq!(parse_args(&["--version".to_string()]), CliAction::Version);
    }

    #[test]
    fn parse_new_command() {
        assert_eq!(
            parse_args(&["new".to_string(), "myapp".to_string()]),
            CliAction::New {
                name: "myapp".to_string()
            }
        );
    }

    #[test]
    fn parse_dev_command() {
        assert_eq!(parse_args(&["dev".to_string()]), CliAction::Dev);
    }

    #[test]
    fn parse_invalid_name_returns_error() {
        match parse_args(&["new".to_string(), "1bad".to_string()]) {
            CliAction::Error { .. } => {}
            other => panic!("expected error, got {other:?}"),
        }
    }
}
