"""Custom template import into the user templates library."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from .template_analyzer import analyze_template, format_analysis_report
from .template_loader import TemplateLoader, is_template_file, validate_template_zip


def user_templates_dir(base_dir: Path | None = None) -> Path:
    root = base_dir if base_dir is not None else Path.home() / ".pics2ppt"
    path = root / "templates"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w.\-]+", "_", name.strip(), flags=re.UNICODE)
    return cleaned[:120] or "template.pptx"


def import_template(
    source: Path | str,
    *,
    display_name: str | None = None,
    base_dir: Path | None = None,
) -> Path:
    """Validate and copy a template into ``~/.pics2ppt/templates/``."""
    src = Path(source)
    if not is_template_file(src):
        raise FileNotFoundError(f"Not a valid template file: {src}")
    validate_template_zip(src)

    suffix = src.suffix.lower() if src.suffix.lower() in {".pptx", ".potx"} else ".pptx"
    stem = _safe_filename(display_name or src.stem)
    if not stem.lower().endswith(suffix):
        dest_name = f"{stem}{suffix}"
    else:
        dest_name = stem
    dest = user_templates_dir(base_dir) / dest_name
    if dest.resolve() != src.resolve():
        shutil.copy2(src, dest)
    TemplateLoader(dest).validate()
    return dest


def layout_wizard_report(path: Path | str) -> str:
    """Analyze template and append suggested layout indices for Expert Panel."""
    rows = analyze_template(path)
    report = format_analysis_report(rows)
    blank_idx = None
    for row in rows:
        name = (row.get("name") or "").lower()
        if "blank" in name or "خالی" in name:
            blank_idx = row["index"]
            break
    if blank_idx is None and rows:
        blank_idx = rows[-1]["index"] if len(rows) > 6 else rows[0]["index"]
    suggestions = [
        "",
        "Suggested Expert Panel values:",
        f"  layout_index_grid = {blank_idx}",
        f"  layout_index_detail = {blank_idx}",
        f"  layout_index_divider = {blank_idx}",
    ]
    return report + "\n".join(suggestions)


def list_imported_templates(base_dir: Path | None = None) -> list[Path]:
    root = user_templates_dir(base_dir)
    files = []
    for path in sorted(root.iterdir()):
        if is_template_file(path):
            files.append(path)
    return files
