"""File templates for generated Boltra projects."""

from __future__ import annotations


def display_title(name: str) -> str:
    """Build a human-readable API title from a project slug."""
    words = name.replace("_", " ").replace("-", " ")
    return f"{words.title()} API"


def main_py(name: str) -> str:
    """Return the generated main.py source."""
    return """from fastapi import FastAPI

from settings import settings

app = FastAPI(
    title=settings.api_title,
    version="0.1.0",
    debug=settings.debug,
)


@app.get("/")
async def home():
    return {"message": "Hello from FastAPI + Boltra Kit"}
"""


def settings_py(name: str) -> str:
    """Return the generated settings.py source."""
    title = display_title(name)
    return f'''"""Application settings for this Boltra project."""

from __future__ import annotations

from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Any
import warnings

try:
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    _HAS_PYDANTIC_SETTINGS = False

    class BaseSettings:
        """Fallback so the project can still import before uv sync."""

    def Field(
        default: Any = None,
        *,
        default_factory: Any | None = None,
    ) -> Any:
        return default_factory() if default_factory is not None else default

    def SettingsConfigDict(**kwargs: Any) -> dict[str, Any]:
        return kwargs
else:
    _HAS_PYDANTIC_SETTINGS = True


_ENV_FILE = Path(__file__).with_name(".env")
_DEFAULT_SECRET_KEY = "change-this-secret-key"
_DEFAULT_ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


def _read_env_file(path: Path) -> dict[str, str]:
    """Read simple KEY=VALUE pairs from .env for the import fallback."""
    if not path.is_file():
        return {{}}

    values: dict[str, str] = {{}}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _raw_value(env: dict[str, str], key: str, default: Any) -> Any:
    return os.environ.get(key, env.get(key, default))


def _bool_value(env: dict[str, str], key: str, default: bool) -> bool:
    raw = _raw_value(env, key, default)
    if isinstance(raw, bool):
        return raw
    return str(raw).lower() in {{"1", "true", "yes", "on"}}


def _list_value(env: dict[str, str], key: str, default: list[str]) -> list[str]:
    raw = _raw_value(env, key, default)
    if isinstance(raw, list):
        return list(raw)
    if not raw:
        return list(default)
    try:
        parsed = json.loads(str(raw))
    except json.JSONDecodeError:
        return [item.strip() for item in str(raw).split(",") if item.strip()]
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    return list(default)


def _optional_value(env: dict[str, str], key: str) -> str | None:
    raw = _raw_value(env, key, None)
    return str(raw) if raw else None


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "{name}"
    api_title: str = "{title}"
    debug: bool = True
    secret_key: str = _DEFAULT_SECRET_KEY
    allowed_hosts: list[str] = Field(
        default_factory=lambda: list(_DEFAULT_ALLOWED_HOSTS)
    )
    installed_apps: list[str] = Field(default_factory=list)
    database_url: str | None = None
    auth_enabled: bool = False
    admin_enabled: bool = False
    ai_enabled: bool = False
    worker_enabled: bool = False
    payments_enabled: bool = False
    boltra_mode: str = "fastapi-kit"
    api_engine: str = "fastapi"
    native_modules: bool = False

    def __init__(self, **values: Any) -> None:
        if _HAS_PYDANTIC_SETTINGS:
            super().__init__(**values)
            return

        env = _read_env_file(_ENV_FILE)
        self.app_name = str(
            values.get("app_name", _raw_value(env, "APP_NAME", self.app_name))
        )
        self.api_title = str(
            values.get("api_title", _raw_value(env, "API_TITLE", self.api_title))
        )
        self.debug = bool(values.get("debug", _bool_value(env, "DEBUG", self.debug)))
        self.secret_key = str(
            values.get("secret_key", _raw_value(env, "SECRET_KEY", self.secret_key))
        )
        self.allowed_hosts = _list_value(env, "ALLOWED_HOSTS", self.allowed_hosts)
        self.installed_apps = _list_value(env, "INSTALLED_APPS", self.installed_apps)
        self.database_url = values.get(
            "database_url",
            _optional_value(env, "DATABASE_URL"),
        )
        self.auth_enabled = bool(
            values.get(
                "auth_enabled",
                _bool_value(env, "AUTH_ENABLED", self.auth_enabled),
            )
        )
        self.admin_enabled = bool(
            values.get(
                "admin_enabled",
                _bool_value(env, "ADMIN_ENABLED", self.admin_enabled),
            )
        )
        self.ai_enabled = bool(
            values.get("ai_enabled", _bool_value(env, "AI_ENABLED", self.ai_enabled))
        )
        self.worker_enabled = bool(
            values.get(
                "worker_enabled",
                _bool_value(env, "WORKER_ENABLED", self.worker_enabled),
            )
        )
        self.payments_enabled = bool(
            values.get(
                "payments_enabled",
                _bool_value(env, "PAYMENTS_ENABLED", self.payments_enabled),
            )
        )
        self.boltra_mode = str(
            values.get("boltra_mode", _raw_value(env, "BOLTRA_MODE", self.boltra_mode))
        )
        self.api_engine = str(
            values.get("api_engine", _raw_value(env, "API_ENGINE", self.api_engine))
        )
        self.native_modules = bool(
            values.get(
                "native_modules",
                _bool_value(env, "NATIVE_MODULES", self.native_modules),
            )
        )


@lru_cache
def get_settings() -> Settings:
    """Return the cached project settings."""
    return Settings()


settings = get_settings()

if settings.secret_key == _DEFAULT_SECRET_KEY:
    warnings.warn(
        "SECRET_KEY is still using the generated default. "
        "Set SECRET_KEY in .env before deployment.",
        RuntimeWarning,
        stacklevel=2,
    )

APP_NAME = settings.app_name
API_TITLE = settings.api_title
DEBUG = settings.debug
SECRET_KEY = settings.secret_key
ALLOWED_HOSTS = settings.allowed_hosts
INSTALLED_APPS = settings.installed_apps
DATABASE = settings.database_url

AUTH = {{"ENABLED": settings.auth_enabled}}
ADMIN = {{"ENABLED": settings.admin_enabled}}
AI = {{"ENABLED": settings.ai_enabled}}
WORKER = {{"ENABLED": settings.worker_enabled}}
PAYMENTS = {{"ENABLED": settings.payments_enabled}}

BOLTRA = {{
    "MODE": settings.boltra_mode,
    "API_ENGINE": settings.api_engine,
    "NATIVE_MODULES": settings.native_modules,
}}
'''


def env_example(name: str) -> str:
    """Return the generated .env.example content."""
    title = display_title(name)
    return f"""APP_NAME={name}
API_TITLE={title}
DEBUG=true
SECRET_KEY=change-this-secret-key
ALLOWED_HOSTS=["localhost","127.0.0.1"]
DATABASE_URL=

AUTH_ENABLED=false
ADMIN_ENABLED=false
AI_ENABLED=false
WORKER_ENABLED=false
PAYMENTS_ENABLED=false

BOLTRA_MODE=fastapi-kit
API_ENGINE=fastapi
NATIVE_MODULES=false
"""


def pyproject_toml(name: str) -> str:
    """Return the generated ``pyproject.toml`` source."""
    return f'''[project]
name = "{name}"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "pydantic-settings>=2.6",
    "uvicorn[standard]>=0.27",
]

[tool.boltra]
mode = "fastapi-kit"
app = "main:app"
settings = "settings.py"
host = "127.0.0.1"
port = 8000
# Boltra CLI is used to scaffold and manage this project.
# Add `boltra` as a dependency when it is published or install from source:
#   uv add boltra --path ../path/to/boltra
'''
