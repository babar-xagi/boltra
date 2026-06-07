"""Tests for the PyO3 native bridge and Python fallback path."""

from __future__ import annotations

import importlib
import sys

import pytest

import boltra
import boltra._native as _native_ext
import boltra.native as native
from boltra.cli.parser import parse_argv


def test_native_extension_imports() -> None:
    """The maturin-built extension module must be importable."""
    assert _native_ext.is_available() is True
    assert _native_ext.version() == boltra.__version__


def test_native_parse_argv() -> None:
    """Rust clap parser is exposed via ``parse_argv``."""
    result = _native_ext.parse_argv(["new", "hello"])
    assert result["action"] == "new"
    assert result["name"] == "hello"


def test_public_native_api() -> None:
    """Package-level helpers expose native availability."""
    assert boltra.is_available() is True
    assert boltra.native_version() == boltra.__version__


def test_native_disabled_via_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """BOLTRA_DISABLE_NATIVE forces the Python fallback parser."""
    monkeypatch.setenv("BOLTRA_DISABLE_NATIVE", "1")

    native._native_import_attempted = False
    native._native_available = False
    importlib.reload(native)
    importlib.reload(boltra)

    assert native.is_available() is False
    assert boltra.is_available() is False
    assert boltra.native_version() is None

    parsed = parse_argv(["--version"])
    assert parsed.action == "version"

    monkeypatch.delenv("BOLTRA_DISABLE_NATIVE", raising=False)
    native._native_import_attempted = False
    native._native_available = False
    importlib.reload(native)
    importlib.reload(boltra)


def test_native_fallback_on_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing extension module falls back to argparse without raising."""
    monkeypatch.setitem(sys.modules, "boltra._native", None)

    native._native_import_attempted = False
    native._native_available = False
    importlib.reload(native)

    assert native.is_available() is False
    parsed = parse_argv(["--version"])
    assert parsed.action == "version"

    monkeypatch.delitem(sys.modules, "boltra._native", raising=False)
    native._native_import_attempted = False
    native._native_available = False
    importlib.reload(native)
