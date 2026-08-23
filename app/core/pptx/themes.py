"""Theme color helpers for Expert Panel RGB overrides."""

from __future__ import annotations

from pptx.dml.color import RGBColor

from .constants import ACCENT_COLOR, BORDER_COLOR, MUTED_COLOR, TITLE_COLOR

DEFAULT_HEX = {
    "color_title": "000000",
    "color_muted": "505050",
    "color_accent": "0F3D2E",
    "color_border": "B4B4B4",
    "color_background": "FFFFFF",
}


def normalize_hex(value: str | None, fallback: str) -> str:
    raw = (value or "").strip().lstrip("#").upper()
    if len(raw) == 6 and all(c in "0123456789ABCDEF" for c in raw):
        return raw
    return fallback.upper()


def rgb_from_hex(value: str | None, default: RGBColor) -> RGBColor:
    h = normalize_hex(value, "")
    if len(h) != 6:
        return default
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def title_color(settings) -> RGBColor:
    return rgb_from_hex(getattr(settings, "color_title", None), TITLE_COLOR)


def muted_color(settings) -> RGBColor:
    return rgb_from_hex(getattr(settings, "color_muted", None), MUTED_COLOR)


def accent_color(settings) -> RGBColor:
    return rgb_from_hex(getattr(settings, "color_accent", None), ACCENT_COLOR)


def border_color(settings) -> RGBColor:
    return rgb_from_hex(getattr(settings, "color_border", None), BORDER_COLOR)
