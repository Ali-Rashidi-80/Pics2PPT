"""Layout constants and default colors for code-path PPTX generation."""

from pptx.dml.color import RGBColor
from pptx.util import Inches

TITLE_COLOR = RGBColor(0, 0, 0)
MUTED_COLOR = RGBColor(80, 80, 80)
ACCENT_COLOR = RGBColor(15, 61, 46)
BORDER_COLOR = RGBColor(180, 180, 180)

MARGIN_X = Inches(0.35)
GUTTER = Inches(0.25)
TITLE_BAND = Inches(0.35)
LOGO_SIZE = Inches(0.85)

HEADER_TOP = Inches(0.0)
HEADER_BOTTOM = Inches(1.2)
GRID_ROW1_TOP = Inches(1.2)
GRID_ROW1_BOTTOM = Inches(4.0)
GRID_ROW2_TOP = Inches(4.0)
GRID_ROW2_BOTTOM = Inches(6.8)
FOOTER_TOP = Inches(6.8)
FOOTER_BOTTOM = Inches(7.5)
