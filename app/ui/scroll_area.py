"""RTL-aware scroll areas and responsive page helpers."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QSizePolicy, QVBoxLayout, QWidget


class RtlScrollArea(QScrollArea):
    """RTL content with vertical scrollbar on the right (Persian desktop convention)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("RtlScrollArea")
        self.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._apply_rtl()

    def _apply_rtl(self) -> None:
        # Keep chrome LTR so the vertical bar stays on the right edge.
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.viewport().setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        bar = self.verticalScrollBar()
        if bar is not None:
            bar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def setWidget(self, widget: QWidget | None) -> None:  # noqa: N802 — Qt API
        if widget is not None:
            widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        super().setWidget(widget)
        self._apply_rtl()

    def resizeEvent(self, event) -> None:  # noqa: N802 — Qt API
        super().resizeEvent(event)
        self._apply_rtl()

    def showEvent(self, event) -> None:  # noqa: N802 — Qt API
        super().showEvent(event)
        self._apply_rtl()


def configure_rtl_scroll(area: QScrollArea) -> None:
    """RTL scrollable content; scrollbar remains on the right."""
    area.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    area.viewport().setLayoutDirection(Qt.LayoutDirection.RightToLeft)
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
