"""RTL scrollbar mirroring for scroll areas."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractScrollArea, QScrollArea, QWidget


def apply_layout_direction(root: QWidget, rtl: bool = True) -> None:
    direction = Qt.RightToLeft if rtl else Qt.LeftToRight
    root.setLayoutDirection(direction)
    for area in root.findChildren(QAbstractScrollArea):
        area.setLayoutDirection(direction)
        if isinstance(area, QScrollArea):
            bar = area.verticalScrollBar()
            if bar is not None:
                bar.setLayoutDirection(direction)
