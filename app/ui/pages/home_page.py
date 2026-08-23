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
from app.i18n import dialog_direction, is_rtl, t
from app.ui.drop_line_edit import DropLineEdit
from app.ui.layout_direction import ALIGN_START, configure_footer_field, mark_path_field
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
        self._status_state = "idle"
        self._build_ui()

    def _build_ui(self) -> None:
        root = make_page_layout(self)

        self.scroll = RtlScrollArea()
        self.scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        body = QWidget()
        body.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        content = QVBoxLayout(body)
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(12)

        self.page_header = make_page_header("", "")
        content.addWidget(self.page_header)

        self.tip_card = make_tip_card("")
        content.addWidget(self.tip_card)

        self.src_group = QGroupBox()
        src_layout = QHBoxLayout(self.src_group)
        src_layout.setSpacing(10)
        self.root_edit = DropLineEdit()
        self.root_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        mark_path_field(self.root_edit)
        self.browse_btn = QPushButton()
        self.browse_btn.setObjectName("GhostBtn")
        self.browse_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.browse_btn.clicked.connect(self._browse_root)
        src_layout.addWidget(self.root_edit, stretch=1)
        src_layout.addWidget(self.browse_btn)
        content.addWidget(self.src_group)

        self.meta_group = QGroupBox()
        meta_layout = QVBoxLayout(self.meta_group)
        meta_layout.setSpacing(10)
        self.meta_hint = QLabel()
        self.meta_hint.setObjectName("GroupHint")
        self.meta_hint.setWordWrap(True)
        self.meta_hint.setAlignment(ALIGN_START)
        meta_layout.addWidget(self.meta_hint)

        self.logo_right_edit = QLineEdit()
        mark_path_field(self.logo_right_edit)
        self.btn_logo_r = make_icon_button()
        self.btn_logo_r.clicked.connect(lambda: self._browse_logo(self.logo_right_edit))
        self.field_logo_r = make_stacked_field("", make_path_row(self.logo_right_edit, self.btn_logo_r))
        meta_layout.addWidget(self.field_logo_r)

        self.logo_left_edit = QLineEdit()
        mark_path_field(self.logo_left_edit)
        self.btn_logo_l = make_icon_button()
        self.btn_logo_l.clicked.connect(lambda: self._browse_logo(self.logo_left_edit))
        self.field_logo_l = make_stacked_field("", make_path_row(self.logo_left_edit, self.btn_logo_l))
        meta_layout.addWidget(self.field_logo_l)

        self.footer_edit = QLineEdit()
        self.footer_edit.setAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignVCenter)
        self.field_footer = make_stacked_field("", self.footer_edit)
        meta_layout.addWidget(self.field_footer)

        meta_actions = QHBoxLayout()
        self.clear_inputs_btn = QPushButton()
        self.clear_inputs_btn.setObjectName("GhostBtn")
        self.clear_inputs_btn.clicked.connect(self._clear_inputs)
        meta_actions.addWidget(self.clear_inputs_btn)
        meta_actions.addStretch()
        meta_layout.addLayout(meta_actions)
        content.addWidget(self.meta_group)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.status_label = QLabel()
        self.status_label.setObjectName("StatusLabel")
        action_row.addWidget(self.status_label)
        action_row.addStretch()
        self.shortcut_hint = QLabel()
        self.shortcut_hint.setObjectName("ShortcutHint")
        self.shortcut_hint.setWordWrap(True)
        self.shortcut_hint.setAlignment(ALIGN_START)
        action_row.addWidget(self.shortcut_hint)
        content.addLayout(action_row)

        self.start_btn = QPushButton()
        self.start_btn.setObjectName("PrimaryBtn")
        self.start_btn.clicked.connect(self._start)
        self.cancel_btn = QPushButton()
        self.cancel_btn.setObjectName("DangerBtn")
        self.cancel_btn.clicked.connect(self._cancel)
        self.open_out_btn = QPushButton()
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

        self.scroll.setWidget(body)
        root.addWidget(self.scroll, stretch=1)

        log_panel, self.log_view, self.log_title = make_log_panel()
        root.addWidget(log_panel)

        self._last_output_dir = ""
        self._last_placement: OutputPlacement = "central"
        self._set_running(False)
        self.retranslate_ui()
        self.load_from_settings()

    def apply_direction(self, rtl: bool) -> None:
        self.scroll.apply_direction(rtl)
        configure_footer_field(self.footer_edit, rtl=rtl)

    def retranslate_ui(self) -> None:
        self.page_header.title_label.setText(t("home.title"))  # type: ignore[attr-defined]
        self.page_header.subtitle_label.setText(t("home.subtitle"))  # type: ignore[attr-defined]
        self.tip_card.body_label.setText(t("home.tip"))  # type: ignore[attr-defined]
        self.src_group.setTitle(t("home.group.input"))
        self.root_edit.setPlaceholderText(t("home.placeholder.root"))
        self.root_edit.setToolTip(t("drop.tooltip"))
        self.browse_btn.setText(t("home.btn.browse"))
        self.browse_btn.setToolTip(t("home.tooltip.browse"))
        self.meta_group.setTitle(t("home.group.meta"))
        self.meta_hint.setText(t("home.meta.hint"))
        self.field_logo_r.field_label.setText(t("home.label.logo_right"))  # type: ignore[attr-defined]
        self.logo_right_edit.setPlaceholderText(t("home.placeholder.logo_right"))
        self.btn_logo_r.setToolTip(t("home.btn.logo_right"))
        self.field_logo_l.field_label.setText(t("home.label.logo_left"))  # type: ignore[attr-defined]
        self.logo_left_edit.setPlaceholderText(t("home.placeholder.logo_left"))
        self.btn_logo_l.setToolTip(t("home.btn.logo_left"))
        self.field_footer.field_label.setText(t("home.label.footer"))  # type: ignore[attr-defined]
        self.footer_edit.setPlaceholderText(t("home.placeholder.footer"))
        self.clear_inputs_btn.setText(t("home.btn.clear"))
        self.clear_inputs_btn.setToolTip(t("home.tooltip.clear"))
        self.shortcut_hint.setText(t("home.shortcut_hint"))
        self.start_btn.setText(t("home.btn.start"))
        self.start_btn.setToolTip(t("home.tooltip.start"))
        self.cancel_btn.setText(t("home.btn.cancel"))
        self.cancel_btn.setToolTip(t("home.tooltip.cancel"))
        self.open_out_btn.setText(t("home.btn.open_output"))
        self.log_title.setText(t("home.log.title"))
        self._set_status(self._status_state)

    def _message_box(self) -> QMessageBox:
        box = QMessageBox(self)
        box.setLayoutDirection(dialog_direction())
        return box

    def _set_status(self, state: str, text: str | None = None) -> None:
        self._status_state = state
        labels = {
            "idle": t("home.status.idle"),
            "ready": t("home.status.ready"),
            "running": t("home.status.running"),
            "error": t("home.status.error"),
            "done": t("home.status.done"),
        }
        self.status_label.setProperty("state", state)
        self.status_label.setText(text or labels.get(state, state))
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def load_from_settings(self) -> None:
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
        data["ui_language"] = self.parent_window.settings.get("ui_language", "fa")
        data["slide_language_mode"] = self.parent_window.settings.get("slide_language_mode", "same_as_ui")
        data["slide_language"] = self.parent_window.settings.get("slide_language", "fa")
        return BuildSettings.from_dict(data)

    def _browse_root(self) -> None:
        start = self.root_edit.text().strip() or str(Path.home() / "Desktop")
        path = QFileDialog.getExistingDirectory(self, t("home.file_dialog.root"), start)
        if path:
            self.root_edit.setText(path)
            self._set_status("ready")

    def _browse_logo(self, target: QLineEdit) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            t("home.file_dialog.logo"),
            "",
            t("home.file_filter.images"),
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
        box = self._message_box()
        box.setWindowTitle(t("home.dialog.clear.title"))
        box.setText(t("home.dialog.clear.text"))
        box.setInformativeText(t("home.dialog.clear.info"))
        yes_btn = box.addButton(t("home.dialog.clear.btn"), QMessageBox.ButtonRole.DestructiveRole)
        no_btn = box.addButton(t("home.dialog.cancel"), QMessageBox.ButtonRole.RejectRole)
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
        direct = root / folder_name
        if direct.is_dir():
            found.extend(sorted(direct.glob("*.pptx")))
        seen: set[Path] = set()
        unique: list[Path] = []
        for p in found:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        return unique

    def _show_success_dialog(self, output_dir: str) -> None:
        box = self._message_box()
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle(t("home.dialog.success.title"))
        folder_name = self.parent_window.settings.get("output_folder_name", "Output_PPTX")
        pptx_files = self._collect_created_pptx(output_dir)
        input_dir = self.root_edit.text().strip()
        box.setText(t("home.dialog.success.text"))
        if self._last_placement == "per_folder":
            where = t("home.dialog.success.per_folder", folder=folder_name)
        else:
            where = t("home.dialog.success.central", path=output_dir)
        box.setInformativeText(f"{where}\n\n{t('home.dialog.success.count', count=len(pptx_files))}")
        open_out_btn = box.addButton(t("home.dialog.success.open_out"), QMessageBox.ButtonRole.ActionRole)
        open_in_btn = None
        if input_dir and Path(input_dir).is_dir():
            open_in_btn = box.addButton(t("home.dialog.success.open_in"), QMessageBox.ButtonRole.ActionRole)
        open_pptx_btn = None
        if len(pptx_files) == 1:
            open_pptx_btn = box.addButton(t("home.dialog.success.open_pptx"), QMessageBox.ButtonRole.ActionRole)
        elif len(pptx_files) > 1:
            open_pptx_btn = box.addButton(t("home.dialog.success.open_first_pptx"), QMessageBox.ButtonRole.ActionRole)
        close_btn = box.addButton(t("home.dialog.close"), QMessageBox.ButtonRole.AcceptRole)
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
        box = self._message_box()
        box.setWindowTitle(t("home.dialog.placement.title"))
        box.setText(t("home.dialog.placement.text", count=job_count))
        box.setInformativeText(t("home.dialog.placement.info"))
        per_btn = box.addButton(t("home.dialog.placement.per_folder"), QMessageBox.ButtonRole.AcceptRole)
        central_btn = box.addButton(t("home.dialog.placement.central"), QMessageBox.ButtonRole.ActionRole)
        cancel_btn = box.addButton(t("home.dialog.cancel"), QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(per_btn)
        box.exec()
        clicked = box.clickedButton()
        if clicked is cancel_btn or clicked is None:
            return None
        if clicked is central_btn:
            return "central"
        return "per_folder"

    def _ask_conflict_mode(self, existing: list[Path]) -> ConflictMode | None:
        box = self._message_box()
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setWindowTitle(t("home.dialog.conflict.title"))
        count = len(existing)
        preview = "\n".join(f"• {p.parent.name}/{p.name}" for p in existing[:6])
        if count > 6:
            preview += f"\n{t('home.dialog.conflict.more', count=count - 6)}"
        box.setText(t("home.dialog.conflict.text", count=count))
        box.setInformativeText(t("home.dialog.conflict.info", preview=preview))
        replace_btn = box.addButton(t("home.dialog.conflict.replace"), QMessageBox.ButtonRole.DestructiveRole)
        version_btn = box.addButton(t("home.dialog.conflict.version"), QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = box.addButton(t("home.dialog.cancel"), QMessageBox.ButtonRole.RejectRole)
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
            QMessageBox.warning(
                self,
                t("home.dialog.invalid_path.title"),
                t("home.dialog.invalid_path.text"),
            )
            self._set_status("error", t("home.status.invalid_path"))
            return

        folder_name = self.parent_window.settings.get("output_folder_name", "Output_PPTX")
        try:
            jobs = scan_jobs(Path(root), folder_name)
        except (NotADirectoryError, OSError) as exc:
            QMessageBox.warning(self, t("home.dialog.error.title"), str(exc))
            self._set_status("error")
            return
        if not jobs:
            QMessageBox.warning(
                self,
                t("home.dialog.no_images.title"),
                t("home.dialog.no_images.text"),
            )
            self._set_status("error", t("home.status.no_images"))
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
        self.log_view.append(t("home.log.preparing"))
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
        self.log_view.append(t("home.log.error_prefix", message=message))
        self._set_status("error")

    def _cancel(self) -> None:
        if self.worker:
            self.worker.cancel()
            self.log_view.append(t("home.log.cancel_request"))
            self._set_status("running", t("home.status.stopping"))

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
            self._set_status("error", t("home.status.build_failed"))

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
