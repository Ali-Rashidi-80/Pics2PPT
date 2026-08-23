"""Text boxes, pictures, logos, and image fitting."""

from __future__ import annotations

from pathlib import Path

from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Emu, Pt

from ..image_processor import compress_image_to_bytes, get_image_size
from ..models import BuildSettings
from .constants import LOGO_SIZE
from .themes import border_color, title_color


def set_rtl(paragraph, *, rtl: bool = True) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    if rtl:
        pPr.set("rtl", "1")
    elif pPr.get("rtl") is not None:
        del pPr.attrib["rtl"]


def paragraph_rtl(settings: BuildSettings) -> bool:
    return settings.slide_language != "en"


def style_run(
    run,
    settings: BuildSettings,
    *,
    size_pt: float,
    bold: bool = False,
    color: RGBColor | None = None,
) -> None:
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.color.rgb = color if color is not None else title_color(settings)
    run.font.name = settings.font_name
    rPr = run._r.get_or_add_rPr()
    existing_cs = rPr.find(qn("a:cs"))
    if existing_cs is not None:
        rPr.remove(existing_cs)
    cs = OxmlElement("a:cs")
    cs.set("typeface", settings.font_name)
    rPr.append(cs)


def add_textbox(
    slide,
    left,
    top,
    width,
    height,
    text: str,
    settings: BuildSettings,
    *,
    size_pt: float,
    bold: bool = False,
    color: RGBColor | None = None,
    align=None,
):
    rtl = paragraph_rtl(settings)
    if align is None:
        align = PP_ALIGN.RIGHT if rtl else PP_ALIGN.LEFT
    shape = slide.shapes.add_textbox(left, top, width, height)
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    set_rtl(p, rtl=rtl)
    run = p.add_run()
    run.text = text
    style_run(run, settings, size_pt=size_pt, bold=bold, color=color)
    return shape


def fit_image_in_box(img_w, img_h, box_left, box_top, box_width, box_height) -> tuple:
    box_w = float(box_width)
    box_h = float(box_height)
    if img_w <= 0 or img_h <= 0:
        return box_left, box_top, box_width, box_height
    img_ratio = img_w / img_h
    box_ratio = box_w / box_h
    if img_ratio >= box_ratio:
        final_w, final_h = box_w, box_w / img_ratio
    else:
        final_h, final_w = box_h, box_h * img_ratio
    left = float(box_left) + (box_w - final_w) / 2
    top = float(box_top) + (box_h - final_h) / 2
    return Emu(int(left)), Emu(int(top)), Emu(int(final_w)), Emu(int(final_h))


def decorate_picture(pic, settings: BuildSettings) -> None:
    if settings.enable_image_border:
        pic.line.color.rgb = border_color(settings)
        pic.line.width = Pt(0.75)
    if settings.enable_image_shadow:
        try:
            from .openxml_ext import apply_outer_shadow

            apply_outer_shadow(pic)
        except Exception:
            pic.shadow.inherit = False


def compress_image(image_path: Path, settings: BuildSettings):
    return compress_image_to_bytes(
        image_path,
        max_dimension=settings.max_dimension,
        jpeg_quality=settings.jpeg_quality,
        auto_rotate=bool(getattr(settings, "enable_auto_rotate", True)),
        strip_gps=bool(getattr(settings, "strip_gps", True)),
    )


def add_logo(slide, path: Path | None, left, top, settings: BuildSettings, size=LOGO_SIZE) -> None:
    if path is None or not Path(path).is_file():
        return
    try:
        buffer = compress_image(path, settings)
        w_px, h_px = get_image_size(
            path,
            auto_rotate=bool(getattr(settings, "enable_auto_rotate", True)),
        )
        left_f, top_f, w_f, h_f = fit_image_in_box(w_px, h_px, left, top, size, size)
        slide.shapes.add_picture(buffer, left_f, top_f, w_f, h_f)
    except Exception:
        pass


def caption_for(image_path: Path, settings: BuildSettings) -> str:
    source = str(getattr(settings, "caption_source", "filename") or "filename")
    if source == "none":
        return ""
    from ..image_processor import read_exif_caption

    filename_cap = image_path.stem if settings.caption_from_filename else ""
    if source == "filename":
        return filename_cap
    exif_cap = read_exif_caption(image_path)
    if source == "exif":
        return exif_cap
    if source == "both":
        if filename_cap and exif_cap:
            return f"{filename_cap} — {exif_cap}"
        return filename_cap or exif_cap
    return filename_cap
