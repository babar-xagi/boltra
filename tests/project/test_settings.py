"""Behavioral tests for generated settings with and without Pydantic."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path
from types import ModuleType

import pytest

from boltra.project.generator import create_project


@pytest.fixture(params=["pydantic", "fallback"])
def settings_module(
    request: pytest.FixtureRequest,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> ModuleType:
    """Import a fresh generated module under each settings backend."""
    project = create_project("demo", cwd=tmp_path)
    if request.param == "fallback":
        monkeypatch.setitem(sys.modules, "pydantic_settings", None)
    else:
        import pydantic_settings  # noqa: F401

    keys = [
        "APP_NAME",
        "API_TITLE",
        "DEBUG",
        "SECRET_KEY",
        "ALLOWED_HOSTS",
        "INSTALLED_APPS",
        "DATABASE_URL",
        "AUTH_ENABLED",
        "ADMIN_ENABLED",
        "AI_ENABLED",
        "WORKER_ENABLED",
        "PAYMENTS_ENABLED",
        "BOLTRA_MODE",
        "API_ENGINE",
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)
    path = project / "settings.py"
    module = ModuleType("generated_settings")
    module.__file__ = str(path)
    monkeypatch.setitem(sys.modules, module.__name__, module)
    with pytest.warns(RuntimeWarning, match="SECRET_KEY"):
        exec(
            compile(path.read_text(encoding="utf-8"), str(path), "exec"),
            module.__dict__,
        )
    assert module._HAS_PYDANTIC_SETTINGS is (request.param == "pydantic")
    return module


def test_settings_defaults_and_cache(settings_module: ModuleType) -> None:
    """Defaults, aliases, and cached settings agree across both backends."""
    module = settings_module
    assert module.get_settings() is module.settings
    assert module.API_TITLE == "Demo API"
    assert module.DEBUG is True
    assert module.ALLOWED_HOSTS == ["localhost", "127.0.0.1"]
    assert module.DATABASE is None
    assert module.AUTH == {"ENABLED": False}


def test_settings_constructor_overrides(settings_module: ModuleType) -> None:
    """Explicit keyword arguments take precedence for every field type."""
    settings = settings_module.Settings(
        api_title="Custom",
        allowed_hosts=["example.com"],
        installed_apps=["apps.school"],
        debug="false",
        auth_enabled="false",
        database_url="postgresql://localhost/demo",
    )
    assert settings.api_title == "Custom"
    assert settings.allowed_hosts == ["example.com"]
    assert settings.installed_apps == ["apps.school"]
    assert settings.debug is False
    assert settings.auth_enabled is False
    assert settings.database_url == "postgresql://localhost/demo"


def test_settings_env_precedence(
    settings_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Explicit values beat environment values, which beat the .env file."""
    Path(settings_module.__file__).with_name(".env").write_text(
        'API_TITLE="From file"\nDEBUG=false\nALLOWED_HOSTS=["file.test"]\n'
        'INSTALLED_APPS=["apps.school"]\nAUTH_ENABLED=true\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("API_TITLE", "From environment")
    settings = settings_module.Settings()
    assert settings.api_title == "From environment"
    assert settings.debug is False
    assert settings.allowed_hosts == ["file.test"]
    assert settings.installed_apps == ["apps.school"]
    assert settings.auth_enabled is True
    assert settings_module.Settings(api_title="Explicit").api_title == "Explicit"


@pytest.mark.parametrize("value", ["false", "0", "off", "no", "true", "1", "yes", "on"])
def test_settings_boolean_values(
    settings_module: ModuleType, monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    """Settings parse common boolean forms rather than Python string truthiness."""
    monkeypatch.setenv("DEBUG", value)
    assert settings_module.Settings().debug is (value in {"true", "1", "yes", "on"})


def test_settings_invalid_boolean(
    settings_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Invalid boolean configuration must be reported instead of silently coerced."""
    monkeypatch.setenv("DEBUG", "invalid")
    with pytest.raises(ValueError):
        settings_module.Settings()


def test_settings_lists_do_not_share_state(settings_module: ModuleType) -> None:
    """Mutable list defaults belong to each Settings instance."""
    first = settings_module.Settings()
    first.allowed_hosts.append("extra.test")
    first.installed_apps.append("apps.one")
    second = settings_module.Settings()
    assert second.allowed_hosts == ["localhost", "127.0.0.1"]
    assert second.installed_apps == []


def test_settings_custom_secret_has_no_warning(
    settings_module: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A configured secret avoids the placeholder-secret warning on import."""
    monkeypatch.setenv("SECRET_KEY", "a-local-custom-secret")
    module = ModuleType("generated_custom_secret")
    module.__file__ = settings_module.__file__
    monkeypatch.setitem(sys.modules, module.__name__, module)
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        path = Path(module.__file__)
        exec(
            compile(path.read_text(encoding="utf-8"), str(path), "exec"),
            module.__dict__,
        )
    assert not recorded
    assert module.SECRET_KEY == "a-local-custom-secret"
