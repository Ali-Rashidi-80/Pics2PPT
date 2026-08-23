"""First-run UI language picker (bilingual labels; works before i18n is set)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app import APP_NAME
from app.i18n.locale_detect import normalize


class LanguagePickerDialog(QDialog):
    """Ask the user to choose Persian or English on first launch."""

    def __init__(self, parent=None, *, suggested: str = "en") -> None:
        super().__init__(parent)
        self._choice: str | None = None
        self._suggested = normalize(suggested)
        self.setWindowTitle(f"{APP_NAME} — Language / زبان")
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 20)
        root.setSpacing(14)

        title = QLabel("Choose language / انتخاب زبان")
        title.setObjectName("AboutTitle")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        body = QLabel(
            "Select the interface language. You can change this later in Settings.\n\n"
            "زبان رابط کاربری را انتخاب کنید. بعداً از تنظیمات قابل تغییر است."
        )
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.setObjectName("GroupHint")
        root.addWidget(body)

        row = QHBoxLayout()
        row.setSpacing(12)
        self.btn_fa = QPushButton("فارسی")
        self.btn_en = QPushButton("English")
        self.btn_fa.setMinimumHeight(44)
        self.btn_en.setMinimumHeight(44)
        self.btn_fa.clicked.connect(lambda: self._pick("fa"))
        self.btn_en.clicked.connect(lambda: self._pick("en"))
        row.addWidget(self.btn_fa)
        row.addWidget(self.btn_en)
        root.addLayout(row)

        hint = QLabel("Tip: also controls default slide language (Same as UI).")
        hint.setObjectName("SidebarHint")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)

        if self._suggested == "fa":
            self.btn_fa.setDefault(True)
            self.btn_fa.setFocus()
        else:
            self.btn_en.setDefault(True)
            self.btn_en.setFocus()

    def _pick(self, code: str) -> None:
        self._choice = normalize(code)
        self.accept()

    def selected_language(self) -> str:
        if self._choice:
            return self._choice
        return self._suggested

    def reject(self) -> None:
        # Escape / window close → keep OS-suggested language, still mark as chosen.
        self._choice = self._suggested
        self.accept()


def prompt_ui_language(parent=None, *, suggested: str = "en") -> str:
    dlg = LanguagePickerDialog(parent, suggested=suggested)
    dlg.exec()
    return dlg.selected_language()
