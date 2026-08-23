"""Named PPTX output presets — Report / Minimal / Print / Brand."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

PRESET_DIR_NAME = "presets"
BUILTIN_PRESET_IDS = ("report", "minimal", "print", "brand")

# Keys applied when a preset is selected (never touch UI language / theme).
PRESET_APPLY_KEYS = frozenset({
    "output_mode",
    "slide_size_preset",
    "slide_width_inches",
    "slide_height_inches",
    "images_per_slide",
    "jpeg_quality",
    "max_dimension",
    "title_font_size",
    "caption_font_size",
    "footer_font_size",
    "enable_section_dividers",
    "enable_image_zoom",
    "enable_hover_zoom",
    "enable_image_shadow",
    "enable_image_border",
    "caption_from_filename",
    "caption_source",
    "enable_auto_rotate",
    "strip_gps",
    "image_fit",
    "enable_native_sections",
    "write_build_report",
    "enable_index_slide",
    "color_title",
    "color_muted",
    "color_accent",
    "color_border",
    "color_background",
})

_BUILTIN: dict[str, dict] = {
    "report": {
        "label_en": "Report",
        "label_fa": "گزارش",
        "settings": {
            "output_mode": "auto",
            "slide_size_preset": "widescreen_16_9",
            "slide_width_inches": 13.33,
            "slide_height_inches": 7.5,
            "images_per_slide": 4,
            "jpeg_quality": 75,
            "max_dimension": 1200,
            "title_font_size": 22,
            "caption_font_size": 11,
            "footer_font_size": 12,
            "enable_section_dividers": True,
            "enable_image_zoom": True,
            "enable_hover_zoom": True,
            "enable_image_shadow": True,
            "enable_image_border": True,
            "caption_from_filename": True,
            "caption_source": "filename",
            "enable_index_slide": True,
            "color_title": "000000",
            "color_muted": "505050",
            "color_accent": "0F3D2E",
            "color_border": "B4B4B4",
            "color_background": "FFFFFF",
        },
    },
    "minimal": {
        "label_en": "Minimal",
        "label_fa": "مینیمال",
        "settings": {
            "output_mode": "code",
            "images_per_slide": 4,
            "jpeg_quality": 70,
            "max_dimension": 1000,
            "enable_section_dividers": False,
            "enable_image_zoom": False,
            "enable_hover_zoom": False,
            "enable_image_shadow": False,
            "enable_image_border": False,
            "enable_index_slide": False,
            "enable_native_sections": False,
            "caption_source": "filename",
            "color_title": "222222",
            "color_muted": "777777",
            "color_accent": "444444",
            "color_border": "DDDDDD",
        },
    },
    "print": {
        "label_en": "Print",
        "label_fa": "چاپ",
        "settings": {
            "output_mode": "code",
            "slide_size_preset": "a4_landscape",
            "slide_width_inches": 11.69,
            "slide_height_inches": 8.27,
            "images_per_slide": 2,
            "jpeg_quality": 90,
            "max_dimension": 1800,
            "enable_image_zoom": False,
            "enable_hover_zoom": False,
            "enable_image_shadow": False,
            "enable_image_border": True,
            "enable_index_slide": True,
            "color_title": "000000",
            "color_muted": "404040",
            "color_accent": "000000",
            "color_border": "999999",
            "color_background": "FFFFFF",
        },
    },
    "brand": {
        "label_en": "Brand",
        "label_fa": "برند",
        "settings": {
            "output_mode": "auto",
            "images_per_slide": 4,
            "jpeg_quality": 80,
            "max_dimension": 1400,
            "title_font_size": 24,
            "caption_font_size": 12,
            "footer_font_size": 11,
            "enable_section_dividers": True,
            "enable_image_zoom": True,
            "enable_hover_zoom": True,
            "enable_image_shadow": True,
            "enable_image_border": True,
            "enable_index_slide": True,
            "color_title": "0A2540",
            "color_muted": "5A6A7A",
            "color_accent": "0F3D2E",
            "color_border": "C5D0DA",
            "color_background": "F7FAFC",
        },
    },
}


def presets_dir(base_dir: Path | None = None) -> Path:
    root = base_dir if base_dir is not None else Path.home() / ".pics2ppt"
    path = root / PRESET_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_builtin_presets() -> list[str]:
    return list(BUILTIN_PRESET_IDS)


def get_builtin_preset(preset_id: str) -> dict | None:
    raw = _BUILTIN.get(preset_id)
    return deepcopy(raw) if raw else None


def preset_settings(preset_id: str) -> dict:
    builtin = get_builtin_preset(preset_id)
    if builtin:
        return deepcopy(builtin["settings"])
    return {}


def list_user_presets(base_dir: Path | None = None) -> list[str]:
    names = []
    for path in sorted(presets_dir(base_dir).glob("*.json")):
        names.append(path.stem)
    return names


def _safe_name(name: str) -> str:
    cleaned = re.sub(r"[^\w\-]+", "_", name.strip(), flags=re.UNICODE)
    return cleaned[:64] or "preset"


def save_user_preset(name: str, settings: dict, *, base_dir: Path | None = None) -> Path:
    safe = _safe_name(name)
    payload = {
        "name": name,
        "settings": {k: settings[k] for k in settings if k in PRESET_APPLY_KEYS},
    }
    path = presets_dir(base_dir) / f"{safe}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_user_preset(name: str, *, base_dir: Path | None = None) -> dict:
    safe = _safe_name(name)
    path = presets_dir(base_dir) / f"{safe}.json"
    if not path.is_file():
        # try exact stem match
        path = presets_dir(base_dir) / f"{name}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    settings = raw.get("settings") if isinstance(raw, dict) else {}
    if not isinstance(settings, dict):
        return {}
    return {k: v for k, v in settings.items() if k in PRESET_APPLY_KEYS}


def resolve_preset_settings(preset_id: str, *, base_dir: Path | None = None) -> dict:
    if preset_id in _BUILTIN:
        return preset_settings(preset_id)
    try:
        return load_user_preset(preset_id, base_dir=base_dir)
    except (OSError, json.JSONDecodeError, FileNotFoundError):
        return {}


def apply_preset_to_mapping(target: dict, preset_id: str, *, base_dir: Path | None = None) -> dict:
    """Return a new mapping with preset keys overlaid onto ``target``."""
    merged = dict(target)
    overlay = resolve_preset_settings(preset_id, base_dir=base_dir)
    for key, value in overlay.items():
        if key in PRESET_APPLY_KEYS:
            merged[key] = value
    merged["active_preset"] = preset_id
    return merged
