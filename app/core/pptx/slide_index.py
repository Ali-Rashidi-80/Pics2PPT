"""Optional table-of-contents / index slide (Phase 3)."""

from __future__ import annotations

from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

from app.i18n import t_slide

from ..models import BuildSettings
from ..scanner import PresentationJob
from .shapes import add_textbox
from .slide_header import draw_footer, draw_header
from .themes import accent_color, muted_color, title_color


def add_index_slide(
    prs,
    blank,
    job: PresentationJob,
    settings: BuildSettings,
    *,
    slide_width,
) -> None:
    """Add a simple two-column table listing sections and image counts."""
    slide = prs.slides.add_slide(blank)
    draw_header(slide, job.name, settings, settings.logo_right, settings.logo_left, slide_width)
    draw_footer(slide, settings.footer_text, settings, slide_width)

    title = t_slide("pptx.index.title")
    add_textbox(
        slide,
        Inches(0.5),
        Inches(1.35),
        Emu(int(float(slide_width) - Inches(1.0))),
        Inches(0.45),
        title,
        settings,
        size_pt=max(14, settings.title_font_size - 4),
        bold=True,
        color=accent_color(settings),
        align=PP_ALIGN.CENTER,
    )

    rows = max(1, len(job.groups) + 1)
    cols = 2
    table_width = float(slide_width) - float(Inches(1.2))
    table_height = min(4.5 * 914400, 0.42 * 914400 * rows)
    left = Inches(0.6)
    top = Inches(1.95)
    shape = slide.shapes.add_table(rows, cols, left, top, Emu(int(table_width)), Emu(int(table_height)))
    table = shape.table
    table.columns[0].width = Emu(int(table_width * 0.72))
    table.columns[1].width = Emu(int(table_width * 0.28))

    headers = (t_slide("pptx.index.col.section"), t_slide("pptx.index.col.count"))
    for col, text in enumerate(headers):
        cell = table.cell(0, col)
        cell.text = text
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.bold = True
            paragraph.font.size = Pt(12)
            paragraph.font.color.rgb = title_color(settings)
            paragraph.font.name = settings.font_name

    for i, group in enumerate(job.groups, start=1):
        table.cell(i, 0).text = group.name
        table.cell(i, 1).text = str(len(group.images))
        for col in (0, 1):
            for paragraph in table.cell(i, col).text_frame.paragraphs:
                paragraph.font.size = Pt(11)
                paragraph.font.color.rgb = muted_color(settings)
                paragraph.font.name = settings.font_name
