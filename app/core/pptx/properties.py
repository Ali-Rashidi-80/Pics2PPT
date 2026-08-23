"""Document core properties (+ light custom metadata via comments/keywords)."""

from __future__ import annotations

from datetime import datetime, timezone

from app import APP_NAME, __version__

from ..models import BuildSettings
from ..scanner import PresentationJob


def apply_core_properties(
    prs,
    job: PresentationJob,
    settings: BuildSettings,
    *,
    path_used: str = "code",
    template_name: str | None = None,
) -> None:
    cp = prs.core_properties
    title = (getattr(settings, "doc_title", None) or "").strip() or job.name
    author = (getattr(settings, "doc_author", None) or "").strip() or APP_NAME
    subject = (getattr(settings, "doc_subject", None) or "").strip() or (
        f"Photo report — {job.name}"
    )
    cp.title = title
    cp.author = author
    cp.subject = subject
    cp.category = (getattr(settings, "doc_category", None) or "").strip() or "Photo Report"
    keywords = ["Pics2PPT", "photo-report", path_used]
    if template_name:
        keywords.append(f"template:{template_name}")
    extra_kw = (getattr(settings, "doc_keywords", None) or "").strip()
    if extra_kw:
        keywords.append(extra_kw)
    cp.keywords = "; ".join(keywords)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cp.comments = (
        f"built_by={APP_NAME}; version={__version__}; path={path_used}; "
        f"built_at={now}; groups={len(job.groups)}; "
        f"images={sum(len(g.images) for g in job.groups)}"
    )
    try:
        cp.last_modified_by = APP_NAME
    except Exception:
        pass
