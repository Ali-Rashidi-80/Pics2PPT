"""Optional LibreOffice headless preview (PDF / PNG)."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PreviewResult:
    ok: bool
    skipped: bool
    message: str
    output_path: Path | None = None


def find_soffice() -> Path | None:
    """Locate LibreOffice ``soffice`` / ``soffice.exe`` on PATH or common install dirs."""
    for name in ("soffice", "soffice.exe"):
        found = shutil.which(name)
        if found:
            return Path(found)

    candidates = [
        Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
        Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
        Path("/usr/bin/soffice"),
        Path("/usr/lib/libreoffice/program/soffice"),
        Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"),
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def libreoffice_available() -> bool:
    return find_soffice() is not None


def export_preview(
    pptx_path: Path | str,
    *,
    fmt: str = "pdf",
    out_dir: Path | str | None = None,
    timeout_sec: int = 120,
) -> PreviewResult:
    """
    Convert PPTX to PDF or PNG via LibreOffice headless.

    ``fmt``: ``pdf`` or ``png`` (PNG exports first slide as image in some LO versions;
    PDF is the reliable default).
    """
    path = Path(pptx_path).resolve()
    if not path.is_file():
        return PreviewResult(ok=False, skipped=False, message=f"File not found: {path}")

    soffice = find_soffice()
    if soffice is None:
        return PreviewResult(
            ok=True,
            skipped=True,
            message="LibreOffice not found — preview skipped",
            output_path=None,
        )

    fmt_norm = (fmt or "pdf").lower().strip()
    if fmt_norm not in {"pdf", "png"}:
        fmt_norm = "pdf"

    dest_dir = Path(out_dir) if out_dir else path.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    # LibreOffice writes into --outdir using the source stem
    cmd = [
        str(soffice),
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--convert-to",
        fmt_norm,
        "--outdir",
        str(dest_dir),
        str(path),
    ]
    env = os.environ.copy()
    # Avoid user profile lock issues in concurrent/CI runs
    env.setdefault("SAL_USE_VCLPLUGIN", "svp")

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return PreviewResult(ok=False, skipped=False, message="LibreOffice conversion timed out")
    except OSError as exc:
        return PreviewResult(ok=True, skipped=True, message=f"LibreOffice skipped: {exc}")

    expected = dest_dir / f"{path.stem}.{fmt_norm}"
    if completed.returncode != 0 and not expected.is_file():
        err = (completed.stderr or completed.stdout or "").strip()[:300]
        return PreviewResult(
            ok=False,
            skipped=False,
            message=f"LibreOffice failed (code {completed.returncode}): {err or 'unknown error'}",
        )

    if not expected.is_file():
        # Some builds write slightly different names — pick newest matching suffix
        matches = sorted(dest_dir.glob(f"{path.stem}*.{fmt_norm}"), key=lambda p: p.stat().st_mtime, reverse=True)
        if matches:
            expected = matches[0]
        else:
            return PreviewResult(
                ok=False,
                skipped=False,
                message="LibreOffice finished but output file was not found",
            )

    return PreviewResult(
        ok=True,
        skipped=False,
        message=f"Preview exported: {expected.name}",
        output_path=expected,
    )
