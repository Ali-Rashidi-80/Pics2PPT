"""Output path helpers for PPTX conflict handling and placement."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from .scanner import PresentationJob, scan_project_folders

ConflictMode = Literal["replace", "version"]
OutputPlacement = Literal["central", "per_folder"]


def resolve_output_path(base: Path, mode: ConflictMode) -> Path:
    """Return output path; in version mode pick the next free sibling name."""
    if mode == "replace" or not base.is_file():
        return base
    stem = base.stem
    suffix = base.suffix
    parent = base.parent
    n = 2
    while True:
        candidate = parent / f"{stem} ({n}){suffix}"
        if not candidate.is_file():
            return candidate
        n += 1


def planned_output_path(output_dir: Path, job_name: str, mode: ConflictMode) -> Path:
    return resolve_output_path(output_dir / f"{job_name}.pptx", mode)


def job_output_file(
    job: PresentationJob,
    root: Path,
    output_folder_name: str,
    placement: OutputPlacement,
) -> Path:
    """
    Target PPTX path for a job (before conflict versioning).

    central     → <root>/<Output_PPTX>/<job>.pptx
    per_folder  → <job.source>/<Output_PPTX>/<job>.pptx  (manual-style)
    """
    folder_name = (output_folder_name or "Output_PPTX").strip() or "Output_PPTX"
    if placement == "per_folder":
        return job.source / folder_name / f"{job.name}.pptx"
    return root / folder_name / f"{job.name}.pptx"


def find_existing_outputs(
    root: Path,
    output_folder_name: str,
    *,
    placement: OutputPlacement = "central",
    skip_dir_names: set[str] | None = None,
) -> list[Path]:
    """List PPTX files that would be overwritten in replace mode."""
    folder_name = (output_folder_name or "Output_PPTX").strip() or "Output_PPTX"
    skip = {folder_name, "Output_PPTX"}
    if skip_dir_names:
        skip.update(skip_dir_names)
    try:
        jobs = scan_project_folders(root, skip_dir_names=skip)
    except (NotADirectoryError, OSError):
        return []
    existing: list[Path] = []
    for job in jobs:
        path = job_output_file(job, root, folder_name, placement)
        if path.is_file():
            existing.append(path)
    return existing


def scan_jobs(root: Path, output_folder_name: str) -> list[PresentationJob]:
    folder_name = (output_folder_name or "Output_PPTX").strip() or "Output_PPTX"
    skip = {folder_name, "Output_PPTX"}
    return scan_project_folders(root, skip_dir_names=skip)
