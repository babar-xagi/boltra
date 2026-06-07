"""File templates for generated Boltra projects."""

from __future__ import annotations


def display_title(name: str) -> str:
    """Build a human-readable API title from a project slug."""
    words = name.replace("_", " ").replace("-", " ")
    return f"{words.title()} API"


def main_py(name: str) -> str:
    """Return the generated ``main.py`` source."""
    title = display_title(name)
    return f'''from fastapi import FastAPI

app = FastAPI(
    title="{title}",
    version="0.1.0",
)


@app.get("/")
async def home():
    return {{"message": "Hello from FastAPI + Boltra Kit"}}
'''


def settings_py(name: str) -> str:
    """Return the generated ``settings.py`` source."""
    return f'''APP_NAME = "{name}"
DEBUG = True
SECRET_KEY = "change-this-secret-key"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = []

DATABASE = None

AUTH = {{
    "ENABLED": False,
}}

ADMIN = {{
    "ENABLED": False,
}}

AI = {{
    "ENABLED": False,
}}

WORKER = {{
    "ENABLED": False,
}}

PAYMENTS = {{
    "ENABLED": False,
}}

BOLTRA = {{
    "MODE": "fastapi-kit",
    "API_ENGINE": "fastapi",
    "NATIVE_MODULES": False,
}}
'''


def pyproject_toml(name: str) -> str:
    """Return the generated ``pyproject.toml`` source."""
    return f'''[project]
name = "{name}"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.27",
]

[tool.boltra]
mode = "fastapi-kit"
app = "main:app"
settings = "settings.py"
# Boltra CLI is used to scaffold and manage this project.
# Add `boltra` as a dependency when it is published or install from source:
#   uv add boltra --path ../path/to/boltra
'''
