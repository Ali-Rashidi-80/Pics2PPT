"""Slide dimension presets for Expert Panel."""

from __future__ import annotations

SLIDE_SIZE_PRESETS: dict[str, tuple[float, float]] = {
    "widescreen_16_9": (13.33, 7.5),
    "standard_4_3": (10.0, 7.5),
    "a4_landscape": (11.69, 8.27),
}

VALID_SLIDE_SIZE_PRESETS = frozenset(SLIDE_SIZE_PRESETS) | {"custom"}


def preset_dimensions(preset: str) -> tuple[float, float] | None:
    return SLIDE_SIZE_PRESETS.get(preset)


def detect_preset(width: float, height: float, *, tol: float = 0.02) -> str:
    for key, (w, h) in SLIDE_SIZE_PRESETS.items():
        if abs(width - w) <= tol and abs(height - h) <= tol:
            return key
    return "custom"
