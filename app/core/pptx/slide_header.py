"""Slide header and footer drawing."""

from pptx.enum.text import PP_ALIGN
from pptx.util import Emu

from ..models import BuildSettings
from .constants import FOOTER_BOTTOM, FOOTER_TOP, GUTTER, HEADER_BOTTOM, HEADER_TOP, LOGO_SIZE, MARGIN_X
from .shapes import add_logo, add_textbox
from .themes import muted_color


def header_title_box(slide_width):
    title_left = Emu(int(float(MARGIN_X) + float(LOGO_SIZE) + float(GUTTER)))
    title_width = Emu(int(float(slide_width) - 2 * (float(MARGIN_X) + float(LOGO_SIZE) + float(GUTTER))))
    return title_left, title_width


def draw_header(
    slide,
    title: str,
    settings: BuildSettings,
    logo_right,
    logo_left,
    slide_width,
    *,
    subtitle: str | None = None,
) -> None:
    header_h = float(HEADER_BOTTOM) - float(HEADER_TOP)
    logo_top = Emu(int(float(HEADER_TOP) + (header_h - float(LOGO_SIZE)) / 2))
    add_logo(slide, logo_right, Emu(int(float(slide_width) - float(MARGIN_X) - float(LOGO_SIZE))), logo_top, settings)
    add_logo(slide, logo_left, MARGIN_X, logo_top, settings)
    title_left, title_width = header_title_box(slide_width)
    if subtitle:
        add_textbox(
            slide,
            title_left,
            Emu(int(float(HEADER_TOP) + 0.12 * 914400)),
            title_width,
            Emu(int(0.45 * 914400)),
            title,
            settings,
            size_pt=settings.title_font_size - 4,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_textbox(
            slide,
            title_left,
            Emu(int(float(HEADER_TOP) + 0.55 * 914400)),
            title_width,
            Emu(int(0.4 * 914400)),
            subtitle,
            settings,
            size_pt=13,
            color=muted_color(settings),
            align=PP_ALIGN.CENTER,
        )
    else:
        add_textbox(
            slide,
            title_left,
            Emu(int(float(HEADER_TOP) + 0.25 * 914400)),
            title_width,
            Emu(int(0.7 * 914400)),
            title,
            settings,
            size_pt=settings.title_font_size,
            bold=True,
            align=PP_ALIGN.CENTER,
        )


def draw_footer(slide, footer_text: str, settings: BuildSettings, slide_width) -> None:
    if not footer_text.strip():
        return
    footer_h = float(FOOTER_BOTTOM) - float(FOOTER_TOP)
    add_textbox(
        slide,
        MARGIN_X,
        FOOTER_TOP,
        Emu(int(float(slide_width) - 2 * float(MARGIN_X))),
        Emu(int(footer_h)),
        footer_text,
        settings,
        size_pt=settings.footer_font_size,
        color=muted_color(settings),
        align=PP_ALIGN.CENTER,
    )
