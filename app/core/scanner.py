"""Folder scanning and layout classification for PPTX jobs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.i18n import t_slide

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
IGNORE_NAMES = {"thumbs.db"}
IGNORE_EXTENSIONS = {".rar", ".zip"}
SKIP_DIR_NAMES = {"output_pptx"}


@dataclass
class ImageGroup:
    """One topical section inside a presentation."""

    name: str
    images: list[Path] = field(default_factory=list)


@dataclass
class PresentationJob:
    """One output PPTX file to build."""

    name: str
    source: Path
    groups: list[ImageGroup]
    grouped: bool  # True → section divider slides between topics


def is_valid_image(path: Path) -> bool:
    name = path.name.lower()
    if name in IGNORE_NAMES:
        return False
    if path.suffix.lower() in IGNORE_EXTENSIONS:
        return False
    if not path.is_file():
        return False
    return path.suffix.lower() in IMAGE_EXTENSIONS


def collect_images(folder: Path) -> list[Path]:
    images = [p for p in folder.iterdir() if is_valid_image(p)]
    images.sort(key=lambda p: p.name.lower())
    return images


def _iter_subdirs(folder: Path, skip_names: set[str] | None = None) -> list[Path]:
    skip = {n.lower() for n in (skip_names or SKIP_DIR_NAMES)}
    dirs = [
        p
        for p in folder.iterdir()
        if p.is_dir() and p.name.lower() not in skip
    ]
    dirs.sort(key=lambda p: p.name.lower())
    return dirs


def is_container(folder: Path, skip_names: set[str] | None = None) -> bool:
    """True if folder has at least one subdirectory that contains images."""
    return any(collect_images(child) for child in _iter_subdirs(folder, skip_names))


def make_flat_job(folder: Path) -> PresentationJob | None:
    images = collect_images(folder)
    if not images:
        return None
    return PresentationJob(
        name=folder.name,
        source=folder,
        groups=[ImageGroup(name=folder.name, images=images)],
        grouped=False,
    )


def _section_label(name: str) -> str:
    """Prettier labels for purely numeric group folders (1, 2, …)."""
    if name.isdigit():
        return t_slide("pptx.section.group_n", n=name)
    return name


def make_grouped_job(folder: Path, skip_names: set[str] | None = None) -> PresentationJob | None:
    """
    Build one PPTX job from a person/subject folder.

    - Direct images → section "General images" / overview (via t_slide)
    - Each image-bearing subdirectory → its own named section
    """
    groups: list[ImageGroup] = []

    own = collect_images(folder)
    topic_dirs = _iter_subdirs(folder, skip_names)
    has_topics = any(collect_images(d) for d in topic_dirs)

    if own and has_topics:
        groups.append(ImageGroup(name=t_slide("pptx.section.overview"), images=own))
    elif own and not has_topics:
        groups.append(ImageGroup(name=folder.name, images=own))

    for child in topic_dirs:
        child_imgs = collect_images(child)
        nested = [g for g in _iter_subdirs(child, skip_names) if collect_images(g)]

        if nested and not child_imgs:
            for g in nested:
                gimgs = collect_images(g)
                if gimgs:
                    groups.append(
                        ImageGroup(
                            name=f"{_section_label(child.name)} — {_section_label(g.name)}",
                            images=gimgs,
                        )
                    )
        elif child_imgs:
            groups.append(ImageGroup(name=_section_label(child.name), images=child_imgs))
            for g in nested:
                gimgs = collect_images(g)
                if gimgs:
                    groups.append(
                        ImageGroup(
                            name=f"{_section_label(child.name)} — {_section_label(g.name)}",
                            images=gimgs,
                        )
                    )

    if not groups:
        return None

    return PresentationJob(
        name=folder.name,
        source=folder,
        groups=groups,
        grouped=len(groups) > 1 or has_topics,
    )


def _is_numeric_folder(name: str) -> bool:
    return name.isdigit()


def scan_project_folders(root: Path, skip_dir_names: set[str] | None = None) -> list[PresentationJob]:
    """
    Classify the selected path into PPTX jobs.

    Patterns:
    1. Flat folder with images → one simple PPTX
    2. Person/subject folder with topic subfolders → one grouped PPTX
    3. Numbered group subfolders (e.g. FieldTrip/1, /2) → one grouped PPTX
    4. Project root with multiple first-level units → one PPTX per unit
    """
    root = Path(root)
    if not root.is_dir():
        raise NotADirectoryError(t_slide("scanner.err.invalid_path", path=root))

    skip = set(SKIP_DIR_NAMES)
    if skip_dir_names:
        skip.update(n.lower() for n in skip_dir_names)

    children = _iter_subdirs(root, skip)
    nested_containers = [c for c in children if is_container(c, skip)]
    leaf_topics = [c for c in children if collect_images(c) and not is_container(c, skip)]

    def _jobs_from_children() -> list[PresentationJob]:
        jobs: list[PresentationJob] = []
        for child in children:
            if is_container(child, skip):
                job = make_grouped_job(child, skip)
            elif collect_images(child):
                job = make_flat_job(child)
            else:
                job = None
            if job:
                jobs.append(job)
        return jobs

    # Project root: at least one nested person/group folder
    if nested_containers:
        return _jobs_from_children()

    # Project root of named flat units (e.g. Visit/A, Visit/B with images)
    # Keep all-numeric leaves as one grouped presentation (Pattern 3).
    if len(leaf_topics) >= 2 and not all(_is_numeric_folder(c.name) for c in leaf_topics):
        return _jobs_from_children()

    # Person / section folder selected directly (topics are leaf image folders)
    if leaf_topics:
        job = make_grouped_job(root, skip)
        return [job] if job else []

    # Single flat folder with images
    job = make_flat_job(root)
    return [job] if job else []


# Backwards-compatible alias used by older imports
def scan_as_simple_pairs(root: Path) -> list[tuple[Path, list[Path]]]:
    jobs = scan_project_folders(root)
    return [(j.source, [img for g in j.groups for img in g.images]) for j in jobs]
