"""Reusable UI widgets."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


def make_page_header(title: str, subtitle: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName("PageHeader")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 8)
    layout.setSpacing(4)
    t = QLabel(title)
    t.setObjectName("PageTitle")
    t.setAlignment(Qt.AlignRight)
    s = QLabel(subtitle)
    s.setObjectName("PageSubtitle")
    s.setWordWrap(True)
    s.setAlignment(Qt.AlignRight)
    layout.addWidget(t)
    layout.addWidget(s)
    return frame


def make_form_row(label: str, widget: QWidget) -> QHBoxLayout:
    row = QHBoxLayout()
    lbl = QLabel(label)
    lbl.setMinimumWidth(140)
    lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    row.addWidget(lbl)
    row.addWidget(widget, stretch=1)
    return row


class FormComboBox(QComboBox):
    """Combo that ignores wheel events while scrolling the page."""

    def wheelEvent(self, event) -> None:
        if not self.hasFocus():
            event.ignore()
            return
        super().wheelEvent(event)

    def set_items(self, items: list[tuple[str, str]]) -> None:
        self.clear()
        for key, label in items:
            self.addItem(label, key)

    def current_key(self) -> str:
        return str(self.currentData() or "")

    def set_current_key(self, key: str) -> None:
        idx = self.findData(key)
        if idx >= 0:
            self.setCurrentIndex(idx)
