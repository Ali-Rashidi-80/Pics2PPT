"""Shared data models for PPTX generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

VALID_OUTPUT_MODES = frozenset({"auto", "template", "code"})


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

    # Phase 2 image / EXIF pipeline
    enable_auto_rotate: bool = True
    strip_gps: bool = True
    caption_source: str = "filename"  # filename | exif | both | none

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

        caption_source = str(data.get("caption_source", "filename"))
        if caption_source not in {"filename", "exif", "both", "none"}:
            caption_source = "filename"

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
            enable_auto_rotate=bool(data.get("enable_auto_rotate", True)),
            strip_gps=bool(data.get("strip_gps", True)),
            caption_source=caption_source,
            ui_language=ui_lang,
            slide_language=slide_lang,
        )


@dataclass
class PptxOutputSettings(BuildSettings):
    output_mode: str = "auto"
    template_path: Path | None = None
    slide_size_preset: str = "widescreen_16_9"
    image_fit: str = "fit"  # fill | fit | native
    layout_index_grid: int | None = None
    layout_index_detail: int | None = None
    layout_index_divider: int | None = None
    enable_native_sections: bool = True
    write_build_report: bool = True
    enable_index_slide: bool = False
    active_preset: str = ""
    enable_com_postprocess: bool = False
    enable_libreoffice_preview: bool = False
    enable_plugins: bool = False
    preview_format: str = "pdf"  # pdf | png
    doc_title: str = ""
    doc_author: str = ""
    doc_subject: str = ""
    doc_category: str = ""
    doc_keywords: str = ""
    color_title: str = "000000"
    color_muted: str = "505050"
    color_accent: str = "0F3D2E"
    color_border: str = "B4B4B4"
    color_background: str = "FFFFFF"

    @classmethod
    def from_build_settings(cls, settings: BuildSettings, **overrides) -> "PptxOutputSettings":
        data = {
            "footer_text": settings.footer_text,
            "logo_right": str(settings.logo_right) if settings.logo_right else "",
            "logo_left": str(settings.logo_left) if settings.logo_left else "",
            "output_folder_name": settings.output_folder_name,
            "slide_width_inches": settings.slide_width_inches,
            "slide_height_inches": settings.slide_height_inches,
            "images_per_slide": settings.images_per_slide,
            "jpeg_quality": settings.jpeg_quality,
            "max_dimension": settings.max_dimension,
            "font_name": settings.font_name,
            "title_font_size": settings.title_font_size,
            "caption_font_size": settings.caption_font_size,
            "footer_font_size": settings.footer_font_size,
            "enable_section_dividers": settings.enable_section_dividers,
            "enable_image_zoom": settings.enable_image_zoom,
            "enable_hover_zoom": settings.enable_hover_zoom,
            "enable_image_shadow": settings.enable_image_shadow,
            "enable_image_border": settings.enable_image_border,
            "caption_from_filename": settings.caption_from_filename,
            "enable_auto_rotate": settings.enable_auto_rotate,
            "strip_gps": settings.strip_gps,
            "caption_source": settings.caption_source,
            "ui_language": settings.ui_language,
            "slide_language_mode": "fixed",
            "slide_language": settings.slide_language,
        }
        data.update(overrides)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "PptxOutputSettings":
        base = BuildSettings.from_dict(data)
        output_mode = str(data.get("output_mode", "auto"))
        if output_mode not in VALID_OUTPUT_MODES:
            output_mode = "auto"
        tpl_raw = str(data.get("template_path") or "").strip()
        template_path = Path(tpl_raw) if tpl_raw else None
        slide_size_preset = str(data.get("slide_size_preset", "widescreen_16_9"))
        from app.core.pptx.slide_sizes import VALID_SLIDE_SIZE_PRESETS
        from app.core.pptx.template_pictures import VALID_IMAGE_FIT
        from app.core.pptx.themes import DEFAULT_HEX, normalize_hex

        if slide_size_preset not in VALID_SLIDE_SIZE_PRESETS:
            slide_size_preset = "widescreen_16_9"
        image_fit = str(data.get("image_fit", "fit"))
        if image_fit not in VALID_IMAGE_FIT:
            image_fit = "fit"

        def _opt_int(key: str) -> int | None:
            raw = data.get(key)
            if raw is None or raw == "":
                return None
            try:
                return int(raw)
            except (TypeError, ValueError):
                return None

        return cls(
            footer_text=base.footer_text,
            logo_right=base.logo_right,
            logo_left=base.logo_left,
            output_folder_name=base.output_folder_name,
            slide_width_inches=base.slide_width_inches,
            slide_height_inches=base.slide_height_inches,
            images_per_slide=base.images_per_slide,
            jpeg_quality=base.jpeg_quality,
            max_dimension=base.max_dimension,
            font_name=base.font_name,
            title_font_size=base.title_font_size,
            caption_font_size=base.caption_font_size,
            footer_font_size=base.footer_font_size,
            enable_section_dividers=base.enable_section_dividers,
            enable_image_zoom=base.enable_image_zoom,
            enable_hover_zoom=base.enable_hover_zoom,
            enable_image_shadow=base.enable_image_shadow,
            enable_image_border=base.enable_image_border,
            caption_from_filename=base.caption_from_filename,
            enable_auto_rotate=base.enable_auto_rotate,
            strip_gps=base.strip_gps,
            caption_source=base.caption_source,
            ui_language=base.ui_language,
            slide_language=base.slide_language,
            output_mode=output_mode,
            template_path=template_path,
            slide_size_preset=slide_size_preset,
            image_fit=image_fit,
            layout_index_grid=_opt_int("layout_index_grid"),
            layout_index_detail=_opt_int("layout_index_detail"),
            layout_index_divider=_opt_int("layout_index_divider"),
            enable_native_sections=bool(data.get("enable_native_sections", True)),
            write_build_report=bool(data.get("write_build_report", True)),
            enable_index_slide=bool(data.get("enable_index_slide", False)),
            active_preset=str(data.get("active_preset", "")),
            enable_com_postprocess=bool(data.get("enable_com_postprocess", False)),
            enable_libreoffice_preview=bool(data.get("enable_libreoffice_preview", False)),
            enable_plugins=bool(data.get("enable_plugins", False)),
            preview_format=(
                str(data.get("preview_format", "pdf")).lower()
                if str(data.get("preview_format", "pdf")).lower() in {"pdf", "png"}
                else "pdf"
            ),
            doc_title=str(data.get("doc_title", "")),
            doc_author=str(data.get("doc_author", "")),
            doc_subject=str(data.get("doc_subject", "")),
            doc_category=str(data.get("doc_category", "")),
            doc_keywords=str(data.get("doc_keywords", "")),
            color_title=normalize_hex(str(data.get("color_title", "")), DEFAULT_HEX["color_title"]),
            color_muted=normalize_hex(str(data.get("color_muted", "")), DEFAULT_HEX["color_muted"]),
            color_accent=normalize_hex(str(data.get("color_accent", "")), DEFAULT_HEX["color_accent"]),
            color_border=normalize_hex(str(data.get("color_border", "")), DEFAULT_HEX["color_border"]),
            color_background=normalize_hex(str(data.get("color_background", "")), DEFAULT_HEX["color_background"]),
        )

    def resolved_template_path(self) -> Path | None:
        if self.template_path is None:
            return None
        path = Path(self.template_path)
        if not path.is_file():
            return None
        if path.suffix.lower() not in {".pptx", ".potx"}:
            return None
        return path

