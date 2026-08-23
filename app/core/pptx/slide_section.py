"""Section divider slides between topic groups."""

from pptx.enum.text import PP_ALIGN
from pptx.util import Emu

from app.i18n import t_slide

from .constants import MARGIN_X
from .shapes import add_textbox
from .slide_header import draw_footer, draw_header
from .themes import accent_color, muted_color


def add_section_divider(
    prs,
    blank,
    settings,
    *,
    person_title,
    section_name,
    section_index,
    section_total,
    footer_text,
    logo_right,
    logo_left,
    slide_width,
):
    slide = prs.slides.add_slide(blank)
    draw_header(slide, person_title, settings, logo_right, logo_left, slide_width)
    draw_footer(slide, footer_text, settings, slide_width)
    add_textbox(
        slide,
        MARGIN_X,
        Emu(int(2.6 * 914400)),
        Emu(int(float(slide_width) - 2 * float(MARGIN_X))),
        Emu(int(0.5 * 914400)),
        t_slide("pptx.section.n_of_m", n=section_index, m=section_total),
        settings,
        size_pt=14,
        color=muted_color(settings),
        align=PP_ALIGN.CENTER,
    )
    add_textbox(
        slide,
        MARGIN_X,
        Emu(int(3.2 * 914400)),
        Emu(int(float(slide_width) - 2 * float(MARGIN_X))),
        Emu(int(1.2 * 914400)),
        section_name,
        settings,
        size_pt=32,
        bold=True,
        color=accent_color(settings),
        align=PP_ALIGN.CENTER,
    )
