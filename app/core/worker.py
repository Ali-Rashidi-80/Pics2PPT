"""Background worker for PPTX generation."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from app.i18n import set_build_slide_language, t

from .models import BuildSettings
from .output_paths import ConflictMode, OutputPlacement, job_output_file, resolve_output_path
from .pptx.engine import HybridEngine
from .scanner import scan_project_folders


class WorkerSignals(QObject):
    progress = Signal(int)
    log = Signal(str)
    error = Signal(str)
    folder_done = Signal(str)
    finished = Signal(bool, str)  # success, browse_dir


class PresentationWorker(QRunnable):
    def __init__(
        self,
        root_path: str,
        settings: BuildSettings,
        *,
        conflict_mode: ConflictMode = "replace",
        output_placement: OutputPlacement = "central",
    ) -> None:
        super().__init__()
        self.root_path = Path(root_path)
        self.settings = settings
        self.conflict_mode = conflict_mode
        self.output_placement = output_placement
        self._ui_lang = settings.ui_language
        self.signals = WorkerSignals()
        self.is_cancelled = False
        self.setAutoDelete(True)

    def cancel(self) -> None:
        self.is_cancelled = True

    def _cancelled(self) -> bool:
        return self.is_cancelled

    def _log(self, key: str, **kwargs: object) -> None:
        self.signals.log.emit(t(key, lang=self._ui_lang, **kwargs))

    def _err(self, key: str, **kwargs: object) -> None:
        self.signals.error.emit(t(key, lang=self._ui_lang, **kwargs))

    @Slot()
    def run(self) -> None:
        browse_dir = ""
        lang = self._ui_lang
        try:
            set_build_slide_language(self.settings.slide_language)
            self._log("worker.log.scan_start", path=self.root_path)
            folder_name = (self.settings.output_folder_name or "Output_PPTX").strip() or "Output_PPTX"
            skip_dirs = {folder_name, "Output_PPTX"}
            jobs = scan_project_folders(self.root_path, skip_dir_names=skip_dirs)
            if not jobs:
                self._err("worker.err.no_images")
                self.signals.finished.emit(False, "")
                return

            if self.output_placement == "per_folder":
                browse_dir = str(self.root_path)
                placement_label = t("worker.log.placement.per_folder", lang=lang)
            else:
                browse_dir = str(self.root_path / folder_name)
                Path(browse_dir).mkdir(parents=True, exist_ok=True)
                placement_label = t("worker.log.placement.central", lang=lang, folder=folder_name)

            self._log("worker.log.output_location", label=placement_label)
            self._log("worker.log.pptx_count", count=len(jobs))

            if self.conflict_mode == "version":
                self._log("worker.log.mode.version")
            else:
                self._log("worker.log.mode.replace")

            total = len(jobs)
            for index, job in enumerate(jobs):
                if self.is_cancelled:
                    self._log("worker.log.cancelled")
                    self.signals.finished.emit(False, browse_dir)
                    return

                mode_key = "worker.log.mode.grouped" if job.grouped else "worker.log.mode.simple"
                sections = ", ".join(
                    t("worker.log.section_item", lang=lang, name=g.name, count=len(g.images))
                    for g in job.groups
                )
                self._log(
                    "worker.log.job",
                    index=index + 1,
                    total=total,
                    name=job.name,
                    mode=t(mode_key, lang=lang),
                )
                self._log("worker.log.sections", sections=sections)

                base = job_output_file(job, self.root_path, folder_name, self.output_placement)
                base.parent.mkdir(parents=True, exist_ok=True)
                out_file = resolve_output_path(base, self.conflict_mode)
                if out_file.name != base.name:
                    self._log("worker.log.output_name", name=out_file.name)
                self._log("worker.log.output_path", path=out_file.parent)
                try:
                    result = HybridEngine().build(
                        job,
                        out_file,
                        settings=self.settings,
                        should_cancel=self._cancelled,
                    )
                    path_label = t(
                        "worker.log.build_path.template"
                        if result.path_used.value == "template"
                        else "worker.log.build_path.code",
                        lang=lang,
                    )
                    self._log("worker.log.build_path", path=path_label)
                    if result.template_path:
                        self._log("worker.log.template_used", path=result.template_path.name)
                    self.signals.folder_done.emit(str(result.output_path))
                    self._log("worker.log.saved", name=result.output_path.name)
                except InterruptedError:
                    self._log("worker.log.cancelled")
                    self.signals.finished.emit(False, browse_dir)
                    return
                except Exception as exc:
                    self._err("worker.err.job", name=job.name, exc=exc)

                self.signals.progress.emit(int(((index + 1) / total) * 100))

            if self.is_cancelled:
                self.signals.finished.emit(False, browse_dir)
            else:
                self._log("worker.log.all_done")
                self.signals.progress.emit(100)
                self.signals.finished.emit(True, browse_dir)
        except Exception as exc:
            self._err("worker.err.general", exc=exc)
            self.signals.finished.emit(False, browse_dir)
