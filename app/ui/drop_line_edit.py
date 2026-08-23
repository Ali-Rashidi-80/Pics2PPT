"""Line edit that accepts folder drag-and-drop with visual feedback."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QLineEdit, QStyle


class DropLineEdit(QLineEdit):
    path_dropped = Signal(str)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setObjectName("DropZone")
        self.setToolTip("پوشهٔ ورودی را اینجا بکشید و رها کنید، یا مسیر را تایپ کنید.")

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].isLocalFile():
                self.setProperty("dragOver", True)
                self.style().unpolish(self)
                self.style().polish(self)
                event.acceptProposedAction()
                return
        event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        self.setProperty("dragOver", False)
        self.style().unpolish(self)
        self.style().polish(self)
        urls = event.mimeData().urls()
        if not urls:
            return
        path = Path(urls[0].toLocalFile())
        if path.is_file():
            path = path.parent
        if path.is_dir():
            text = str(path)
            self.setText(text)
            self.path_dropped.emit(text)
            event.acceptProposedAction()
        else:
            event.ignore()
