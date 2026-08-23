"""Reusable UI widgets."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.ui.layout_direction import ALIGN_START


def make_page_header(title: str, subtitle: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName("PageHeader")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 6)
    layout.setSpacing(4)

    accent = QFrame()
    accent.setObjectName("PageHeaderAccent")
    accent.setFixedHeight(3)

    t = QLabel(title)
    t.setObjectName("PageTitle")
    t.setAlignment(ALIGN_START)
    s = QLabel(subtitle)
    s.setObjectName("PageSubtitle")
    s.setWordWrap(True)
    s.setAlignment(ALIGN_START | Qt.AlignmentFlag.AlignTop)

    layout.addWidget(accent)
    layout.addWidget(t)
    layout.addWidget(s)
    return frame


def make_tip_card(text: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName("TipCard")
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(14, 12, 14, 12)
    icon = QLabel("💡")
    icon.setObjectName("TipIcon")
    icon.setProperty("keepAlign", True)
    icon.setFixedWidth(28)
    icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
    body = QLabel(text)
    body.setObjectName("TipText")
    body.setWordWrap(True)
    body.setAlignment(ALIGN_START)
    layout.addWidget(icon)
    layout.addWidget(body, stretch=1)
    return frame


def make_log_panel(title: str = "گزارش عملیات", *, log_height: int = 88) -> tuple[QFrame, QTextEdit]:
    panel = QFrame()
    panel.setObjectName("LogPanel")
    panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(14, 10, 14, 12)
    layout.setSpacing(6)

    lbl = QLabel(title)
    lbl.setObjectName("LogPanelTitle")
    lbl.setAlignment(ALIGN_START)
    layout.addWidget(lbl)

    log = QTextEdit()
    log.setObjectName("LogView")
    log.setReadOnly(True)
    log.setFixedHeight(log_height)
    log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    log.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    layout.addWidget(log)
    return panel, log


def make_icon_button(tooltip: str = "") -> QPushButton:
    btn = QPushButton("…")
    btn.setObjectName("IconBtn")
    btn.setFixedSize(38, 38)
    btn.setToolTip(tooltip)
    return btn


def wrap_layout(layout: QHBoxLayout | QVBoxLayout) -> QWidget:
    """Wrap a layout in a QWidget so parent layouts compute size correctly."""
    host = QWidget()
    host.setLayout(layout)
    host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return host


def make_stacked_field(label: str, content: QWidget | QHBoxLayout | QVBoxLayout) -> QWidget:
    """Label above control — stable in RTL and at narrow widths."""
    host = QWidget()
    host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)

    lbl = QLabel(label)
    lbl.setObjectName("FormLabel")
    lbl.setAlignment(ALIGN_START)
    layout.addWidget(lbl)

    if isinstance(content, QWidget):
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(content)
    else:
        layout.addWidget(wrap_layout(content))
    return host


def make_path_row(edit: QLineEdit, browse_btn: QPushButton) -> QWidget:
    row = QHBoxLayout()
    row.setSpacing(8)
    edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    browse_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    row.addWidget(edit, stretch=1)
    row.addWidget(browse_btn)
    return wrap_layout(row)


def make_responsive_button_bar(*buttons: QPushButton, spacing: int = 10) -> QWidget:
    """Button row that shares width evenly on narrow windows."""
    host = QWidget()
    row = QHBoxLayout(host)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(spacing)
    for btn in buttons:
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        row.addWidget(btn, stretch=1)
    return host


def make_form_row(label: str, widget: QWidget) -> QHBoxLayout:
    row = QHBoxLayout()
    lbl = QLabel(label)
    lbl.setObjectName("FormLabel")
    lbl.setMinimumWidth(140)
    lbl.setAlignment(ALIGN_START)
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
