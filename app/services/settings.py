"""Persistent application settings (JSON in user profile)."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from app.i18n.locale_detect import detect, normalize as normalize_lang
from app.services import language_prefs

VALID_THEMES = frozenset({"dark_cyan", "dark_purple", "light"})
VALID_UI_LANGUAGES = frozenset({"fa", "en"})
VALID_SLIDE_LANGUAGE_MODES = frozenset({"same_as_ui", "fixed"})
VALID_OUTPUT_MODES = frozenset({"auto", "template", "code"})
SETTINGS_VERSION = 6

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
    "ui_language",
    "slide_language_mode",
    "slide_language",
    "ui_language_confirmed",
    "output_mode",
    "template_path",
    "slide_size_preset",
    "image_fit",
    "enable_auto_rotate",
    "strip_gps",
    "caption_source",
    "enable_native_sections",
    "write_build_report",
    "doc_title",
    "doc_author",
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
    "ui_language": "fa",
    "slide_language_mode": "same_as_ui",
    "slide_language": "fa",
    # False until the first-run picker (or v4 migration) confirms a choice.
    "ui_language_confirmed": False,
    "output_mode": "auto",
    "template_path": "",
    "slide_size_preset": "widescreen_16_9",
    "image_fit": "fit",
    "enable_auto_rotate": True,
    "strip_gps": True,
    "caption_source": "filename",
    "enable_native_sections": True,
    "write_build_report": True,
    "enable_index_slide": False,
    "active_preset": "",
    "enable_com_postprocess": False,
    "enable_libreoffice_preview": False,
    "enable_plugins": False,
    "preview_format": "pdf",
    "doc_title": "",
    "doc_author": "",
    "color_title": "000000",
    "color_muted": "505050",
    "color_accent": "0F3D2E",
    "color_border": "B4B4B4",
    "color_background": "FFFFFF",
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
        self._fresh_install = False
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

    def _apply_language_prefs(self) -> None:
        if language_prefs.is_confirmed(self._dir):
            lang = language_prefs.read_language(self._dir)
            if lang:
                self._data["ui_language"] = lang
                self._data["slide_language"] = lang
                self._data["slide_language_mode"] = "same_as_ui"
                self._data["ui_language_confirmed"] = True

    def _language_confirmed_from_disk(self, raw: dict, *, from_legacy: bool) -> bool:
        if language_prefs.is_confirmed(self._dir):
            return True
        if "ui_language_confirmed" in raw:
            return raw["ui_language_confirmed"] is True
        if from_legacy:
            return False
        version = int(raw.get("settings_version") or 0)
        if version < 5:
            return True
        return False

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
        if version < 4:
            self._data["theme"] = DEFAULT_SETTINGS["theme"]
            changed = True
        if version < 5:
            if version == 0 or self._fresh_install:
                detected = detect()
                self._data["ui_language"] = detected
                self._data["slide_language"] = detected
                if "ui_language_confirmed" not in self._data:
                    self._data["ui_language_confirmed"] = False
            else:
                self._data.setdefault("ui_language", "fa")
                self._data.setdefault("slide_language", "fa")
                if "ui_language_confirmed" not in self._data:
                    self._data["ui_language_confirmed"] = True
                    self._sync_language_prefs()
            self._data["slide_language_mode"] = "same_as_ui"
            changed = True
        if version < 6:
            self._data.setdefault("output_mode", "auto")
            self._data.setdefault("template_path", "")
            self._data.setdefault("slide_size_preset", "widescreen_16_9")
            self._data.setdefault("image_fit", "fit")
            self._data.setdefault("enable_auto_rotate", True)
            self._data.setdefault("strip_gps", True)
            self._data.setdefault("caption_source", "filename")
            self._data.setdefault("enable_native_sections", True)
            self._data.setdefault("write_build_report", True)
            self._data.setdefault("enable_index_slide", False)
            self._data.setdefault("color_title", "000000")
            self._data.setdefault("color_muted", "505050")
            self._data.setdefault("color_accent", "0F3D2E")
            self._data.setdefault("color_border", "B4B4B4")
            self._data.setdefault("color_background", "FFFFFF")
            changed = True
        if version < SETTINGS_VERSION:
            self._data["settings_version"] = SETTINGS_VERSION
            changed = True
        output_mode = self._data.get("output_mode")
        if output_mode not in VALID_OUTPUT_MODES:
            self._data["output_mode"] = DEFAULT_SETTINGS["output_mode"]
            changed = True
        from app.core.pptx.slide_sizes import VALID_SLIDE_SIZE_PRESETS
        from app.core.pptx.template_pictures import VALID_IMAGE_FIT

        preset = self._data.get("slide_size_preset")
        if preset not in VALID_SLIDE_SIZE_PRESETS:
            self._data["slide_size_preset"] = DEFAULT_SETTINGS["slide_size_preset"]
            changed = True
        if self._data.get("image_fit") not in VALID_IMAGE_FIT:
            self._data["image_fit"] = DEFAULT_SETTINGS["image_fit"]
            changed = True
        if "ui_language_confirmed" not in self._data:
            self._data["ui_language_confirmed"] = False
            changed = True
        # Coerce JSON quirks (0/1/"true") but preserve explicit False.
        raw_confirmed = self._data.get("ui_language_confirmed")
        if raw_confirmed is True or raw_confirmed is False:
            pass
        elif raw_confirmed in (0, "0", "false", "False", "no", "No"):
            self._data["ui_language_confirmed"] = False
            changed = True
        else:
            self._data["ui_language_confirmed"] = bool(raw_confirmed)
            changed = True
        ui_lang = self._data.get("ui_language")
        if ui_lang not in VALID_UI_LANGUAGES:
            self._data["ui_language"] = DEFAULT_SETTINGS["ui_language"]
            changed = True
        slide_mode = self._data.get("slide_language_mode")
        if slide_mode not in VALID_SLIDE_LANGUAGE_MODES:
            self._data["slide_language_mode"] = DEFAULT_SETTINGS["slide_language_mode"]
            changed = True
        slide_lang = self._data.get("slide_language")
        if slide_lang not in VALID_UI_LANGUAGES:
            self._data["slide_language"] = DEFAULT_SETTINGS["slide_language"]
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
                self._data = deepcopy(DEFAULT_SETTINGS)
                self._data.update(loaded)
                if "ui_language_confirmed" not in loaded:
                    self._data["ui_language_confirmed"] = self._language_confirmed_from_disk(
                        loaded, from_legacy=False
                    )
                    dirty = True
            else:
                self._fresh_install = True
                self._data = deepcopy(DEFAULT_SETTINGS)
                detected = detect()
                self._data["ui_language"] = detected
                self._data["slide_language"] = detected
                self._data["ui_language_confirmed"] = False
                dirty = True
        else:
            legacy = self._find_legacy_settings()
            if legacy:
                merged = deepcopy(DEFAULT_SETTINGS)
                for key in LEGACY_MERGE_KEYS:
                    if key in legacy:
                        merged[key] = legacy[key]
                if "ui_language_confirmed" not in legacy:
                    merged["ui_language_confirmed"] = self._language_confirmed_from_disk(
                        legacy, from_legacy=True
                    )
                    if not merged["ui_language_confirmed"] and "ui_language" not in legacy:
                        detected = detect()
                        merged["ui_language"] = detected
                        merged["slide_language"] = detected
                        merged["slide_language_mode"] = "same_as_ui"
                self._data = merged
            else:
                self._fresh_install = True
                detected = detect()
                self._data = deepcopy(DEFAULT_SETTINGS)
                self._data["ui_language"] = detected
                self._data["slide_language"] = detected
                self._data["ui_language_confirmed"] = False
            dirty = True

        if self._normalize():
            dirty = True

        self._apply_language_prefs()

        if dirty:
            self._write()

    def clear_session_inputs(self) -> None:
        for key in SESSION_INPUT_KEYS:
            self._data[key] = ""

    def _write(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        payload = deepcopy(self._data)
        if "ui_language_confirmed" not in payload:
            payload["ui_language_confirmed"] = False
        self._path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _sync_language_prefs(self) -> None:
        if self._data.get("ui_language_confirmed") is True:
            lang = normalize_lang(str(self._data.get("ui_language", "fa")))
            if not language_prefs.is_confirmed(self._dir):
                language_prefs.write_confirmed(lang, base_dir=self._dir)

    def save(self) -> None:
        self.clear_session_inputs()
        self._data["settings_version"] = SETTINGS_VERSION
        theme = self._data.get("theme")
        if theme not in VALID_THEMES:
            self._data["theme"] = DEFAULT_SETTINGS["theme"]
        # Dedicated prefs file wins — survives settings.json rewrites on close.
        if language_prefs.is_confirmed(self._dir):
            self._data["ui_language_confirmed"] = True
            pref_lang = language_prefs.read_language(self._dir)
            if pref_lang:
                self._data["ui_language"] = pref_lang
                if self._data.get("slide_language_mode") == "same_as_ui":
                    self._data["slide_language"] = pref_lang
        elif self._path.is_file():
            prev = self._read_json(self._path) or {}
            if prev.get("ui_language_confirmed") is True:
                self._data["ui_language_confirmed"] = True
        if self._data.get("ui_language_confirmed") is True:
            pass
        elif self._data.get("ui_language_confirmed") is not False:
            self._data["ui_language_confirmed"] = bool(self._data.get("ui_language_confirmed"))
        self._sync_language_prefs()
        self._write()

    def get(self, key: str, default=None):
        return self._data.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value) -> None:
        if key in SESSION_INPUT_KEYS:
            return
        self._data[key] = value

    def all(self) -> dict:
        return deepcopy(self._data)

    def needs_language_prompt(self) -> bool:
        if language_prefs.is_confirmed(self._dir):
            return False
        return self._data.get("ui_language_confirmed") is not True

    def confirm_ui_language(self, code: str) -> None:
        lang = normalize_lang(code)
        language_prefs.write_confirmed(lang, base_dir=self._dir)
        self._data["ui_language"] = lang
        self._data["slide_language_mode"] = "same_as_ui"
        self._data["slide_language"] = lang
        self._data["ui_language_confirmed"] = True
        self.save()

    def reset(self) -> None:
        keep_output = self._data.get("output_folder_name", "Output_PPTX")
        keep_lang = normalize_lang(str(self._data.get("ui_language", "fa")))
        if language_prefs.is_confirmed(self._dir):
            pref_lang = language_prefs.read_language(self._dir)
            if pref_lang:
                keep_lang = pref_lang
        self._data = deepcopy(DEFAULT_SETTINGS)
        self._data["output_folder_name"] = keep_output
        self._data["ui_language"] = keep_lang
        self._data["slide_language"] = keep_lang
        self._data["slide_language_mode"] = "same_as_ui"
        self._data["ui_language_confirmed"] = True
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
            "ui_language",
            "slide_language_mode",
            "slide_language",
            "output_mode",
            "template_path",
            "slide_size_preset",
            "image_fit",
            "layout_index_grid",
            "layout_index_detail",
            "layout_index_divider",
            "enable_auto_rotate",
            "strip_gps",
            "caption_source",
            "enable_native_sections",
            "write_build_report",
            "doc_title",
            "doc_author",
            "enable_index_slide",
            "active_preset",
            "enable_com_postprocess",
            "enable_libreoffice_preview",
            "enable_plugins",
            "preview_format",
            "doc_subject",
            "doc_category",
            "doc_keywords",
            "color_title",
            "color_muted",
            "color_accent",
            "color_border",
            "color_background",
        ]
        return {k: self.get(k) for k in keys}

    def resolved_slide_language(self) -> str:
        from app.i18n import resolve_slide_language

        return resolve_slide_language(self._data)
