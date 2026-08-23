"""Persistent application settings (JSON in user profile)."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

DEFAULT_SETTINGS = {
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
        self._dir = Path.home() / ".slidereport"
        self._legacy_dir = Path.home() / ".gen_powerpoint"
        self._path = self._dir / "settings.json"
        self._data = deepcopy(DEFAULT_SETTINGS)
        self.load()

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> None:
        if self._path.is_file():
            raw_path = self._path
        elif (self._legacy_dir / "settings.json").is_file():
            raw_path = self._legacy_dir / "settings.json"
        else:
            return
        try:
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                self._data.update(raw)
        except (OSError, json.JSONDecodeError):
            pass

    def save(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get(self, key: str, default=None):
        return self._data.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value) -> None:
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
