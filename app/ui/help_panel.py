"""Native help panel for the About page (FA + EN, no HTML)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.i18n import ui_language
from app.i18n.help_content import get_help_sections
from app.ui.layout_direction import ALIGN_START, ALIGN_START_TOP
from app.ui.theme import palette


def _content_direction(lang: str | None = None) -> Qt.LayoutDirection:
    lng = lang or ui_language()
    return Qt.LayoutDirection.RightToLeft if lng == "fa" else Qt.LayoutDirection.LeftToRight


def _heading(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("HelpHeading")
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START)
    return lbl


def _subheading(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("HelpSubheading")
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START)
    return lbl


def _paragraph(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("HelpParagraph")
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START_TOP)
    return lbl


def _list_item(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("HelpParagraph")
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START_TOP)
    lbl.setLayoutDirection(_content_direction())
    return lbl


def _bullet_list(items: list[str]) -> QWidget:
    box = QWidget()
    box.setLayoutDirection(_content_direction())
    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    for item in items:
        layout.addWidget(_list_item(f"• {item}"))
    return box


def _numbered_list(items: list[str]) -> QWidget:
    box = QWidget()
    box.setLayoutDirection(_content_direction())
    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    for index, item in enumerate(items, start=1):
        layout.addWidget(_list_item(f"{index}. {item}"))
    return box


def _tip(text: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName("HelpTip")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 12, 14, 12)
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START_TOP)
    lbl.setObjectName("HelpParagraph")
    layout.addWidget(lbl)
    return frame


def _warn(text: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName("HelpWarn")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 12, 14, 12)
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START_TOP)
    lbl.setObjectName("HelpParagraph")
    layout.addWidget(lbl)
    return frame


def _code_block(text: str) -> QPlainTextEdit:
    edit = QPlainTextEdit()
    edit.setObjectName("HelpCode")
    edit.setReadOnly(True)
    edit.setPlainText(text)
    edit.setFixedHeight(min(180, 16 + text.count("\n") * 18))
    edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    edit.setProperty("forceLtr", True)
    return edit


def _path_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("HelpPath")
    lbl.setWordWrap(True)
    lbl.setProperty("forceLtr", True)
    lbl.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    return lbl


def _table(headers: list[str], rows: list[list[str]]) -> QFrame:
    frame = QFrame()
    frame.setObjectName("HelpTable")
    frame.setLayoutDirection(_content_direction())
    grid = QGridLayout(frame)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(0)
    grid.setVerticalSpacing(0)

    cols = len(headers)
    for col, title in enumerate(headers):
        head = QLabel(title)
        head.setObjectName("HelpTableHeader")
        head.setWordWrap(True)
        head.setAlignment(ALIGN_START_TOP)
        grid.addWidget(head, 0, col)

    for row_idx, row in enumerate(rows, start=1):
        for col, cell in enumerate(row):
            if col == 1 and "\\" in cell:
                widget: QWidget = _path_label(cell)
            else:
                widget = QLabel(cell)
                widget.setObjectName("HelpTableCell")
                widget.setWordWrap(True)
                widget.setAlignment(ALIGN_START_TOP)
            grid.addWidget(widget, row_idx, col)

    for col in range(cols):
        grid.setColumnStretch(col, 1)
    return frame


def build_help_panel(theme_id: str, app_version: str = "1.3.0", lang: str | None = None) -> QWidget:
    _ = palette(theme_id)
    lng = lang or ui_language()
    sections = get_help_sections(lng)

    root = QWidget()
    root.setObjectName("HelpPanel")
    root.setLayoutDirection(_content_direction(lng))
    layout = QVBoxLayout(root)
    layout.setContentsMargins(4, 4, 4, 12)
    layout.setSpacing(16)

    for section in sections:
        kind = section["type"]
        if kind == "heading":
            layout.addWidget(_heading(section["text"]))
        elif kind == "subheading":
            layout.addWidget(_subheading(section["text"]))
        elif kind == "paragraph":
            layout.addWidget(_paragraph(section["text"]))
        elif kind == "numbered":
            layout.addWidget(_numbered_list(section["items"]))
        elif kind == "bullet":
            layout.addWidget(_bullet_list(section["items"]))
        elif kind == "tip":
            layout.addWidget(_tip(section["text"]))
        elif kind == "warn":
            layout.addWidget(_warn(section["text"]))
        elif kind == "code":
            layout.addWidget(_code_block(section["text"]))
        elif kind == "table":
            layout.addWidget(_table(section["headers"], section["rows"]))

    version_label = "نسخه" if lng == "fa" else "Version"
    layout.addWidget(
        _paragraph(f"Pics2PPT — {version_label} {app_version} — Ali Rashidi")
    )

    root.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
    return root
