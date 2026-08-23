"""PowerPoint builder — backward-compatible facade over HybridEngine."""

from __future__ import annotations

from .models import BuildSettings, PptxOutputSettings
from .pptx import build_presentation, build_presentation_from_job
from .scanner import ImageGroup, PresentationJob

__all__ = [
    "BuildSettings",
    "PptxOutputSettings",
    "build_presentation",
    "build_presentation_from_job",
    "PresentationJob",
    "ImageGroup",
]
