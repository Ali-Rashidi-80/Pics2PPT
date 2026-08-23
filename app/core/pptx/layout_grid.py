"""Grid cell geometry for multi-image slides."""

from pptx.util import Emu

from .constants import GUTTER, GRID_ROW1_BOTTOM, GRID_ROW1_TOP, GRID_ROW2_BOTTOM, MARGIN_X, TITLE_BAND


def cell_geometry(index: int, slide_width, images_per_slide: int) -> tuple:
    slide_w = float(slide_width)
    margin = float(MARGIN_X)
    gutter = float(GUTTER)
    cols = 2 if images_per_slide > 1 else 1
    rows = max(1, (images_per_slide + cols - 1) // cols)
    usable_w = slide_w - 2 * margin - gutter * (cols - 1)
    cell_w = usable_w / cols

    col = index % cols
    row = index // cols

    body_top = float(GRID_ROW1_TOP)
    body_bottom = float(GRID_ROW2_BOTTOM if rows > 1 else GRID_ROW1_BOTTOM)
    body_h = body_bottom - body_top
    row_h = body_h / rows

    left = margin + col * (cell_w + gutter)
    band_top = body_top + row * row_h
    title_h = float(TITLE_BAND)
    title_box = (Emu(int(left)), Emu(int(band_top)), Emu(int(cell_w)), Emu(int(title_h)))
    img_top = band_top + title_h
    img_h = band_top + row_h - img_top
    image_box = (Emu(int(left)), Emu(int(img_top)), Emu(int(cell_w)), Emu(int(img_h)))
    return title_box, image_box
