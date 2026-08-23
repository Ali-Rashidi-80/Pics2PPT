"""Dedicated persistence for first-run UI language choice (survives settings rewrites)."""

from __future__ import annotations

import json
from pathlib import Path

from app.i18n.locale_detect import normalize as normalize_lang

_PREFS_NAME = "ui_language.json"


def _prefs_path(base_dir: Path | None = None) -> Path:
    root = base_dir if base_dir is not None else Path.home() / ".pics2ppt"
    return root / _PREFS_NAME


def read(base_dir: Path | None = None) -> dict | None:
    path = _prefs_path(base_dir)
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None


def is_confirmed(base_dir: Path | None = None) -> bool:
    raw = read(base_dir)
    return bool(raw and raw.get("confirmed") is True)


def read_language(base_dir: Path | None = None) -> str | None:
    raw = read(base_dir)
    if not raw or raw.get("confirmed") is not True:
        return None
    lang = normalize_lang(str(raw.get("ui_language", "")))
    return lang if lang in {"fa", "en"} else None


def write_confirmed(ui_language: str, *, base_dir: Path | None = None) -> None:
    lang = normalize_lang(ui_language)
    root = base_dir if base_dir is not None else Path.home() / ".pics2ppt"
    root.mkdir(parents=True, exist_ok=True)
    path = _prefs_path(root)
    payload = {"ui_language": lang, "confirmed": True}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
