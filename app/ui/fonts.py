"""Typography helpers for cross-Windows consistency."""

from __future__ import annotations

import sys

from PySide6.QtGui import QFont

FONT_SCALES = {
    "small": {"base": 12, "label": 11, "caption": 10, "title": 20, "brand": 16},
    "medium": {"base": 13, "label": 12, "caption": 11, "title": 22, "brand": 17},
    "large": {"base": 15, "label": 13, "caption": 12, "title": 24, "brand": 19},
}


def _ui_font_stack() -> str:
    if sys.platform == "win32":
        return '"Segoe UI", "Tahoma", "B Nazanin", sans-serif'
    return '"B Nazanin", "Tahoma", "Segoe UI", sans-serif'


def _display_font_stack() -> str:
    return '"B Nazanin", "Vazir", "Tahoma", "Segoe UI", sans-serif'


def _mono_font_stack() -> str:
    if sys.platform == "win32":
        return '"Cascadia Mono", "Consolas", monospace'
    return '"Consolas", "Courier New", monospace'


def font_css_roles() -> dict[str, str]:
    return {
        "ui": _ui_font_stack(),
        "display": _display_font_stack(),
        "mono": _mono_font_stack(),
        "tooltip": _ui_font_stack(),
    }


def configure_app_typography(app, font_key: str = "medium") -> None:
    scale = FONT_SCALES.get(font_key, FONT_SCALES["medium"])
    font = QFont()
    if sys.platform == "win32":
        font.setFamily("Segoe UI")
    else:
        font.setFamily("Tahoma")
    font.setPointSize(scale["base"])
    app.setFont(font)
