"""RTL/LTR-aware scroll areas and responsive page helpers."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QSizePolicy, QVBoxLayout, QWidget


class RtlScrollArea(QScrollArea):
    """Scroll area with direction-aware content (RTL or LTR)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("RtlScrollArea")
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._rtl = True
        self.apply_direction(True)

    def apply_direction(self, rtl: bool) -> None:
        self._rtl = rtl
        if rtl:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.viewport().setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            direction = Qt.LayoutDirection.LeftToRight
            self.setLayoutDirection(direction)
            self.viewport().setLayoutDirection(direction)
        bar = self.verticalScrollBar()
        if bar is not None:
            bar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def setWidget(self, widget: QWidget | None) -> None:  # noqa: N802 — Qt API
        if widget is not None:
            widget.setLayoutDirection(
                Qt.LayoutDirection.RightToLeft if self._rtl else Qt.LayoutDirection.LeftToRight
            )
            widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        super().setWidget(widget)
        self.apply_direction(self._rtl)

    def resizeEvent(self, event) -> None:  # noqa: N802 — Qt API
        super().resizeEvent(event)
        self.apply_direction(self._rtl)

    def showEvent(self, event) -> None:  # noqa: N802 — Qt API
        super().showEvent(event)
        self.apply_direction(self._rtl)


def configure_rtl_scroll(area: QScrollArea, *, rtl: bool = True) -> None:
    """Configure scrollable content direction; scrollbar stays on the right."""
    if isinstance(area, RtlScrollArea):
        area.apply_direction(rtl)
        return
    if rtl:
        area.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        area.viewport().setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    else:
        area.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        area.viewport().setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    bar = area.verticalScrollBar()
    if bar is not None:
        bar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)


def make_page_layout(host: QWidget, *, margins: tuple[int, int, int, int] = (24, 18, 24, 18)) -> QVBoxLayout:
    layout = QVBoxLayout(host)
    layout.setContentsMargins(*margins)
    layout.setSpacing(12)
    return layout


def mark_expanding(widget: QWidget, *, vertical: bool = True, horizontal: bool = False) -> None:
    policy_h = QSizePolicy.Policy.Expanding if horizontal else QSizePolicy.Policy.Preferred
    policy_v = QSizePolicy.Policy.Expanding if vertical else QSizePolicy.Policy.Preferred
    widget.setSizePolicy(policy_h, policy_v)
