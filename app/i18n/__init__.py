"""Internationalization for Pics2PPT (Persian + English)."""

from __future__ import annotations

from PySide6.QtCore import Qt

from . import catalog_en, catalog_fa
from .locale_detect import detect, normalize

_CATALOGS = {"fa": catalog_fa.STRINGS, "en": catalog_en.STRINGS}

_ui_language = "fa"
_slide_language = "fa"
_build_slide_language = "fa"


def set_ui_language(code: str) -> None:
    global _ui_language
    _ui_language = normalize(code)


def ui_language() -> str:
    return _ui_language


def is_rtl() -> bool:
    return _ui_language == "fa"


def dialog_direction() -> Qt.LayoutDirection:
    return Qt.LayoutDirection.RightToLeft if is_rtl() else Qt.LayoutDirection.LeftToRight


def set_build_slide_language(code: str) -> None:
    global _build_slide_language
    _build_slide_language = normalize(code)


def build_slide_language() -> str:
    return _build_slide_language


def resolve_slide_language(settings: dict) -> str:
    mode = settings.get("slide_language_mode", "same_as_ui")
    if mode == "same_as_ui":
        return normalize(settings.get("ui_language", _ui_language))
    return normalize(settings.get("slide_language", "fa"))


def t(key: str, *, lang: str | None = None, **kwargs: object) -> str:
    """Translate a key for UI (or explicit lang). Raises KeyError if missing."""
    lng = normalize(lang) if lang else _ui_language
    catalog = _CATALOGS[lng]
    if key not in catalog:
        raise KeyError(f"Missing i18n key: {key!r} ({lng})")
    text = catalog[key]
    if kwargs:
        return text.format(**kwargs)
    return text


def t_slide(key: str, **kwargs: object) -> str:
    """Translate using the active build/slide language snapshot."""
    catalog = _CATALOGS[_build_slide_language]
    if key not in catalog:
        raise KeyError(f"Missing i18n key: {key!r} ({_build_slide_language})")
    text = catalog[key]
    if kwargs:
        return text.format(**kwargs)
    return text


def default_ui_language_for_new_install() -> str:
    return detect()


__all__ = [
    "build_slide_language",
    "default_ui_language_for_new_install",
    "dialog_direction",
    "is_rtl",
    "resolve_slide_language",
    "set_build_slide_language",
    "set_ui_language",
    "t",
    "t_slide",
    "ui_language",
]
