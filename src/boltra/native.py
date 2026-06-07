"""Rust acceleration bridge with automatic Python fallback.

Every hot path will delegate to ``boltra._native`` when available and fall back
to pure Python when the extension is missing or disabled via ``BOLTRA_DISABLE_NATIVE``.
"""

from __future__ import annotations

import logging
import os
from typing import Final

logger = logging.getLogger(__name__)

_DISABLE_ENV: Final = "BOLTRA_DISABLE_NATIVE"
_TRUTHY: Final = frozenset({"1", "true", "yes", "on"})

_native_import_attempted = False
_native_available = False


def _native_disabled() -> bool:
    """Return True when native acceleration is explicitly turned off."""
    return os.environ.get(_DISABLE_ENV, "").lower() in _TRUTHY


def is_available() -> bool:
    """Return True when the Rust native extension is loaded and active."""
    global _native_import_attempted, _native_available

    if _native_disabled():
        return False

    if _native_import_attempted:
        return _native_available

    _native_import_attempted = True
    try:
        import boltra._native as _native

        _native_available = bool(_native.is_available())
    except ImportError:
        _native_available = False
        logger.info(
            "Boltra native extension unavailable; using Python fallback.",
        )

    return _native_available


def native_version() -> str | None:
    """Return the native extension version, or None when unavailable."""
    if not is_available():
        return None

    import boltra._native as _native

    return str(_native.version())
