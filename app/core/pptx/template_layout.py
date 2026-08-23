"""Build PPTX content onto a loaded template (theme/masters preserved)."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from pptx.slide import SlideLayout

from app.i18n import set_build_slide_language

from ..models import BuildSettings, PptxOutputSettings
from ..scanner import PresentationJob
from .code_layout import build_into_presentation
from .finalize import finalize_presentation
from .template_fill import fill_presentation_tokens, job_token_map
from .template_loader import TemplateLoader


def _pick_blank_layout(prs, preferred_index: int | None = None) -> SlideLayout:
    layouts = list(prs.slide_layouts)
    if not layouts:
        raise RuntimeError("Template has no slide layouts")
    if preferred_index is not None and 0 <= preferred_index < len(layouts):
        return layouts[preferred_index]
    # Prefer true blank / empty name layouts
    for layout in layouts:
        name = (layout.name or "").lower()
        if "blank" in name or "خالی" in name:
            return layout
    # Fall back to last layout (often blank in Office themes) then first
    if len(layouts) > 6:
        return layouts[6]
    return layouts[-1]


def build_from_template(
    job: PresentationJob,
    output_path: Path,
    template_path: Path,
    *,
    settings: BuildSettings | PptxOutputSettings | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> Path:
    cfg = settings or PptxOutputSettings()
    set_build_slide_language(cfg.slide_language)

    loaded = TemplateLoader(template_path).load()
    prs = loaded.presentation

    layout_idx = None
    if isinstance(cfg, PptxOutputSettings):
        layout_idx = cfg.layout_index_grid
    blank = _pick_blank_layout(prs, layout_idx)

    # Fill designer tokens on existing template slides (cover / branding)
    tokens = job_token_map(title=job.name, footer=cfg.footer_text or "")
    fill_presentation_tokens(prs, tokens)

    markers = build_into_presentation(
        prs,
        blank,
        job,
        settings=cfg,
        should_cancel=should_cancel,
    )

    # Re-fill so tokens on newly added text (if any) and cover stay consistent
    fill_presentation_tokens(prs, tokens)

    finalize_presentation(
        prs,
        job,
        cfg,
        path_used="template",
        template_name=Path(template_path).name,
        section_markers=markers,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    return output_path
