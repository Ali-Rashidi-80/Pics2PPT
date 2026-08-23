"""Post-build PPTX validation and build_report.json (G14 / G30)."""

from __future__ import annotations

import json
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app import APP_NAME, __version__


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_pptx(path: Path | str) -> ValidationResult:
    path = Path(path)
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, Any] = {"path": str(path)}

    if not path.is_file():
        return ValidationResult(ok=False, errors=[f"File not found: {path}"], metrics=metrics)

    try:
        size = path.stat().st_size
        metrics["size_bytes"] = size
        if size <= 0:
            errors.append("Empty PPTX file")
    except OSError as exc:
        return ValidationResult(ok=False, errors=[str(exc)], metrics=metrics)

    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            metrics["zip_members"] = len(names)
            if "[Content_Types].xml" not in names:
                errors.append("Missing [Content_Types].xml")
            slide_files = [n for n in names if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
            metrics["slide_count"] = len(slide_files)
            if not slide_files:
                errors.append("No slides found in package")

            xml_blob = b""
            for n in names:
                if n.endswith(".xml"):
                    try:
                        xml_blob += zf.read(n)
                    except Exception:
                        warnings.append(f"Could not read {n}")

            metrics["has_rtl"] = b'rtl="1"' in xml_blob or b"rtl='1'" in xml_blob
            metrics["has_hlink_click"] = b"hlinkClick" in xml_blob or b"hlinksldjump" in xml_blob
            metrics["has_hlink_hover"] = b"hlinkHover" in xml_blob
            metrics["has_p14_sections"] = b"sectionLst" in xml_blob
            metrics["has_core_props"] = "docProps/core.xml" in names

            # Path traversal residual check
            for n in names:
                norm = n.replace("\\", "/")
                if norm.startswith("/") or ".." in norm.split("/"):
                    errors.append(f"Unsafe zip member path: {n}")

            # Optional openxml-audit (G30) — soft dependency
            try:
                import openxml_audit  # type: ignore

                audit_fn = getattr(openxml_audit, "audit", None) or getattr(openxml_audit, "validate", None)
                if callable(audit_fn):
                    audit_result = audit_fn(str(path))
                    metrics["openxml_audit"] = "ran"
                    if audit_result is False:
                        warnings.append("openxml-audit reported issues")
                    elif isinstance(audit_result, dict) and audit_result.get("errors"):
                        warnings.append(f"openxml-audit: {audit_result.get('errors')}")
                else:
                    metrics["openxml_audit"] = "api_unavailable"
            except ImportError:
                metrics["openxml_audit"] = "not_installed"
            except Exception as exc:
                warnings.append(f"openxml-audit failed: {exc}")
                metrics["openxml_audit"] = "error"

    except zipfile.BadZipFile:
        errors.append("Not a valid ZIP/OOXML package")
    except Exception as exc:
        errors.append(str(exc))

    # Soft a11y baseline (G17): warn if no RTL on Persian builds is checked by caller
    return ValidationResult(ok=not errors, errors=errors, warnings=warnings, metrics=metrics)


def write_build_report(
    pptx_path: Path | str,
    *,
    validation: ValidationResult,
    extra: dict[str, Any] | None = None,
) -> Path:
    pptx_path = Path(pptx_path)
    report_path = pptx_path.with_name(pptx_path.stem + "_build_report.json")
    payload: dict[str, Any] = {
        "app": APP_NAME,
        "version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pptx": pptx_path.name,
        "validation": validation.to_dict(),
    }
    if extra:
        payload["build"] = extra
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path
