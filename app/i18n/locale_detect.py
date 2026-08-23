"""Detect default UI language from system locale."""

from __future__ import annotations

import locale

VALID = frozenset({"fa", "en"})


def detect() -> str:
    """Return ``fa`` for Persian system locales, otherwise ``en``."""
    try:
        from PySide6.QtCore import QLocale

        lang = QLocale.system().language()
        if lang == QLocale.Language.Persian:
            return "fa"
    except Exception:
        pass

    try:
        loc = locale.getlocale()
        if isinstance(loc, tuple):
            loc = loc[0]
        if loc and str(loc).lower().startswith("fa"):
            return "fa"
    except Exception:
        pass
    return "en"


def normalize(code: str | None) -> str:
    if code in VALID:
        return code  # type: ignore[return-value]
    return "en"
