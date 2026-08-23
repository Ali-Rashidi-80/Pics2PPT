"""Hybrid Smart orchestrator — routes auto / template / code output paths."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from app.i18n import t_slide

from ..models import BuildSettings, PptxOutputSettings
from ..scanner import PresentationJob
from .code_layout import build_from_job
from .postprocess import PostProcessResult, run_before_build_hooks, run_post_build_pipeline
from .template_layout import build_from_template
from .template_loader import bundled_template_if_available, is_template_file
from .validator import ValidationResult, validate_pptx, write_build_report


class BuildPath(str, Enum):
    CODE = "code"
    TEMPLATE = "template"


@dataclass(frozen=True)
class BuildResult:
    output_path: Path
    path_used: BuildPath
    template_path: Path | None = None
    report_path: Path | None = None
    validation: ValidationResult | None = None
    postprocess: PostProcessResult | None = None


def _as_pptx_settings(settings: BuildSettings | PptxOutputSettings | None) -> PptxOutputSettings:
    if settings is None:
        return PptxOutputSettings()
    if isinstance(settings, PptxOutputSettings):
        return settings
    # Legacy BuildSettings callers keep code-path behavior unless upgraded.
    return PptxOutputSettings.from_build_settings(settings, output_mode="code")


def resolve_template_file(settings: PptxOutputSettings) -> Path | None:
    """User template wins; otherwise bundled default when present."""
    user = settings.resolved_template_path()
    if user is not None:
        return user
    return bundled_template_if_available()


class HybridEngine:
    """Selects template vs code layout (Hybrid Smart)."""

    def resolve_path(self, settings: PptxOutputSettings) -> BuildPath:
        mode = settings.output_mode
        template = resolve_template_file(settings)
        if mode == "code":
            return BuildPath.CODE
        if mode == "template":
            if not template:
                raise FileNotFoundError(t_slide("pptx.err.template_required"))
            return BuildPath.TEMPLATE
        # auto
        if template and is_template_file(template):
            return BuildPath.TEMPLATE
        return BuildPath.CODE

    def build(
        self,
        job: PresentationJob,
        output_path: Path,
        *,
        settings: BuildSettings | PptxOutputSettings | None = None,
        should_cancel: Callable[[], bool] | None = None,
    ) -> BuildResult:
        cfg = _as_pptx_settings(settings)
        plugin_warnings = run_before_build_hooks(job, cfg)

        path_used = self.resolve_path(cfg)
        if path_used == BuildPath.TEMPLATE:
            tpl = resolve_template_file(cfg)
            if tpl is None:
                raise FileNotFoundError(t_slide("pptx.err.template_required"))
            out = build_from_template(
                job,
                output_path,
                tpl,
                settings=cfg,
                should_cancel=should_cancel,
            )
            result = BuildResult(output_path=out, path_used=BuildPath.TEMPLATE, template_path=tpl)
        else:
            out = build_from_job(job, output_path, settings=cfg, should_cancel=should_cancel)
            result = BuildResult(output_path=out, path_used=BuildPath.CODE, template_path=None)

        report_path = None
        validation = None
        if bool(getattr(cfg, "write_build_report", True)):
            validation = validate_pptx(result.output_path)
            if cfg.slide_language != "en" and not validation.metrics.get("has_rtl"):
                validation.warnings.append("RTL flag not detected in output XML")
            validation.warnings.extend(plugin_warnings)
            extra: dict[str, Any] = {
                "path_used": result.path_used.value,
                "job_name": job.name,
                "template": result.template_path.name if result.template_path else None,
                "groups": len(job.groups),
                "images": sum(len(g.images) for g in job.groups),
            }
            report_path = write_build_report(result.output_path, validation=validation, extra=extra)

        post = run_post_build_pipeline(
            result.output_path,
            job,
            cfg,
            validation=validation,
        )
        if report_path and report_path.is_file() and (post.notes or post.plugin_warnings):
            # Enrich report with Phase 4 notes when present
            try:
                import json

                payload = json.loads(report_path.read_text(encoding="utf-8"))
                payload["postprocess"] = post.to_dict()
                if post.plugin_warnings:
                    payload.setdefault("validation", {}).setdefault("warnings", []).extend(post.plugin_warnings)
                report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass

        return BuildResult(
            output_path=result.output_path,
            path_used=result.path_used,
            template_path=result.template_path,
            report_path=report_path,
            validation=validation,
            postprocess=post,
        )


_default_engine = HybridEngine()


def build_presentation_from_job(
    job: PresentationJob,
    output_path: Path,
    *,
    settings: BuildSettings | PptxOutputSettings | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> Path:
    return _default_engine.build(
        job,
        output_path,
        settings=settings,
        should_cancel=should_cancel,
    ).output_path
