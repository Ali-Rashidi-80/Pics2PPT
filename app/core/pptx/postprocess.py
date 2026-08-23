"""Optional Phase 4 post-build pipeline: plugins, COM, LibreOffice preview."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..models import PptxOutputSettings
from ..scanner import PresentationJob
from .com_postprocess import ComResult, com_postprocess_pptx
from .libreoffice_preview import PreviewResult, export_preview
from .plugins import (
    HOOK_AFTER_BUILD,
    HOOK_AFTER_VALIDATE,
    HOOK_BEFORE_BUILD,
    PluginRegistry,
    default_registry,
    load_plugins_from_dir,
)


@dataclass
class PostProcessResult:
    com: ComResult | None = None
    preview: PreviewResult | None = None
    plugin_warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "com": None
            if self.com is None
            else {
                "ok": self.com.ok,
                "skipped": self.com.skipped,
                "message": self.com.message,
            },
            "preview": None
            if self.preview is None
            else {
                "ok": self.preview.ok,
                "skipped": self.preview.skipped,
                "message": self.preview.message,
                "output": str(self.preview.output_path) if self.preview.output_path else None,
            },
            "plugin_warnings": list(self.plugin_warnings),
            "notes": list(self.notes),
        }


def run_before_build_hooks(
    job: PresentationJob,
    settings: PptxOutputSettings,
    *,
    registry: PluginRegistry | None = None,
) -> list[str]:
    if not bool(getattr(settings, "enable_plugins", False)):
        return []
    reg = registry or default_registry
    load_plugins_from_dir(registry=reg)
    return reg.run(HOOK_BEFORE_BUILD, job=job, settings=settings)


def run_post_build_pipeline(
    pptx_path: Path,
    job: PresentationJob,
    settings: PptxOutputSettings,
    *,
    validation: Any = None,
    registry: PluginRegistry | None = None,
) -> PostProcessResult:
    result = PostProcessResult()
    reg = registry or default_registry

    if bool(getattr(settings, "enable_plugins", False)):
        load_plugins_from_dir(registry=reg)
        result.plugin_warnings.extend(
            reg.run(HOOK_AFTER_BUILD, path=pptx_path, job=job, settings=settings)
        )
        if validation is not None:
            result.plugin_warnings.extend(
                reg.run(
                    HOOK_AFTER_VALIDATE,
                    path=pptx_path,
                    job=job,
                    settings=settings,
                    validation=validation,
                )
            )

    if bool(getattr(settings, "enable_com_postprocess", False)):
        result.com = com_postprocess_pptx(pptx_path)
        result.notes.append(result.com.message)

    if bool(getattr(settings, "enable_libreoffice_preview", False)):
        fmt = str(getattr(settings, "preview_format", "pdf") or "pdf")
        result.preview = export_preview(pptx_path, fmt=fmt)
        result.notes.append(result.preview.message)

    return result
