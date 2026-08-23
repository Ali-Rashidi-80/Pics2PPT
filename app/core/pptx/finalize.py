"""Finalize a presentation before save — properties, sections, shared post-steps."""

from __future__ import annotations

from ..models import BuildSettings, PptxOutputSettings
from ..scanner import PresentationJob
from .openxml_ext import inject_p14_sections, sections_from_markers
from .properties import apply_core_properties


def finalize_presentation(
    prs,
    job: PresentationJob,
    settings: BuildSettings | PptxOutputSettings,
    *,
    path_used: str = "code",
    template_name: str | None = None,
    section_markers: list[tuple[str, int]] | None = None,
) -> dict:
    """Apply Phase 2 finishing touches. Returns stats for build report."""
    apply_core_properties(
        prs,
        job,
        settings,
        path_used=path_used,
        template_name=template_name,
    )

    enable_native = bool(getattr(settings, "enable_native_sections", True))
    sections_written = 0
    if enable_native and section_markers:
        ranges = sections_from_markers(section_markers, len(prs.slides))
        sections_written = inject_p14_sections(prs, ranges)

    return {
        "path_used": path_used,
        "template": template_name,
        "slide_count": len(prs.slides),
        "native_sections": sections_written,
        "groups": len(job.groups),
        "images": sum(len(g.images) for g in job.groups),
    }
