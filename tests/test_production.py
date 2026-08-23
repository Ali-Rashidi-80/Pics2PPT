"""Production-readiness tests — edge cases and runtime bootstrap."""

from __future__ import annotations

import signal
import sys
import tempfile
import unittest
import warnings
from pathlib import Path

from PIL import Image

from app.bootstrap import configure_hidpi, install_sigint_handler, is_frozen
from app.core.image_processor import compress_image_to_bytes
from app.core.models import BuildSettings
from app.core.pptx_builder import build_presentation_from_job
from app.core.scanner import scan_project_folders
from app.core.worker import PresentationWorker


def _img(folder: Path, name: str, mode="RGB", size=(400, 300)) -> Path:
    p = folder / name
    if mode == "RGBA":
        Image.new("RGBA", size, (255, 0, 0, 128)).save(p, format="PNG")
    else:
        Image.new("RGB", size, (10, 20, 30)).save(p, format="JPEG")
    return p


class TestBootstrap(unittest.TestCase):
    def test_configure_hidpi_no_deprecation(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            configure_hidpi()
        deprecated = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertEqual(deprecated, [], [str(w.message) for w in deprecated])

    def test_is_frozen_false_in_dev(self) -> None:
        self.assertFalse(is_frozen())

    @classmethod
    def setUpClass(cls) -> None:
        from PySide6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication(sys.argv)

    def test_sigint_handler_quits_app(self) -> None:
        from PySide6.QtWidgets import QApplication
        from app.ui.main_window import MainWindow

        app = QApplication.instance()
        win = MainWindow()
        install_sigint_handler(app, win)
        handler = signal.getsignal(signal.SIGINT)
        self.assertIsNotNone(handler)
        win.close()

    def test_request_shutdown_without_error(self) -> None:
        from app.ui.main_window import MainWindow

        win = MainWindow()
        try:
            win.request_shutdown()
        except KeyboardInterrupt:
            self.fail("request_shutdown must not propagate KeyboardInterrupt")


class TestImageProcessor(unittest.TestCase):
    def test_png_rgba_converts_to_jpeg_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = _img(Path(td), "alpha.png", mode="RGBA")
            buf = compress_image_to_bytes(p, max_dimension=800, jpeg_quality=70)
            self.assertGreater(buf.getbuffer().nbytes, 100)
            self.assertTrue(buf.getvalue()[:2] == b"\xff\xd8")  # JPEG magic


class TestScannerEdgeCases(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="gp_edge_"))

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_invalid_root_raises(self) -> None:
        with self.assertRaises(NotADirectoryError):
            scan_project_folders(self.tmp / "nope")

    def test_empty_folder_returns_empty(self) -> None:
        empty = self.tmp / "empty"
        empty.mkdir()
        self.assertEqual(scan_project_folders(empty), [])

    def test_png_files_accepted(self) -> None:
        d = self.tmp / "pngdir"
        d.mkdir()
        _img(d, "x.png", mode="RGBA")
        jobs = scan_project_folders(d)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(len(jobs[0].groups[0].images), 1)

    def test_output_inside_person_folder_skipped(self) -> None:
        person = self.tmp / "person"
        person.mkdir()
        _img(person, "a.jpg")
        topic = person / "topic"
        topic.mkdir()
        _img(topic, "b.jpg")
        out = person / "Output_PPTX"
        out.mkdir()
        _img(out, "skip.jpg")
        jobs = scan_project_folders(person, skip_dir_names={"Output_PPTX"})
        self.assertEqual(len(jobs), 1)
        self.assertEqual(len(jobs[0].groups), 2)


class TestWorkerFailures(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PySide6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication(sys.argv)

    def test_worker_reports_no_images(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "empty"
            root.mkdir()
            worker = PresentationWorker(str(root), BuildSettings())
            errors: list[str] = []
            finished: list[tuple[bool, str]] = []
            worker.signals.error.connect(errors.append)
            worker.signals.finished.connect(lambda ok, out: finished.append((ok, out)))
            worker.run()
            self.assertTrue(errors)
            self.assertFalse(finished[0][0])

    def test_worker_cancel_flag(self) -> None:
        worker = PresentationWorker("C:\\", BuildSettings())
        worker.cancel()
        self.assertTrue(worker._cancelled())


class TestBuildSettingsClamp(unittest.TestCase):
    def test_clamps_out_of_range(self) -> None:
        cfg = BuildSettings.from_dict(
            {
                "images_per_slide": 99,
                "jpeg_quality": 10,
                "max_dimension": 9999,
            }
        )
        self.assertEqual(cfg.images_per_slide, 4)
        self.assertEqual(cfg.jpeg_quality, 40)
        self.assertEqual(cfg.max_dimension, 2400)


class TestMainEntry(unittest.TestCase):
    def test_main_import_no_deprecation_on_hidpi(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            import main  # noqa: F401

        dep = [w for w in caught if "AA_EnableHighDpiScaling" in str(w.message)]
        self.assertEqual(dep, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
