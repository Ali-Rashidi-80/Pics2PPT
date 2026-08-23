"""Code-path presentation builder (grid layout fallback)."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches

from app.i18n import set_build_slide_language, t_slide

from ..image_processor import get_image_size
from ..models import BuildSettings
from ..scanner import ImageGroup, PresentationJob
from .hyperlinks import link_shape_hover, link_shape_to_slide
from .layout_grid import cell_geometry
from .shapes import add_textbox, caption_for, compress_image, decorate_picture, fit_image_in_box
from .slide_detail import add_detail_slide
from .slide_header import draw_footer, draw_header
from .slide_index import add_index_slide
from .slide_section import add_section_divider
from .themes import muted_color


def _add_image_cell(
    slide,
    prs,
    blank,
    image_path: Path,
    cell_index: int,
    settings: BuildSettings,
    *,
    person_title: str,
    footer_text: str,
    logo_right,
    logo_left,
    slide_width,
    slide_height,
) -> None:
    title_box, image_box = cell_geometry(cell_index, slide_width, settings.images_per_slide)
    caption = caption_for(image_path, settings)
    if caption:
        add_textbox(
            slide,
            *title_box,
            caption,
            settings,
            size_pt=settings.caption_font_size,
            color=muted_color(settings),
            align=PP_ALIGN.CENTER,
        )

    buffer = compress_image(image_path, settings)
    w_px, h_px = get_image_size(
        image_path,
        auto_rotate=bool(getattr(settings, "enable_auto_rotate", True)),
    )
    left, top, width, height = fit_image_in_box(w_px, h_px, *image_box)
    pic = slide.shapes.add_picture(buffer, left, top, width, height)
    decorate_picture(pic, settings)

    if settings.enable_image_zoom:
        detail = add_detail_slide(
            prs,
            blank,
            image_path,
            settings,
            person_title=person_title,
            footer_text=footer_text,
            logo_right=logo_right,
            logo_left=logo_left,
            slide_width=slide_width,
            slide_height=slide_height,
            return_slide=slide,
        )
        link_shape_to_slide(pic, detail)
        if settings.enable_hover_zoom:
            link_shape_hover(pic, detail)


def _add_grid_slides(
    prs,
    blank,
    images,
    settings,
    *,
    title,
    subtitle,
    footer_text,
    logo_right,
    logo_left,
    slide_width,
    slide_height,
    should_cancel,
):
    per = max(1, min(4, settings.images_per_slide))
    for i in range(0, len(images), per):
        if should_cancel and should_cancel():
            raise InterruptedError(t_slide("pptx.err.cancelled"))
        chunk = images[i : i + per]
        slide = prs.slides.add_slide(blank)
        draw_header(slide, title, settings, logo_right, logo_left, slide_width, subtitle=subtitle)
        draw_footer(slide, footer_text, settings, slide_width)
        for cell_index, img_path in enumerate(chunk):
            if should_cancel and should_cancel():
                raise InterruptedError(t_slide("pptx.err.cancelled"))
            try:
                _add_image_cell(
                    slide,
                    prs,
                    blank,
                    img_path,
                    cell_index,
                    settings,
                    person_title=title,
                    footer_text=footer_text,
                    logo_right=logo_right,
                    logo_left=logo_left,
                    slide_width=slide_width,
                    slide_height=slide_height,
                )
            except Exception as exc:
                raise RuntimeError(t_slide("pptx.err.image", name=img_path.name, exc=exc)) from exc


def build_into_presentation(
    prs: Presentation,
    blank,
    job: PresentationJob,
    *,
    settings: BuildSettings | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> list[tuple[str, int]]:
    """Append section/grid/detail slides. Returns [(section_name, start_slide_index), ...]."""
    cfg = settings or BuildSettings()
    slide_width = prs.slide_width
    slide_height = prs.slide_height
    markers: list[tuple[str, int]] = []

    if bool(getattr(cfg, "enable_index_slide", False)) and job.groups:
        add_index_slide(prs, blank, job, cfg, slide_width=slide_width)

    use_sections = cfg.enable_section_dividers and job.grouped and len(job.groups) > 1
    section_total = len(job.groups)

    for section_index, group in enumerate(job.groups, start=1):
        if should_cancel and should_cancel():
            raise InterruptedError(t_slide("pptx.err.cancelled"))
        markers.append((group.name, len(prs.slides)))
        if use_sections:
            add_section_divider(
                prs,
                blank,
                cfg,
                person_title=job.name,
                section_name=group.name,
                section_index=section_index,
                section_total=section_total,
                footer_text=cfg.footer_text,
                logo_right=cfg.logo_right,
                logo_left=cfg.logo_left,
                slide_width=slide_width,
            )
            subtitle = group.name
        else:
            subtitle = None
        _add_grid_slides(
            prs,
            blank,
            group.images,
            cfg,
            title=job.name,
            subtitle=subtitle,
            footer_text=cfg.footer_text,
            logo_right=cfg.logo_right,
            logo_left=cfg.logo_left,
            slide_width=slide_width,
            slide_height=slide_height,
            should_cancel=should_cancel,
        )
    return markers


def build_from_job(
    job: PresentationJob,
    output_path: Path,
    *,
    settings: BuildSettings | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> Path:
    from .finalize import finalize_presentation

    cfg = settings or BuildSettings()
    set_build_slide_language(cfg.slide_language)
    prs = Presentation()
    slide_width = Inches(cfg.slide_width_inches)
    slide_height = Inches(cfg.slide_height_inches)
    prs.slide_width = slide_width
    prs.slide_height = slide_height
    blank = prs.slide_layouts[6]

    markers = build_into_presentation(prs, blank, job, settings=cfg, should_cancel=should_cancel)
    finalize_presentation(prs, job, cfg, path_used="code", section_markers=markers)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    return output_path


def build_presentation(
    images,
    output_path,
    *,
    title: str,
    settings: BuildSettings | None = None,
    should_cancel=None,
):
    job = PresentationJob(
        name=title,
        source=Path(output_path).parent,
        groups=[ImageGroup(name=title, images=list(images))],
        grouped=False,
    )
    cfg = settings or BuildSettings()
    return build_from_job(job, output_path, settings=cfg, should_cancel=should_cancel)
