"""RTL layout helpers for Persian UI."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QTextOption
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextBrowser,
    QTextEdit,
    QWidget,
)

from app.ui.scroll_area import RtlScrollArea, configure_rtl_scroll

# Visual right / reading-start edge in RTL layouts
ALIGN_START = Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignVCenter
ALIGN_START_TOP = Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignTop


def apply_rtl_rich_text(browser: QTextBrowser) -> None:
    """Force RTL alignment inside QTextBrowser (Qt HTML subset ignores much CSS)."""
    browser.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    doc = browser.document()
    opt = QTextOption()
    opt.setTextDirection(Qt.LayoutDirection.RightToLeft)
    opt.setAlignment(Qt.AlignmentFlag.AlignRight)
    doc.setDefaultTextOption(opt)

    cursor = QTextCursor(doc)
    block = doc.begin()
    while block.isValid():
        fmt = block.blockFormat()
        fmt.setAlignment(Qt.AlignmentFlag.AlignRight)
        fmt.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        cursor.setPosition(block.position())
        cursor.setBlockFormat(fmt)
        block = block.next()


def configure_rtl_text_edit(edit: QTextEdit) -> None:
    """Persian RTL text with scrollbar on the right."""
    edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    opt = edit.document().defaultTextOption()
    opt.setTextDirection(Qt.LayoutDirection.RightToLeft)
    opt.setAlignment(Qt.AlignmentFlag.AlignRight)
    edit.document().setDefaultTextOption(opt)


def apply_layout_direction(root: QWidget, rtl: bool = True) -> None:
    direction = Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight
    root.setLayoutDirection(direction)

    for widget in root.findChildren(QWidget):
        if widget.property("forceLtr"):
            widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            continue
        widget.setLayoutDirection(direction)

    for area in root.findChildren(QAbstractScrollArea):
        if area.property("forceLtr"):
            continue
        if isinstance(area, QTextEdit):
            continue
        if isinstance(area, (QScrollArea, RtlScrollArea)):
            configure_rtl_scroll(area, rtl=rtl)
        else:
            area.setLayoutDirection(direction)

    for label in root.findChildren(QLabel):
        if label.property("forceLtr") or label.property("keepAlign"):
            continue
        label.setAlignment(ALIGN_START | Qt.AlignmentFlag.AlignTop if label.wordWrap() else ALIGN_START)

    for edit in root.findChildren(QLineEdit):
        if edit.property("forceLtr"):
            edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            edit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignAbsolute | Qt.AlignmentFlag.AlignVCenter)
            continue
        edit.setAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignVCenter)

    for box in root.findChildren(QTextEdit):
        if box.property("forceLtr"):
            continue
        configure_rtl_text_edit(box)

    for browser in root.findChildren(QTextBrowser):
        browser.setLayoutDirection(direction)
        if browser.property("forceLtr"):
            continue
        apply_rtl_rich_text(browser)

    for form in root.findChildren(QFormLayout):
        form.setLabelAlignment(ALIGN_START)
        form.setFormAlignment(ALIGN_START_TOP)

    for cb in root.findChildren(QCheckBox):
        cb.setLayoutDirection(direction)

    for combo in root.findChildren(QComboBox):
        if not combo.property("forceLtr"):
            combo.setLayoutDirection(direction)

    for spin in root.findChildren(QSpinBox):
        spin.setLayoutDirection(direction)
        spin.setAlignment(Qt.AlignmentFlag.AlignLeading)

    for btn in root.findChildren(QPushButton):
        btn.setLayoutDirection(direction)

    for group in root.findChildren(QGroupBox):
        group.setLayoutDirection(direction)
        group.setAlignment(Qt.AlignmentFlag.AlignLeading)

    for lst in root.findChildren(QListWidget):
        lst_dir = Qt.LayoutDirection.RightToLeft if rtl else Qt.LayoutDirection.LeftToRight
        lst.setLayoutDirection(lst_dir)
        lst.setLayoutMode(QListWidget.LayoutMode.SinglePass)
        bar = lst.verticalScrollBar()
        if bar is not None:
            bar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        for i in range(lst.count()):
            item = lst.item(i)
            if item is not None:
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignVCenter)


def configure_footer_field(edit: QLineEdit, *, rtl: bool) -> None:
    """Footer text follows UI reading direction."""
    if rtl:
        edit.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        edit.setAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignVCenter)
    else:
        edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        edit.setAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignVCenter)


def mark_path_field(edit: QLineEdit) -> None:
    """Windows paths stay LTR for readability."""
    edit.setProperty("forceLtr", True)
    edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    edit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignAbsolute | Qt.AlignmentFlag.AlignVCenter)
