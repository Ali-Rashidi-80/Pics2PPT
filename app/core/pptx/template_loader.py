"""Template zip security guards and presentation loading (.pptx / .potx)."""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

from pptx import Presentation

from app.resources import asset_path

VALID_TEMPLATE_SUFFIXES = (".pptx", ".potx")

# G13 — zip / OOXML safety limits
MAX_TEMPLATE_BYTES = 50 * 1024 * 1024  # 50 MiB on disk
MAX_ZIP_MEMBERS = 4_000
MAX_UNCOMPRESSED_BYTES = 200 * 1024 * 1024  # 200 MiB inflated
MAX_COMPRESSION_RATIO = 100.0


def is_template_file(path: Path | str | None) -> bool:
    if not path:
        return False
    p = Path(path)
    return p.is_file() and p.suffix.lower() in VALID_TEMPLATE_SUFFIXES


def default_template_path() -> Path:
    return asset_path("assets", "templates", "Pics2PPT_Default.pptx")


def bundled_template_if_available() -> Path | None:
    path = default_template_path()
    return path if is_template_file(path) else None


def validate_template_zip(path: Path) -> None:
    """Reject zip bombs, path traversal, and oversized templates (G13)."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Template not found: {path}")
    size = path.stat().st_size
    if size <= 0:
        raise ValueError("Template file is empty")
    if size > MAX_TEMPLATE_BYTES:
        raise ValueError(f"Template exceeds size limit ({MAX_TEMPLATE_BYTES} bytes)")

    try:
        with zipfile.ZipFile(path, "r") as zf:
            infos = zf.infolist()
            if len(infos) > MAX_ZIP_MEMBERS:
                raise ValueError(f"Template has too many zip entries ({len(infos)})")
            uncompressed = 0
            for info in infos:
                name = info.filename.replace("\\", "/")
                if name.startswith("/") or name.startswith("\\") or ".." in name.split("/"):
                    raise ValueError(f"Unsafe zip path in template: {info.filename}")
                uncompressed += max(0, int(info.file_size))
                if info.compress_size > 0 and info.file_size / max(info.compress_size, 1) > MAX_COMPRESSION_RATIO:
                    if info.file_size > 8 * 1024 * 1024:
                        raise ValueError(f"Suspicious compression ratio for {info.filename}")
            if uncompressed > MAX_UNCOMPRESSED_BYTES:
                raise ValueError("Template uncompressed size exceeds safety limit")
            # Must look like OOXML presentation package
            names = {i.filename.replace("\\", "/") for i in infos}
            if "[Content_Types].xml" not in names:
                raise ValueError("Not a valid OOXML package (missing [Content_Types].xml)")
    except zipfile.BadZipFile as exc:
        raise ValueError("Template is not a valid zip/OOXML file") from exc


@dataclass(frozen=True)
class LoadedTemplate:
    path: Path
    presentation: Presentation
    layout_count: int


class TemplateLoader:
    """Loads designer templates for the Hybrid Smart template path."""

    def __init__(self, template_path: Path | str) -> None:
        self.template_path = Path(template_path)

    def validate(self) -> None:
        if not is_template_file(self.template_path):
            raise FileNotFoundError(f"Template not found or unsupported: {self.template_path}")
        validate_template_zip(self.template_path)

    def load(self) -> LoadedTemplate:
        self.validate()
        # python-pptx opens .pptx and .potx the same way (G32)
        prs = Presentation(str(self.template_path))
        return LoadedTemplate(
            path=self.template_path,
            presentation=prs,
            layout_count=len(prs.slide_layouts),
        )

    def analyze(self) -> list[dict]:
        from .template_analyzer import analyze_presentation

        loaded = self.load()
        return analyze_presentation(loaded.presentation)
