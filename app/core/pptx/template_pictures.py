"""PicturePlaceholder insert + crop fit/fill/native (G3)."""

from __future__ import annotations

from pathlib import Path

from pptx.enum.shapes import PP_PLACEHOLDER

from ..image_processor import get_image_size
from ..models import BuildSettings
from .shapes import compress_image, decorate_picture, fit_image_in_box

VALID_IMAGE_FIT = frozenset({"fill", "fit", "native"})


def _crop_for_fill(img_w: int, img_h: int, box_w: float, box_h: float) -> tuple[float, float, float, float]:
    """Return crop_left, crop_top, crop_right, crop_bottom as fractions 0–1."""
    if img_w <= 0 or img_h <= 0 or box_w <= 0 or box_h <= 0:
        return 0.0, 0.0, 0.0, 0.0
    img_ratio = img_w / img_h
    box_ratio = box_w / box_h
    if img_ratio > box_ratio:
        visible = box_ratio / img_ratio
        side = (1.0 - visible) / 2.0
        return side, 0.0, side, 0.0
    if img_ratio < box_ratio:
        visible = img_ratio / box_ratio
        side = (1.0 - visible) / 2.0
        return 0.0, side, 0.0, side
    return 0.0, 0.0, 0.0, 0.0


def insert_picture_into_placeholder(
    placeholder,
    image_path: Path,
    settings: BuildSettings,
    *,
    image_fit: str = "fit",
):
    """Insert image into a PicturePlaceholder with crop mode."""
    fit = image_fit if image_fit in VALID_IMAGE_FIT else "fit"
    buffer = compress_image(image_path, settings)
    pic = placeholder.insert_picture(buffer)

    if fit == "native":
        decorate_picture(pic, settings)
        return pic

    try:
        w_px, h_px = get_image_size(image_path)
    except Exception:
        decorate_picture(pic, settings)
        return pic

    box_w = float(pic.width)
    box_h = float(pic.height)

    if fit == "fill":
        left, top, right, bottom = _crop_for_fill(w_px, h_px, box_w, box_h)
        pic.crop_left = left
        pic.crop_top = top
        pic.crop_right = right
        pic.crop_bottom = bottom
    else:
        pic.crop_left = pic.crop_top = pic.crop_right = pic.crop_bottom = 0.0
        left, top, width, height = fit_image_in_box(
            w_px, h_px, pic.left, pic.top, pic.width, pic.height
        )
        pic.left, pic.top, pic.width, pic.height = left, top, width, height

    decorate_picture(pic, settings)
    return pic


def find_picture_placeholders(slide) -> list:
    found = []
    for shape in slide.placeholders:
        try:
            if shape.placeholder_format.type == PP_PLACEHOLDER.PICTURE:
                found.append(shape)
        except (ValueError, AttributeError):
            continue
    return found


def try_fill_picture_placeholders(
    slide,
    image_paths: list[Path],
    settings: BuildSettings,
    *,
    image_fit: str = "fit",
) -> list[Path]:
    """Fill picture placeholders in order. Returns remaining unplaced image paths."""
    placeholders = find_picture_placeholders(slide)
    remaining = list(image_paths)
    for ph in placeholders:
        if not remaining:
            break
        path = remaining.pop(0)
        insert_picture_into_placeholder(ph, path, settings, image_fit=image_fit)
    return remaining
