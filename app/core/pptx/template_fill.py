"""Run-safe template token replacement (G1) — never wipe placeholder .text."""

from __future__ import annotations

import re
from typing import Mapping

# Tokens like {{title}} or {{ footer }}
_TOKEN_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


def replace_tokens_in_text(text: str, mapping: Mapping[str, str]) -> str:
    def _sub(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in mapping:
            return str(mapping[key])
        return match.group(0)

    return _TOKEN_RE.sub(_sub, text)


def _paragraph_full_text(paragraph) -> str:
    return "".join(run.text for run in paragraph.runs)


def _replace_in_paragraph(paragraph, mapping: Mapping[str, str]) -> bool:
    """Replace tokens across runs without assigning paragraph.text / shape.text."""
    if not paragraph.runs:
        return False
    full = _paragraph_full_text(paragraph)
    if "{{" not in full:
        return False
    new_full = replace_tokens_in_text(full, mapping)
    if new_full == full:
        return False

    # PowerPoint often splits "{{title}}" across runs — rebuild into first run.
    first = paragraph.runs[0]
    first.text = new_full
    for run in paragraph.runs[1:]:
        run.text = ""
    return True


def fill_shape_tokens(shape, mapping: Mapping[str, str]) -> int:
    """Fill {{tokens}} in a shape's text frame. Returns number of paragraphs changed."""
    if not getattr(shape, "has_text_frame", False):
        return 0
    changed = 0
    for paragraph in shape.text_frame.paragraphs:
        if _replace_in_paragraph(paragraph, mapping):
            changed += 1
    return changed


def fill_slide_tokens(slide, mapping: Mapping[str, str]) -> int:
    total = 0
    for shape in slide.shapes:
        total += fill_shape_tokens(shape, mapping)
        if shape.has_table:
            table = shape.table
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.text_frame.paragraphs:
                        if _replace_in_paragraph(paragraph, mapping):
                            total += 1
    return total


def fill_presentation_tokens(prs, mapping: Mapping[str, str]) -> int:
    return sum(fill_slide_tokens(slide, mapping) for slide in prs.slides)


def job_token_map(*, title: str, footer: str = "", section: str = "", **extra: str) -> dict[str, str]:
    data = {
        "title": title,
        "footer": footer,
        "section": section,
        "job_name": title,
    }
    data.update({k: str(v) for k, v in extra.items()})
    return data
