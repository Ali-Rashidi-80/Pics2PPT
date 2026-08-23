"""Background worker for PPTX generation."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from .models import BuildSettings
from .pptx_builder import build_presentation_from_job
from .scanner import scan_project_folders


class WorkerSignals(QObject):
    progress = Signal(int)
    log = Signal(str)
    error = Signal(str)
    folder_done = Signal(str)
    finished = Signal(bool, str)  # success, output_dir


class PresentationWorker(QRunnable):
    def __init__(self, root_path: str, settings: BuildSettings) -> None:
        super().__init__()
        self.root_path = Path(root_path)
        self.settings = settings
        self.signals = WorkerSignals()
        self.is_cancelled = False
        self.setAutoDelete(True)

    def cancel(self) -> None:
        self.is_cancelled = True

    def _cancelled(self) -> bool:
        return self.is_cancelled

    @Slot()
    def run(self) -> None:
        output_dir = ""
        try:
            self.signals.log.emit(f"شروع پیمایش: {self.root_path}")
            folder_name = (self.settings.output_folder_name or "Output_PPTX").strip()
            skip_dirs = {folder_name, "Output_PPTX"}
            jobs = scan_project_folders(self.root_path, skip_dir_names=skip_dirs)
            if not jobs:
                self.signals.error.emit(
                    "هیچ تصویر معتبری (.jpg / .jpeg / .png) در این پوشه یا زیرپوشه‌هایش یافت نشد."
                )
                self.signals.finished.emit(False, "")
                return

            output_dir = str(self.root_path / folder_name)
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            self.signals.log.emit(f"پوشه خروجی: {output_dir}")
            self.signals.log.emit(f"تعداد فایل PPTX: {len(jobs)}")

            total = len(jobs)
            for index, job in enumerate(jobs):
                if self.is_cancelled:
                    self.signals.log.emit("عملیات لغو شد.")
                    self.signals.finished.emit(False, output_dir)
                    return

                mode = "گروه‌بندی موضوعی" if job.grouped else "ساده"
                sections = "، ".join(f"«{g.name}» ({len(g.images)})" for g in job.groups)
                self.signals.log.emit(f"[{index + 1}/{total}] «{job.name}» — {mode}")
                self.signals.log.emit(f"    بخش‌ها: {sections}")

                out_file = Path(output_dir) / f"{job.name}.pptx"
                try:
                    build_presentation_from_job(
                        job,
                        out_file,
                        settings=self.settings,
                        should_cancel=self._cancelled,
                    )
                    self.signals.folder_done.emit(str(out_file))
                    self.signals.log.emit(f"ذخیره شد: {out_file.name}")
                except InterruptedError:
                    self.signals.log.emit("عملیات لغو شد.")
                    self.signals.finished.emit(False, output_dir)
                    return
                except Exception as exc:
                    self.signals.error.emit(f"خطا در «{job.name}»: {exc}")

                self.signals.progress.emit(int(((index + 1) / total) * 100))

            if self.is_cancelled:
                self.signals.finished.emit(False, output_dir)
            else:
                self.signals.log.emit("تمام فایل‌ها با موفقیت ساخته شدند.")
                self.signals.progress.emit(100)
                self.signals.finished.emit(True, output_dir)
        except Exception as exc:
            self.signals.error.emit(f"خطای کلی: {exc}")
            self.signals.finished.emit(False, output_dir)
