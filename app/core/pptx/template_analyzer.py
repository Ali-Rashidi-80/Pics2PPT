"""Template layout analyzer — dump layout indices and placeholders (G2)."""

from __future__ import annotations

from pathlib import Path

from .template_loader import TemplateLoader


def analyze_presentation(prs) -> list[dict]:
    rows: list[dict] = []
    for index, layout in enumerate(prs.slide_layouts):
        placeholders = []
        for shape in layout.placeholders:
            try:
                pf = shape.placeholder_format
                placeholders.append(
                    {
                        "idx": int(pf.idx),
                        "type": str(pf.type),
                        "name": shape.name,
                    }
                )
            except (ValueError, AttributeError):
                placeholders.append({"idx": None, "type": "unknown", "name": shape.name})
        rows.append(
            {
                "index": index,
                "name": layout.name,
                "placeholder_count": len(placeholders),
                "placeholders": placeholders,
            }
        )
    return rows


def analyze_template(path: Path | str) -> list[dict]:
    return TemplateLoader(path).analyze()


def format_analysis_report(rows: list[dict]) -> str:
    lines = ["Template layout analysis", "=" * 40]
    for row in rows:
        lines.append(f"[{row['index']}] {row['name']} — {row['placeholder_count']} placeholder(s)")
        for ph in row["placeholders"]:
            lines.append(f"    idx={ph['idx']} type={ph['type']} name={ph['name']}")
    return "\n".join(lines)
