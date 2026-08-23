"""Persistent application settings (JSON in user profile)."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

VALID_THEMES = frozenset({"dark_cyan", "dark_purple", "light"})
SETTINGS_VERSION = 4

# Cleared on every launch — must not survive across app restarts.
SESSION_INPUT_KEYS = frozenset({"last_input_dir", "footer_text", "logo_right", "logo_left"})

# Keys loaded from legacy installs but never copied verbatim on first migration.
LEGACY_MERGE_KEYS = (
    "output_folder_name",
    "slide_width_inches",
    "slide_height_inches",
    "images_per_slide",
    "jpeg_quality",
    "max_dimension",
    "font_name",
    "title_font_size",
    "caption_font_size",
    "footer_font_size",
    "enable_section_dividers",
    "enable_image_zoom",
    "enable_hover_zoom",
    "enable_image_shadow",
    "enable_image_border",
    "caption_from_filename",
    "open_output_when_done",
    "window_geometry",
)

DEFAULT_SETTINGS = {
    "settings_version": SETTINGS_VERSION,
    "theme": "dark_cyan",
    "font_size": "medium",
    "footer_text": "",
    "logo_right": "",
    "logo_left": "",
    "output_folder_name": "Output_PPTX",
    "slide_width_inches": 13.33,
    "slide_height_inches": 7.5,
    "images_per_slide": 4,
    "jpeg_quality": 75,
    "max_dimension": 1200,
    "font_name": "B Nazanin",
    "title_font_size": 22,
    "caption_font_size": 11,
    "footer_font_size": 12,
    "enable_section_dividers": True,
    "enable_image_zoom": True,
    "enable_hover_zoom": True,
    "enable_image_shadow": True,
    "enable_image_border": True,
    "caption_from_filename": True,
    "open_output_when_done": False,
    "last_input_dir": "",
    "window_geometry": "",
}


class SettingsManager:
    def __init__(self) -> None:
        self._dir = Path.home() / ".pics2ppt"
        self._legacy_dirs = [
            Path.home() / ".slidereport",
            Path.home() / ".gen_powerpoint",
        ]
        self._path = self._dir / "settings.json"
        self._data = deepcopy(DEFAULT_SETTINGS)
        self.load()

    @property
    def path(self) -> Path:
        return self._path

    def _read_json(self, path: Path) -> dict | None:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return raw if isinstance(raw, dict) else None

    def _find_legacy_settings(self) -> dict | None:
        for legacy in self._legacy_dirs:
            candidate = legacy / "settings.json"
            if candidate.is_file():
                return self._read_json(candidate)
        return None

    def _normalize(self) -> bool:
        changed = False
        theme = self._data.get("theme")
        if theme not in VALID_THEMES:
            self._data["theme"] = DEFAULT_SETTINGS["theme"]
            changed = True
        font_size = self._data.get("font_size")
        if font_size not in {"small", "medium", "large"}:
            self._data["font_size"] = DEFAULT_SETTINGS["font_size"]
            changed = True
        version = int(self._data.get("settings_version") or 0)
        if version < SETTINGS_VERSION:
            # Fresh Pics2PPT policy: default visual theme is dark cyan.
            self._data["theme"] = DEFAULT_SETTINGS["theme"]
            self._data["settings_version"] = SETTINGS_VERSION
            changed = True
        for key in SESSION_INPUT_KEYS:
            if self._data.get(key):
                self._data[key] = ""
                changed = True
        return changed

    def load(self) -> None:
        dirty = False
        if self._path.is_file():
            loaded = self._read_json(self._path)
            if loaded:
                self._data.update(loaded)
        else:
            legacy = self._find_legacy_settings()
            if legacy:
                merged = deepcopy(DEFAULT_SETTINGS)
                for key in LEGACY_MERGE_KEYS:
                    if key in legacy:
                        merged[key] = legacy[key]
                self._data = merged
            dirty = True

        if self._normalize():
            dirty = True

        if dirty:
            self._write()

    def clear_session_inputs(self) -> None:
        for key in SESSION_INPUT_KEYS:
            self._data[key] = ""

    def _write(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def save(self) -> None:
        self.clear_session_inputs()
        self._data["settings_version"] = SETTINGS_VERSION
        theme = self._data.get("theme")
        if theme not in VALID_THEMES:
            self._data["theme"] = DEFAULT_SETTINGS["theme"]
        self._write()

    def get(self, key: str, default=None):
        return self._data.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value) -> None:
        if key in SESSION_INPUT_KEYS:
            return
        self._data[key] = value

    def all(self) -> dict:
        return deepcopy(self._data)

    def reset(self) -> None:
        keep_output = self._data.get("output_folder_name", "Output_PPTX")
        self._data = deepcopy(DEFAULT_SETTINGS)
        self._data["output_folder_name"] = keep_output
        self.save()

    def build_settings_dict(self) -> dict:
        keys = [
            "footer_text",
            "logo_right",
            "logo_left",
            "output_folder_name",
            "slide_width_inches",
            "slide_height_inches",
            "images_per_slide",
            "jpeg_quality",
            "max_dimension",
            "font_name",
            "title_font_size",
            "caption_font_size",
            "footer_font_size",
            "enable_section_dividers",
            "enable_image_zoom",
            "enable_hover_zoom",
            "enable_image_shadow",
            "enable_image_border",
            "caption_from_filename",
        ]
        return {k: self.get(k) for k in keys}
