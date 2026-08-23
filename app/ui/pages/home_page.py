"""Main conversion page."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.core.models import BuildSettings
from app.core.output_paths import (
    ConflictMode,
    OutputPlacement,
    find_existing_outputs,
    scan_jobs,
)
from app.core.worker import PresentationWorker
from app.ui.drop_line_edit import DropLineEdit
from app.ui.layout_direction import ALIGN_START, mark_path_field
from app.ui.scroll_area import RtlScrollArea, make_page_layout
from app.ui.widgets import (
    make_icon_button,
    make_log_panel,
    make_page_header,
    make_path_row,
    make_responsive_button_bar,
    make_stacked_field,
    make_tip_card,
)


class HomePage(QWidget):
    def __init__(self, parent_window) -> None:
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.parent_window = parent_window
        self.thread_pool = QThreadPool.globalInstance()
        self.worker: PresentationWorker | None = None
        self._build_ui()
        self.load_from_settings()

    def _build_ui(self) -> None:
        root = make_page_layout(self)

        scroll = RtlScrollArea()
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        body = QWidget()
        body.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        content = QVBoxLayout(body)
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(12)

        content.addWidget(
            make_page_header(
                "ساخت گزارش پاورپوینت",
                "پوشهٔ ورودی را انتخاب کنید. برنامه به‌صورت خودکار ساختار پوشه‌ها را تشخیص می‌دهد "
                "و برای هر بخش یک فایل PPTX می‌سازد. خروجی در همان پوشهٔ ورودی ذخیره می‌شود.",
            )
        )

        content.addWidget(
            make_tip_card(
                "پوشهٔ ریشه را انتخاب کنید تا برای هر زیرپوشه یک PPTX ساخته شود. "
                "قبل از ساخت، محل خروجی را انتخاب می‌کنید: یکجا یا داخل هر پوشه."
            )
        )

        src = QGroupBox("پوشهٔ ورودی")
        src_layout = QHBoxLayout(src)
        src_layout.setSpacing(10)
        self.root_edit = DropLineEdit()
        self.root_edit.setPlaceholderText("مسیر پوشهٔ پروژه یا پوشهٔ تصاویر — یا اینجا رها کنید")
        self.root_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        mark_path_field(self.root_edit)
        browse = QPushButton("انتخاب پوشه…")
        browse.setObjectName("GhostBtn")
        browse.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        browse.setToolTip("انتخاب پوشه (Ctrl+O)")
        browse.clicked.connect(self._browse_root)
        src_layout.addWidget(self.root_edit, stretch=1)
        src_layout.addWidget(browse)
        content.addWidget(src)

        meta = QGroupBox("لوگو و پاورقی (اختیاری)")
        meta_layout = QVBoxLayout(meta)
        meta_layout.setSpacing(10)
        hint = QLabel("لوگوها در گوشهٔ بالای هر اسلاید و متن پاورقی در پایین نمایش داده می‌شود.")
        hint.setObjectName("GroupHint")
        hint.setWordWrap(True)
        hint.setAlignment(ALIGN_START)
        meta_layout.addWidget(hint)

        self.logo_right_edit = QLineEdit()
        self.logo_right_edit.setPlaceholderText("مسیر لوگوی گوشهٔ راست هدر")
        mark_path_field(self.logo_right_edit)
        btn_r = make_icon_button("انتخاب تصویر لوگوی راست")
        btn_r.clicked.connect(lambda: self._browse_logo(self.logo_right_edit))
        meta_layout.addWidget(make_stacked_field("لوگوی راست:", make_path_row(self.logo_right_edit, btn_r)))

        self.logo_left_edit = QLineEdit()
        self.logo_left_edit.setPlaceholderText("مسیر لوگوی گوشهٔ چپ هدر")
        mark_path_field(self.logo_left_edit)
        btn_l = make_icon_button("انتخاب تصویر لوگوی چپ")
        btn_l.clicked.connect(lambda: self._browse_logo(self.logo_left_edit))
        meta_layout.addWidget(make_stacked_field("لوگوی چپ:", make_path_row(self.logo_left_edit, btn_l)))

        self.footer_edit = QLineEdit()
        self.footer_edit.setPlaceholderText("مثال: عنوان پروژه — مکان — ۱۴۰۴/۰۶/۰۱")
        self.footer_edit.setAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignVCenter)
        self.footer_edit.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        meta_layout.addWidget(make_stacked_field("متن پاورقی:", self.footer_edit))

        meta_actions = QHBoxLayout()
        self.clear_inputs_btn = QPushButton("پاک کردن ورودی‌ها")
        self.clear_inputs_btn.setObjectName("GhostBtn")
        self.clear_inputs_btn.setToolTip("پاک کردن پوشه، لوگوها و متن پاورقی")
        self.clear_inputs_btn.clicked.connect(self._clear_inputs)
        meta_actions.addWidget(self.clear_inputs_btn)
        meta_actions.addStretch()
        meta_layout.addLayout(meta_actions)
        content.addWidget(meta)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.status_label = QLabel("آماده")
        self.status_label.setObjectName("StatusLabel")
        self._set_status("ready")
        action_row.addWidget(self.status_label)
        action_row.addStretch()
        shortcut_hint = QLabel("F5 شروع  ·  Esc توقف")
        shortcut_hint.setObjectName("ShortcutHint")
        shortcut_hint.setWordWrap(True)
        shortcut_hint.setAlignment(ALIGN_START)
        action_row.addWidget(shortcut_hint)
        content.addLayout(action_row)

        self.start_btn = QPushButton("شروع ساخت")
        self.start_btn.setObjectName("PrimaryBtn")
        self.start_btn.setToolTip("شروع ساخت خودکار فایل‌های PPTX (F5)")
        self.start_btn.clicked.connect(self._start)
        self.cancel_btn = QPushButton("توقف")
        self.cancel_btn.setObjectName("DangerBtn")
        self.cancel_btn.setToolTip("لغو عملیات در حال اجرا (Esc)")
        self.cancel_btn.clicked.connect(self._cancel)
        self.open_out_btn = QPushButton("باز کردن پوشه خروجی")
        self.open_out_btn.setObjectName("GhostBtn")
        self.open_out_btn.setEnabled(False)
        self.open_out_btn.clicked.connect(self._open_output)
        content.addWidget(make_responsive_button_bar(self.start_btn, self.cancel_btn, self.open_out_btn))

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFormat("%p%")
        self.progress.setTextVisible(True)
        content.addWidget(self.progress)
        content.addStretch(1)

        scroll.setWidget(body)
        root.addWidget(scroll, stretch=1)

        log_panel, self.log_view = make_log_panel()
        root.addWidget(log_panel)

        self._last_output_dir = ""
        self._last_placement: OutputPlacement = "central"
        self._set_running(False)

    def _set_status(self, state: str, text: str | None = None) -> None:
        labels = {
            "idle": "آماده",
            "ready": "آماده برای ساخت",
            "running": "در حال ساخت…",
            "error": "خطا",
            "done": "ساخت کامل شد",
        }
        self.status_label.setProperty("state", state)
        self.status_label.setText(text or labels.get(state, state))
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def load_from_settings(self) -> None:
        """Session inputs stay empty on each launch (no path/footer/logo cache)."""
        self.root_edit.clear()
        self.footer_edit.clear()
        self.logo_right_edit.clear()
        self.logo_left_edit.clear()
        self._set_status("idle")

    def build_settings(self) -> BuildSettings:
        data = self.parent_window.settings.build_settings_dict()
        data["footer_text"] = self.footer_edit.text().strip()
        data["logo_right"] = self.logo_right_edit.text().strip()
        data["logo_left"] = self.logo_left_edit.text().strip()
        return BuildSettings.from_dict(data)

    def _browse_root(self) -> None:
        start = self.root_edit.text().strip() or str(Path.home() / "Desktop")
        path = QFileDialog.getExistingDirectory(self, "انتخاب پوشهٔ ورودی", start)
        if path:
            self.root_edit.setText(path)
            self._set_status("ready")

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
        self.clear_inputs_btn.setEnabled(not running)
        self.root_edit.setEnabled(not running)
        self.logo_right_edit.setEnabled(not running)
        self.logo_left_edit.setEnabled(not running)
        self.footer_edit.setEnabled(not running)
        if running:
            self._set_status("running")
        elif self.root_edit.text().strip() and Path(self.root_edit.text().strip()).is_dir():
            self._set_status("ready")
        else:
            self._set_status("idle")

    def _clear_inputs(self) -> None:
        if self.worker:
            return
        if not any(
            field.text().strip()
            for field in (self.root_edit, self.footer_edit, self.logo_right_edit, self.logo_left_edit)
        ):
            self._set_status("idle")
            return
        box = QMessageBox(self)
        box.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        box.setWindowTitle("پاک کردن ورودی‌ها")
        box.setText("همهٔ فیلدهای ورودی پاک شوند؟")
        box.setInformativeText("پوشهٔ ورودی، لوگوها و متن پاورقی خالی می‌شوند.")
        yes_btn = box.addButton("پاک کردن", QMessageBox.ButtonRole.DestructiveRole)
        no_btn = box.addButton("انصراف", QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(no_btn)
        box.exec()
        if box.clickedButton() is not yes_btn:
            return
        self.load_from_settings()
        self.progress.setValue(0)

    def _collect_created_pptx(self, browse_dir: str) -> list[Path]:
        folder_name = self.parent_window.settings.get("output_folder_name", "Output_PPTX")
        root = Path(browse_dir)
        if not root.is_dir():
            return []
        if self._last_placement == "central":
            target = root if root.name == folder_name else root / folder_name
            if target.is_dir():
                return sorted(target.glob("*.pptx"))
            return []
        found: list[Path] = []
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name in {folder_name, "Output_PPTX"}:
                continue
            out = child / folder_name
            if out.is_dir():
                found.extend(sorted(out.glob("*.pptx")))
        # single-folder selection: outputs sit under browse_dir/Output_PPTX
        direct = root / folder_name
        if direct.is_dir():
            found.extend(sorted(direct.glob("*.pptx")))
        # de-dupe while keeping order
        seen: set[Path] = set()
        unique: list[Path] = []
        for p in found:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        return unique

    def _show_success_dialog(self, output_dir: str) -> None:
        box = QMessageBox(self)
        box.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("پایان موفق")
        folder_name = self.parent_window.settings.get("output_folder_name", "Output_PPTX")
        pptx_files = self._collect_created_pptx(output_dir)
        input_dir = self.root_edit.text().strip()
        box.setText("ساخت فایل‌های پاورپوینت با موفقیت انجام شد.")
        if self._last_placement == "per_folder":
            where = (
                f"هر فایل داخل پوشهٔ مربوطه ذخیره شد:\n"
                f"«نام‌پوشه\\{folder_name}\\نام‌پوشه.pptx»"
            )
        else:
            where = f"همهٔ فایل‌ها یکجا در:\n{output_dir}"
        box.setInformativeText(
            f"{where}\n\n"
            f"تعداد فایل PPTX: {len(pptx_files)}"
        )
        open_out_btn = box.addButton("باز کردن پوشه خروجی", QMessageBox.ButtonRole.ActionRole)
        open_in_btn = None
        if input_dir and Path(input_dir).is_dir():
            open_in_btn = box.addButton("باز کردن پوشه ورودی", QMessageBox.ButtonRole.ActionRole)
        open_pptx_btn = None
        if len(pptx_files) == 1:
            open_pptx_btn = box.addButton("باز کردن PPTX", QMessageBox.ButtonRole.ActionRole)
        elif len(pptx_files) > 1:
            open_pptx_btn = box.addButton("باز کردن اولین PPTX", QMessageBox.ButtonRole.ActionRole)
        close_btn = box.addButton("بستن", QMessageBox.ButtonRole.AcceptRole)
        box.setDefaultButton(open_out_btn)
        box.exec()
        clicked = box.clickedButton()
        if clicked is open_out_btn:
            self._open_path(output_dir)
        elif open_in_btn is not None and clicked is open_in_btn:
            self._open_path(input_dir)
        elif open_pptx_btn is not None and clicked is open_pptx_btn and pptx_files:
            self._open_file(str(pptx_files[0]))
        elif clicked is close_btn and self.parent_window.settings.get("open_output_when_done") and output_dir:
            self._open_path(output_dir)

    def _ask_output_placement(self, job_count: int) -> OutputPlacement | None:
        if job_count <= 1:
            return "per_folder"
        box = QMessageBox(self)
        box.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        box.setWindowTitle("محل ذخیرهٔ فایل‌ها")
        box.setText(f"{job_count} گزارش ساخته خواهد شد. فایل‌ها کجا ذخیره شوند؟")
        box.setInformativeText(
            "داخل هر پوشه: مثل کار دستی — هر PPTX داخل همان زیرپوشه "
            f"(پوشه\\Output_PPTX\\نام.pptx).\n\n"
            "یکجا: همهٔ فایل‌ها در یک پوشه Output_PPTX زیر ریشهٔ انتخاب‌شده."
        )
        per_btn = box.addButton("داخل هر پوشه", QMessageBox.ButtonRole.AcceptRole)
        central_btn = box.addButton("یکجا", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = box.addButton("انصراف", QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(per_btn)
        box.exec()
        clicked = box.clickedButton()
        if clicked is cancel_btn or clicked is None:
            return None
        if clicked is central_btn:
            return "central"
        return "per_folder"

    def _ask_conflict_mode(self, existing: list[Path]) -> ConflictMode | None:
        box = QMessageBox(self)
        box.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setWindowTitle("فایل‌های قبلی یافت شد")
        count = len(existing)
        preview = "\n".join(f"• {p.parent.name}/{p.name}" for p in existing[:6])
        if count > 6:
            preview += f"\n• … و {count - 6} فایل دیگر"
        box.setText(f"{count} فایل PPTX با همین نام در مسیر خروجی وجود دارد.")
        box.setInformativeText(
            f"{preview}\n\n"
            "جایگزین: فایل‌های قبلی بازنویسی می‌شوند.\n"
            "نسخه جدید: فایل‌ها با پسوند (۲)، (۳) … کنار قبلی‌ها ساخته می‌شوند."
        )
        replace_btn = box.addButton("جایگزین", QMessageBox.ButtonRole.DestructiveRole)
        version_btn = box.addButton("نسخه جدید", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = box.addButton("انصراف", QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(version_btn)
        box.exec()
        clicked = box.clickedButton()
        if clicked is cancel_btn:
            return None
        if clicked is version_btn:
            return "version"
        return "replace"

    def _conflict_mode_for_run(self, root: str, placement: OutputPlacement) -> ConflictMode | None:
        folder_name = self.parent_window.settings.get("output_folder_name", "Output_PPTX")
        existing = find_existing_outputs(Path(root), folder_name, placement=placement)
        if not existing:
            return "replace"
        return self._ask_conflict_mode(existing)

    def _start(self) -> None:
        root = self.root_edit.text().strip()
        if not root or not Path(root).is_dir():
            QMessageBox.warning(self, "مسیر نامعتبر", "لطفاً یک پوشهٔ ورودی معتبر انتخاب کنید.")
            self._set_status("error", "مسیر نامعتبر")
            return

        folder_name = self.parent_window.settings.get("output_folder_name", "Output_PPTX")
        try:
            jobs = scan_jobs(Path(root), folder_name)
        except (NotADirectoryError, OSError) as exc:
            QMessageBox.warning(self, "خطا", str(exc))
            self._set_status("error")
            return
        if not jobs:
            QMessageBox.warning(
                self,
                "بدون تصویر",
                "هیچ تصویر معتبری در این پوشه یا زیرپوشه‌هایش یافت نشد.",
            )
            self._set_status("error", "بدون تصویر")
            return

        placement = self._ask_output_placement(len(jobs))
        if placement is None:
            self._set_status("ready")
            return

        conflict_mode = self._conflict_mode_for_run(root, placement)
        if conflict_mode is None:
            self._set_status("ready")
            return

        self._last_placement = placement
        self.progress.setValue(0)
        self.log_view.clear()
        self.log_view.append("آماده‌سازی…")
        self.open_out_btn.setEnabled(False)

        self.worker = PresentationWorker(
            root,
            self.build_settings(),
            conflict_mode=conflict_mode,
            output_placement=placement,
        )
        self.worker.signals.progress.connect(self.progress.setValue)
        self.worker.signals.log.connect(lambda m: self.log_view.append(m))
        self.worker.signals.error.connect(self._on_worker_error)
        self.worker.signals.finished.connect(self._on_finished)
        self._set_running(True)
        self.thread_pool.start(self.worker)

    def _on_worker_error(self, message: str) -> None:
        self.log_view.append(f"[خطا] {message}")
        self._set_status("error")

    def _cancel(self) -> None:
        if self.worker:
            self.worker.cancel()
            self.log_view.append("درخواست توقف ارسال شد…")
            self._set_status("running", "در حال توقف…")

    def _on_finished(self, success: bool, output_dir: str) -> None:
        self._set_running(False)
        self.worker = None
        self._last_output_dir = output_dir
        if output_dir:
            self.open_out_btn.setEnabled(True)
        if success:
            self._set_status("done")
            self._show_success_dialog(output_dir)
        else:
            self._set_status("error", "ساخت ناموفق")

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

    @staticmethod
    def _open_file(path: str) -> None:
        p = Path(path)
        if not p.is_file():
            return
        if sys.platform == "win32":
            os.startfile(str(p))  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", str(p)], check=False)
        else:
            subprocess.run(["xdg-open", str(p)], check=False)
