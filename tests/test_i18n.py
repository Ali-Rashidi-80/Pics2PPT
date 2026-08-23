"""Internationalization tests (no full MainWindow unless needed)."""

from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

from app.core.models import BuildSettings
from app.core.pptx_builder import build_presentation_from_job
from app.core.scanner import scan_project_folders
from app.i18n import (
    resolve_slide_language,
    set_build_slide_language,
    set_ui_language,
    t,
    t_slide,
)
from app.i18n import catalog_en, catalog_fa
from app.i18n.locale_detect import detect, normalize
from app.services.settings import DEFAULT_SETTINGS, SETTINGS_VERSION, SettingsManager


def _write_img(folder: Path, name: str) -> Path:
    p = folder / name
    Image.new("RGB", (640, 480), (120, 140, 160)).save(p, format="JPEG", quality=90)
    return p


class TestLocaleDetect(unittest.TestCase):
    def test_normalize_fa_en(self) -> None:
        self.assertEqual(normalize("fa"), "fa")
        self.assertEqual(normalize("en"), "en")
        self.assertEqual(normalize("de"), "en")
        self.assertEqual(normalize(None), "en")

    def test_detect_returns_valid_code(self) -> None:
        code = detect()
        self.assertIn(code, {"fa", "en"})


class TestCatalogs(unittest.TestCase):
    def test_fa_en_key_parity(self) -> None:
        fa_keys = set(catalog_fa.STRINGS)
        en_keys = set(catalog_en.STRINGS)
        self.assertEqual(fa_keys, en_keys)

    def test_t_both_languages(self) -> None:
        set_ui_language("fa")
        self.assertEqual(t("nav.home"), catalog_fa.STRINGS["nav.home"])
        set_ui_language("en")
        self.assertEqual(t("nav.home"), catalog_en.STRINGS["nav.home"])

    def test_t_slide_english_section_label(self) -> None:
        set_build_slide_language("en")
        text = t_slide("pptx.section.n_of_m", n=2, m=5)
        self.assertIn("2", text)
        self.assertIn("5", text)
        self.assertNotIn("از", text)


class TestResolveSlideLanguage(unittest.TestCase):
    def test_same_as_ui_follows_ui(self) -> None:
        cfg = {"ui_language": "en", "slide_language_mode": "same_as_ui", "slide_language": "fa"}
        self.assertEqual(resolve_slide_language(cfg), "en")

    def test_fixed_mode_independent(self) -> None:
        cfg = {"ui_language": "en", "slide_language_mode": "fixed", "slide_language": "fa"}
        self.assertEqual(resolve_slide_language(cfg), "fa")


class TestSettingsV5Migration(unittest.TestCase):
    def test_v4_migration_keeps_persian(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "settings.json"
            legacy = {"settings_version": 4, "theme": "dark_cyan", "font_size": "medium"}
            path.write_text(json.dumps(legacy), encoding="utf-8")
            mgr = SettingsManager()
            mgr._path = path
            mgr._dir = Path(td)
            mgr.load()
            self.assertEqual(mgr.get("settings_version"), SETTINGS_VERSION)
            self.assertEqual(mgr.get("ui_language"), "fa")
            self.assertEqual(mgr.get("slide_language_mode"), "same_as_ui")
            self.assertFalse(mgr.needs_language_prompt())

    def test_fresh_install_has_language_keys(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            mgr = SettingsManager()
            mgr._path = Path(td) / "settings.json"
            mgr._dir = Path(td)
            mgr._legacy_dirs = []  # isolate from real legacy profiles
            mgr._data = dict(DEFAULT_SETTINGS)
            mgr._fresh_install = False
            mgr.load()
            self.assertIn(mgr.get("ui_language"), {"fa", "en"})
            self.assertEqual(mgr.get("slide_language_mode"), "same_as_ui")
            self.assertTrue(mgr.needs_language_prompt())
            mgr.confirm_ui_language("en")
            self.assertEqual(mgr.get("ui_language"), "en")
            self.assertFalse(mgr.needs_language_prompt())
            self.assertEqual(mgr.get("slide_language_mode"), "same_as_ui")
            self.assertEqual(mgr.get("slide_language"), "en")

    def test_missing_confirmed_key_v5_profile_must_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "settings.json"
            raw = {
                "settings_version": 5,
                "theme": "dark_cyan",
                "font_size": "medium",
                "ui_language": "fa",
                "slide_language_mode": "same_as_ui",
                "slide_language": "fa",
            }
            path.write_text(json.dumps(raw), encoding="utf-8")
            mgr = SettingsManager()
            mgr._path = path
            mgr._dir = Path(td)
            mgr._legacy_dirs = []
            mgr._data = dict(DEFAULT_SETTINGS)
            mgr.load()
            self.assertTrue(mgr.needs_language_prompt())
            self.assertFalse(mgr.get("ui_language_confirmed"))

    def test_v4_on_disk_auto_confirms_without_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "settings.json"
            raw = {"settings_version": 4, "theme": "dark_cyan", "font_size": "medium"}
            path.write_text(json.dumps(raw), encoding="utf-8")
            mgr = SettingsManager()
            mgr._path = path
            mgr._dir = Path(td)
            mgr._legacy_dirs = []
            mgr._data = dict(DEFAULT_SETTINGS)
            mgr.load()
            self.assertFalse(mgr.needs_language_prompt())
            self.assertTrue(mgr.get("ui_language_confirmed"))

    def test_confirm_writes_language_prefs_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            from app.services import language_prefs

            td_path = Path(td)
            mgr = SettingsManager()
            mgr._path = td_path / "settings.json"
            mgr._dir = td_path
            mgr._legacy_dirs = []
            mgr._fresh_install = True
            mgr.load()
            mgr.confirm_ui_language("en")
            self.assertTrue((td_path / "ui_language.json").is_file())
            self.assertTrue(language_prefs.is_confirmed(td_path))
            self.assertEqual(language_prefs.read_language(td_path), "en")

    def test_confirm_persists_across_reload(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            mgr = SettingsManager()
            mgr._path = Path(td) / "settings.json"
            mgr._dir = Path(td)
            mgr._legacy_dirs = []
            mgr._data = dict(DEFAULT_SETTINGS)
            mgr._fresh_install = True
            mgr.load()
            mgr.confirm_ui_language("en")
            mgr2 = SettingsManager()
            mgr2._path = mgr._path
            mgr2._dir = mgr._dir
            mgr2._legacy_dirs = []
            mgr2.load()
            self.assertFalse(mgr2.needs_language_prompt())
            self.assertEqual(mgr2.get("ui_language"), "en")

    def test_save_respects_language_prefs_when_settings_lag(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            from app.services import language_prefs

            td_path = Path(td)
            mgr = SettingsManager()
            mgr._path = td_path / "settings.json"
            mgr._dir = td_path
            mgr._legacy_dirs = []
            mgr._fresh_install = True
            mgr.load()
            mgr.confirm_ui_language("en")
            mgr._data["ui_language_confirmed"] = False
            mgr._data["ui_language"] = "fa"
            mgr.save()
            self.assertTrue(language_prefs.is_confirmed(td_path))
            mgr2 = SettingsManager()
            mgr2._path = mgr._path
            mgr2._dir = mgr._dir
            mgr2._legacy_dirs = []
            mgr2.load()
            self.assertFalse(mgr2.needs_language_prompt())
            self.assertEqual(mgr2.get("ui_language"), "en")


class TestLanguagePickerDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import sys

        from PySide6.QtWidgets import QApplication

        cls._app = QApplication.instance() or QApplication(sys.argv)

    def test_dialog_defaults_to_suggested_on_reject(self) -> None:
        from app.ui.language_dialog import LanguagePickerDialog

        dlg = LanguagePickerDialog(suggested="fa")
        dlg.reject()
        self.assertEqual(dlg.selected_language(), "fa")
        dlg.deleteLater()

    def test_legacy_without_language_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            legacy_dir = Path(td) / "legacy"
            legacy_dir.mkdir()
            (legacy_dir / "settings.json").write_text(
                json.dumps({"theme": "dark_purple", "settings_version": 3}),
                encoding="utf-8",
            )
            empty = Path(td) / "empty"
            empty.mkdir()
            mgr = SettingsManager()
            mgr._path = empty / "settings.json"
            mgr._dir = empty
            mgr._legacy_dirs = [legacy_dir]
            mgr._data = dict(DEFAULT_SETTINGS)
            mgr._fresh_install = False
            mgr.load()
            self.assertTrue(mgr.needs_language_prompt())
            self.assertFalse(bool(mgr.get("ui_language_confirmed")))

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pics2ppt_i18n_"))

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def _inspect_rtl(self, pptx_path: Path) -> bool:
        with zipfile.ZipFile(pptx_path) as zf:
            xml = zf.read("ppt/slides/slide1.xml").decode("utf-8")
        return 'rtl="1"' in xml

    def test_english_slides_ltr(self) -> None:
        d = self.tmp / "flat"
        d.mkdir()
        _write_img(d, "a.jpg")
        job = scan_project_folders(d)[0]
        out = self.tmp / "en.pptx"
        cfg = BuildSettings(slide_language="en", font_name="Calibri", enable_image_zoom=False)
        build_presentation_from_job(job, out, settings=cfg)
        self.assertFalse(self._inspect_rtl(out))

    def test_persian_slides_rtl(self) -> None:
        d = self.tmp / "flat2"
        d.mkdir()
        _write_img(d, "a.jpg")
        job = scan_project_folders(d)[0]
        out = self.tmp / "fa.pptx"
        cfg = BuildSettings(slide_language="fa", enable_image_zoom=False)
        build_presentation_from_job(job, out, settings=cfg)
        self.assertTrue(self._inspect_rtl(out))


class TestHelpPanelI18n(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import sys

        cls._app = QApplication.instance() or QApplication(sys.argv)

    def test_help_panel_english(self) -> None:
        from app import __version__
        from app.ui.help_panel import build_help_panel

        set_ui_language("en")
        panel = build_help_panel("dark_cyan", __version__, lang="en")
        self.assertEqual(panel.layoutDirection(), Qt.LayoutDirection.LeftToRight)
        headings = [
            h.text()
            for h in panel.findChildren(QLabel)
            if h.objectName() == "HelpHeading"
        ]
        self.assertTrue(any("Quick" in h or "Start" in h for h in headings))

    def test_help_panel_persian(self) -> None:
        from app import __version__
        from app.ui.help_panel import build_help_panel

        panel = build_help_panel("dark_cyan", __version__, lang="fa")
        self.assertEqual(panel.layoutDirection(), Qt.LayoutDirection.RightToLeft)
        headings = [h.text() for h in panel.findChildren(QLabel) if h.objectName() == "HelpHeading"]
        self.assertIn("شروع سریع", headings)


class TestSettingsPageFast(unittest.TestCase):
    """Settings persistence without constructing two full MainWindows."""

    @classmethod
    def setUpClass(cls) -> None:
        import sys

        cls._app = QApplication.instance() or QApplication(sys.argv)

    def test_commit_persists_theme_via_manager(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            mgr = SettingsManager()
            mgr._path = Path(td) / "settings.json"
            mgr._dir = Path(td)
            mgr.load()
            mgr.set("theme", "dark_purple")
            mgr.save()

            mgr2 = SettingsManager()
            mgr2._path = mgr._path
            mgr2._dir = mgr._dir
            mgr2.load()
            self.assertEqual(mgr2.get("theme"), "dark_purple")


if __name__ == "__main__":
    unittest.main(verbosity=2)
