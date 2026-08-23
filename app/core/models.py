"""Shared data models for PPTX generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BuildSettings:
    footer_text: str = ""
    logo_right: Path | None = None
    logo_left: Path | None = None
    output_folder_name: str = "Output_PPTX"

    slide_width_inches: float = 13.33
    slide_height_inches: float = 7.5
    images_per_slide: int = 4

    jpeg_quality: int = 75
    max_dimension: int = 1200

    font_name: str = "B Nazanin"
    title_font_size: int = 22
    caption_font_size: int = 11
    footer_font_size: int = 12

    enable_section_dividers: bool = True
    enable_image_zoom: bool = True
    enable_hover_zoom: bool = True
    enable_image_shadow: bool = True
    enable_image_border: bool = True
    caption_from_filename: bool = True

    ui_language: str = "fa"
    slide_language: str = "fa"

    @classmethod
    def from_dict(cls, data: dict) -> "BuildSettings":
        from app.i18n import resolve_slide_language
        from app.i18n.locale_detect import normalize as normalize_lang

        slide_lang = resolve_slide_language(data)
        ui_lang = normalize_lang(str(data.get("ui_language", "fa")))
        font_name = str(data.get("font_name", "B Nazanin"))
        if slide_lang == "en" and font_name in ("B Nazanin", ""):
            font_name = "Calibri"
        elif slide_lang == "fa" and font_name in ("Calibri", "Arial", ""):
            font_name = "B Nazanin"

        return cls(
            footer_text=str(data.get("footer_text", "")),
            logo_right=Path(data["logo_right"]) if data.get("logo_right") else None,
            logo_left=Path(data["logo_left"]) if data.get("logo_left") else None,
            output_folder_name=str(data.get("output_folder_name") or "Output_PPTX").strip() or "Output_PPTX",
            slide_width_inches=float(data.get("slide_width_inches", 13.33)),
            slide_height_inches=float(data.get("slide_height_inches", 7.5)),
            images_per_slide=max(1, min(4, int(data.get("images_per_slide", 4)))),
            jpeg_quality=max(40, min(95, int(data.get("jpeg_quality", 75)))),
            max_dimension=max(600, min(2400, int(data.get("max_dimension", 1200)))),
            font_name=str(data.get("font_name", "B Nazanin")),
            title_font_size=int(data.get("title_font_size", 22)),
            caption_font_size=int(data.get("caption_font_size", 11)),
            footer_font_size=int(data.get("footer_font_size", 12)),
            enable_section_dividers=bool(data.get("enable_section_dividers", True)),
            enable_image_zoom=bool(data.get("enable_image_zoom", True)),
            enable_hover_zoom=bool(data.get("enable_hover_zoom", True))
            and bool(data.get("enable_image_zoom", True)),
            enable_image_shadow=bool(data.get("enable_image_shadow", True)),
            enable_image_border=bool(data.get("enable_image_border", True)),
            caption_from_filename=bool(data.get("caption_from_filename", True)),
            ui_language=ui_lang,
            slide_language=slide_lang,
        )
