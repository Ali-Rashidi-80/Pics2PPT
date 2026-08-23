"""In-memory image compression with Pillow (+ EXIF rotate / captions)."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageOps


def read_exif_caption(image_path: Path | str) -> str:
    """Return a short caption from EXIF DateTimeOriginal / ImageDescription."""
    path = Path(image_path)
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return ""
            # 270 = ImageDescription, 36867 = DateTimeOriginal, 306 = DateTime
            for tag in (270, 36867, 306):
                val = exif.get(tag)
                if val:
                    text = str(val).strip()
                    if text:
                        return text[:200]
    except Exception:
        return ""
    return ""


def compress_image_to_bytes(
    image_path: Path | str,
    *,
    max_dimension: int = 1200,
    jpeg_quality: int = 75,
    auto_rotate: bool = True,
    strip_gps: bool = True,
) -> io.BytesIO:
    path = Path(image_path)
    with Image.open(path) as img:
        if auto_rotate:
            try:
                img = ImageOps.exif_transpose(img) or img
            except Exception:
                pass

        exif_bytes = None
        if not strip_gps:
            try:
                exif_bytes = img.info.get("exif")
            except Exception:
                exif_bytes = None

        if img.mode in ("RGBA", "P", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            alpha = img.split()[-1] if img.mode in ("RGBA", "LA") else None
            if alpha is not None:
                background.paste(img, mask=alpha)
            else:
                background.paste(img)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size
        if max(w, h) > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        save_kwargs: dict = {"format": "JPEG", "optimize": True, "quality": jpeg_quality}
        if exif_bytes and not strip_gps:
            save_kwargs["exif"] = exif_bytes
        img.save(buffer, **save_kwargs)
        buffer.seek(0)
        return buffer


def get_image_size(image_path: Path | str, *, auto_rotate: bool = True) -> tuple[int, int]:
    with Image.open(image_path) as img:
        if auto_rotate:
            try:
                img = ImageOps.exif_transpose(img) or img
            except Exception:
                pass
        return img.size
