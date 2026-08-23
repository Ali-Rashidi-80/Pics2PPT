"""In-memory image compression with Pillow."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image


def compress_image_to_bytes(
    image_path: Path | str,
    *,
    max_dimension: int = 1200,
    jpeg_quality: int = 75,
) -> io.BytesIO:
    path = Path(image_path)
    with Image.open(path) as img:
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
        img.save(buffer, format="JPEG", optimize=True, quality=jpeg_quality)
        buffer.seek(0)
        return buffer


def get_image_size(image_path: Path | str) -> tuple[int, int]:
    with Image.open(image_path) as img:
        return img.size
