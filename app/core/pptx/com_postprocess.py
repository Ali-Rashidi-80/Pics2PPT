"""Optional PowerPoint COM post-process (Windows + installed Office only)."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ComResult:
    ok: bool
    skipped: bool
    message: str
    output_path: Path | None = None


def powerpoint_available() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import win32com.client  # type: ignore  # noqa: F401

        return True
    except ImportError:
        return False


def com_postprocess_pptx(
    pptx_path: Path | str,
    *,
    save_as: Path | str | None = None,
    optimize_for_media: bool = False,
) -> ComResult:
    """
    Open and re-save a PPTX via PowerPoint automation.

    Useful for repairing links / applying Office-side normalization.
    Never required for core builds — opt-in only.
    """
    path = Path(pptx_path).resolve()
    if not path.is_file():
        return ComResult(ok=False, skipped=False, message=f"File not found: {path}")

    if sys.platform != "win32":
        return ComResult(ok=True, skipped=True, message="COM available only on Windows", output_path=path)

    try:
        import win32com.client  # type: ignore
    except ImportError:
        return ComResult(
            ok=True,
            skipped=True,
            message="pywin32 not installed — COM post-process skipped",
            output_path=path,
        )

    out = Path(save_as).resolve() if save_as else path
    app = None
    try:
        app = win32com.client.DispatchEx("PowerPoint.Application")
        app.Visible = 0
        # WithWindow=False
        presentation = app.Presentations.Open(str(path), WithWindow=False)
        try:
            if optimize_for_media:
                # Best-effort; older Office versions may ignore unknown flags
                try:
                    presentation.SaveAs(str(out))
                except Exception:
                    presentation.Save()
            elif out == path:
                presentation.Save()
            else:
                presentation.SaveAs(str(out))
        finally:
            presentation.Close()
        return ComResult(ok=True, skipped=False, message="COM post-process completed", output_path=out)
    except Exception as exc:
        # PowerPoint missing or automation blocked
        return ComResult(
            ok=True,
            skipped=True,
            message=f"COM skipped: {exc}",
            output_path=path,
        )
    finally:
        if app is not None:
            try:
                app.Quit()
            except Exception:
                pass
