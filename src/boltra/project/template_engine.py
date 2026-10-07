"""Render readable template assets packaged alongside the Python code."""

from __future__ import annotations

from importlib.resources import files
from string import Template


def display_title(name: str) -> str:
    """Convert a project slug such as ``school_api`` into ``School Api API``."""
    words = name.replace("_", " ").replace("-", " ")
    return f"{words.title()} API"


def _render(filename: str, name: str) -> str:
    # Package resources work in installed wheels as well as editable checkouts.
    source = (
        files("boltra.project")
        .joinpath("templates", filename)
        .read_text(encoding="utf-8")
    )
    # Only explicit placeholders are replaced; Python braces remain normal code.
    return Template(source).substitute(project_name=name, api_title=display_title(name))


def main_py(name: str) -> str:
    """Render the direct FastAPI application template."""
    return _render("main.py.tmpl", name)


def settings_py(name: str) -> str:
    """Render typed application settings and the first-import fallback."""
    return _render("settings.py.tmpl", name)


def env_example(name: str) -> str:
    """Render the environment example distributed with each project."""
    return _render("env.example.tmpl", name)


def pyproject_toml(name: str) -> str:
    """Render app dependencies and Boltra development-server metadata."""
    return _render("pyproject.toml.tmpl", name)
