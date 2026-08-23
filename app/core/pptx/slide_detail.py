"""Full-size detail slide for click/hover zoom."""

from __future__ import annotations

from pathlib import Path

from pptx.enum.text import PP_ALIGN
from pptx.util import Emu

from ..image_processor import get_image_size
from ..models import BuildSettings
from .constants import FOOTER_TOP, HEADER_BOTTOM, MARGIN_X
from .hyperlinks import link_shape_to_slide
from .shapes import add_textbox, caption_for, compress_image, decorate_picture, fit_image_in_box
from .slide_header import draw_footer, draw_header
from .themes import muted_color


def add_detail_slide(
    prs,
    blank,
    image_path: Path,
    settings: BuildSettings,
    *,
    person_title: str,
    footer_text: str,
    logo_right,
    logo_left,
    slide_width,
    slide_height,
    return_slide=None,
):
    slide = prs.slides.add_slide(blank)
    caption = caption_for(image_path, settings)
    draw_header(slide, person_title, settings, logo_right, logo_left, slide_width)
    draw_footer(slide, footer_text, settings, slide_width)

    margin = float(MARGIN_X)
    top = float(HEADER_BOTTOM) + margin * 0.5
    bottom = float(FOOTER_TOP) - margin
    caption_band = 0.45 * 914400 if caption else 0
    box_left = margin
    box_w = float(slide_width) - 2 * margin
    box_h = bottom - top - caption_band

    buffer = compress_image(image_path, settings)
    w_px, h_px = get_image_size(
        image_path,
        auto_rotate=bool(getattr(settings, "enable_auto_rotate", True)),
    )
    left, top_e, width, height = fit_image_in_box(
        w_px, h_px, Emu(int(box_left)), Emu(int(top)), Emu(int(box_w)), Emu(int(box_h))
    )
    pic = slide.shapes.add_picture(buffer, left, top_e, width, height)
    decorate_picture(pic, settings)

    if caption:
        cap_top = top + box_h + 0.08 * 914400
        add_textbox(
            slide,
            Emu(int(box_left)),
            Emu(int(cap_top)),
            Emu(int(box_w)),
            Emu(int(caption_band)),
            caption,
            settings,
            size_pt=settings.caption_font_size,
            color=muted_color(settings),
            align=PP_ALIGN.CENTER,
        )

    if return_slide is not None:
        link_shape_to_slide(pic, return_slide)
    return slide
