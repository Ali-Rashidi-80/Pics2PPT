"""Resolve bundled asset paths (dev + PyInstaller)."""

from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def asset_path(*parts: str) -> Path:
    return app_root().joinpath(*parts)


def logo_png() -> Path:
    for candidate in (
        asset_path("assets", "app_icon_256.png"),
        asset_path("assets", "pics2ppt_logo.png"),
        asset_path("icon.ico"),
    ):
        if candidate.is_file():
            return candidate
    return asset_path("assets", "app_icon_256.png")


def icon_ico() -> Path:
    return asset_path("icon.ico")
