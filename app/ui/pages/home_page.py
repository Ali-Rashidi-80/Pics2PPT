"""Main conversion page."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.models import BuildSettings
from app.core.worker import PresentationWorker
from app.ui.drop_line_edit import DropLineEdit
from app.ui.widgets import make_page_header


class HomePage(QWidget):
    def __init__(self, parent_window) -> None:
        super().__init__()
        self.parent_window = parent_window
        self.thread_pool = QThreadPool.globalInstance()
        self.worker: PresentationWorker | None = None
        self._build_ui()
        self.load_from_settings()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        body = QWidget()
        root = QVBoxLayout(body)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(14)

        root.addWidget(
            make_page_header(
                "ساخت گزارش پاورپوینت",
                "پوشهٔ ورودی را انتخاب کنید. برنامه به‌صورت خودکار ساختار پوشه‌ها را تشخیص می‌دهد "
                "و برای هر بخش/نفر یک فایل PPTX می‌سازد. خروجی در همان پوشهٔ ورودی ذخیره می‌شود.",
            )
        )

        src = QGroupBox("پوشهٔ ورودی")
        src_layout = QHBoxLayout(src)
        self.root_edit = DropLineEdit()
        self.root_edit.setPlaceholderText("مسیر پوشهٔ پروژه یا پوشهٔ تصاویر — یا اینجا رها کنید")
        self.root_edit.setToolTip("مسیر پوشهٔ اصلی پروژه یا یک پوشهٔ تصویری")
        browse = QPushButton("انتخاب پوشه…")
        browse.setObjectName("GhostBtn")
        browse.setToolTip("انتخاب پوشه از دیالوگ فایل")
        browse.clicked.connect(self._browse_root)
        src_layout.addWidget(self.root_edit, stretch=1)
        src_layout.addWidget(browse)
        root.addWidget(src)

        meta = QGroupBox("لوگو و پاورقی (اختیاری)")
        form = QFormLayout(meta)
        form.setLabelAlignment(Qt.AlignRight)

        self.logo_right_edit = QLineEdit()
        self.logo_right_edit.setPlaceholderText("مسیر لوگوی گوشهٔ راست هدر")
        self.logo_right_edit.setToolTip("PNG یا JPG — در گوشهٔ راست بالای هر اسلاید")
        btn_r = QPushButton("…")
        btn_r.setFixedWidth(36)
        btn_r.clicked.connect(lambda: self._browse_logo(self.logo_right_edit))
        row_r = QHBoxLayout()
        row_r.addWidget(self.logo_right_edit, stretch=1)
        row_r.addWidget(btn_r)
        form.addRow("لوگوی راست:", row_r)

        self.logo_left_edit = QLineEdit()
        self.logo_left_edit.setPlaceholderText("مسیر لوگوی گوشهٔ چپ هدر")
        self.logo_left_edit.setToolTip("PNG یا JPG — در گوشهٔ چپ بالای هر اسلاید")
        btn_l = QPushButton("…")
        btn_l.setFixedWidth(36)
        btn_l.clicked.connect(lambda: self._browse_logo(self.logo_left_edit))
        row_l = QHBoxLayout()
        row_l.addWidget(self.logo_left_edit, stretch=1)
        row_l.addWidget(btn_l)
        form.addRow("لوگوی چپ:", row_l)

        self.footer_edit = QLineEdit()
        self.footer_edit.setPlaceholderText("مثال: عنوان پروژه — مکان — ۱۴۰۴/۰۶/۰۱")
        self.footer_edit.setToolTip("متن ثابت پایین هر اسلاید")
        form.addRow("متن پاورقی:", self.footer_edit)
        root.addWidget(meta)

        actions = QHBoxLayout()
        self.start_btn = QPushButton("شروع ساخت")
        self.start_btn.setObjectName("PrimaryBtn")
        self.start_btn.setToolTip("شروع ساخت خودکار فایل‌های PPTX")
        self.start_btn.clicked.connect(self._start)
        self.cancel_btn = QPushButton("توقف")
        self.cancel_btn.setObjectName("DangerBtn")
        self.cancel_btn.setToolTip("لغو عملیات در حال اجرا")
        self.cancel_btn.clicked.connect(self._cancel)
        self.open_out_btn = QPushButton("باز کردن پوشه خروجی")
        self.open_out_btn.setObjectName("GhostBtn")
        self.open_out_btn.setEnabled(False)
        self.open_out_btn.clicked.connect(self._open_output)
        actions.addWidget(self.start_btn)
        actions.addWidget(self.cancel_btn)
        actions.addWidget(self.open_out_btn)
        actions.addStretch()
        root.addLayout(actions)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFormat("%p%")
        root.addWidget(self.progress)

        root.addWidget(QLabel("گزارش عملیات"))
        self.log_view = QTextEdit()
        self.log_view.setObjectName("LogView")
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumHeight(200)
        root.addWidget(self.log_view)

        scroll.setWidget(body)
        outer.addWidget(scroll)
        self._last_output_dir = ""
        self._set_running(False)

    def load_from_settings(self) -> None:
        s = self.parent_window.settings
        last = s.get("last_input_dir", "")
        if last and Path(last).is_dir():
            self.root_edit.setText(last)
        self.footer_edit.setText(s.get("footer_text", ""))
        self.logo_right_edit.setText(s.get("logo_right", ""))
        self.logo_left_edit.setText(s.get("logo_left", ""))

    def persist_fields(self) -> None:
        s = self.parent_window.settings
        s.set("last_input_dir", self.root_edit.text().strip())
        s.set("footer_text", self.footer_edit.text().strip())
        s.set("logo_right", self.logo_right_edit.text().strip())
        s.set("logo_left", self.logo_left_edit.text().strip())
        s.save()

    def build_settings(self) -> BuildSettings:
        self.persist_fields()
        data = self.parent_window.settings.build_settings_dict()
        return BuildSettings.from_dict(data)

    def _browse_root(self) -> None:
        start = self.root_edit.text().strip() or str(Path.home() / "Desktop")
        path = QFileDialog.getExistingDirectory(self, "انتخاب پوشهٔ ورودی", start)
        if path:
            self.root_edit.setText(path)

    def _browse_logo(self, target: QLineEdit) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب تصویر لوگو",
            "",
            "تصاویر (*.png *.jpg *.jpeg *.bmp);;همه فایل‌ها (*)",
        )
        if path:
            target.setText(path)

    def _set_running(self, running: bool) -> None:
        self.start_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
        self.root_edit.setEnabled(not running)
        self.logo_right_edit.setEnabled(not running)
        self.logo_left_edit.setEnabled(not running)
        self.footer_edit.setEnabled(not running)

    def _start(self) -> None:
        root = self.root_edit.text().strip()
        if not root or not Path(root).is_dir():
            QMessageBox.warning(self, "مسیر نامعتبر", "لطفاً یک پوشهٔ ورودی معتبر انتخاب کنید.")
            return

        self.persist_fields()
        self.progress.setValue(0)
        self.log_view.clear()
        self.log_view.append("آماده‌سازی…")
        self.open_out_btn.setEnabled(False)

        self.worker = PresentationWorker(root, self.build_settings())
        self.worker.signals.progress.connect(self.progress.setValue)
        self.worker.signals.log.connect(lambda m: self.log_view.append(m))
        self.worker.signals.error.connect(lambda m: self.log_view.append(f"[خطا] {m}"))
        self.worker.signals.finished.connect(self._on_finished)
        self._set_running(True)
        self.thread_pool.start(self.worker)

    def _cancel(self) -> None:
        if self.worker:
            self.worker.cancel()
            self.log_view.append("درخواست توقف ارسال شد…")

    def _on_finished(self, success: bool, output_dir: str) -> None:
        self._set_running(False)
        self.worker = None
        self._last_output_dir = output_dir
        if output_dir:
            self.open_out_btn.setEnabled(True)
        if success:
            folder_name = self.parent_window.settings.get("output_folder_name", "Output_PPTX")
            QMessageBox.information(
                self,
                "پایان موفق",
                f"ساخت فایل‌های پاورپوینت با موفقیت انجام شد.\n\n"
                f"مسیر خروجی:\n{output_dir}\n\n"
                f"(پوشهٔ {folder_name} داخل پوشهٔ ورودی)",
            )
            if self.parent_window.settings.get("open_output_when_done") and output_dir:
                self._open_path(output_dir)

    def _open_output(self) -> None:
        if self._last_output_dir:
            self._open_path(self._last_output_dir)

    @staticmethod
    def _open_path(path: str) -> None:
        p = Path(path)
        if not p.is_dir():
            return
        if sys.platform == "win32":
            os.startfile(str(p))  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", str(p)], check=False)
        else:
            subprocess.run(["xdg-open", str(p)], check=False)
