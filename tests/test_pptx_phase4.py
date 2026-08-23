"""Phase 4 — optional COM, LibreOffice preview, plugin hooks."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from app.core.models import PptxOutputSettings
from app.core.pptx.com_postprocess import com_postprocess_pptx, powerpoint_available
from app.core.pptx.engine import HybridEngine
from app.core.pptx.libreoffice_preview import export_preview, find_soffice, libreoffice_available
from app.core.pptx.plugins import (
    HOOK_AFTER_BUILD,
    PluginRegistry,
    load_plugins_from_dir,
)
from app.core.pptx.postprocess import run_post_build_pipeline
from app.core.scanner import scan_project_folders


def _write_img(folder: Path, name: str) -> Path:
    path = folder / name
    Image.new("RGB", (32, 24), color=(70, 90, 110)).save(path)
    return path


class TestComPostprocess(unittest.TestCase):
    def test_skips_without_file(self) -> None:
        result = com_postprocess_pptx(Path(tempfile.mkdtemp()) / "missing.pptx")
        self.assertFalse(result.ok)
        self.assertFalse(result.skipped)

    def test_skips_gracefully_when_unavailable(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        d = tmp / "flat"
        d.mkdir()
        _write_img(d, "a.jpg")
        job = scan_project_folders(d)[0]
        out = tmp / "out.pptx"
        HybridEngine().build(
            job,
            out,
            settings=PptxOutputSettings(output_mode="code", write_build_report=False, enable_image_zoom=False),
        )
        with patch("app.core.pptx.com_postprocess.sys.platform", "linux"):
            result = com_postprocess_pptx(out)
        self.assertTrue(result.ok)
        self.assertTrue(result.skipped)


class TestLibreOfficePreview(unittest.TestCase):
    def test_skips_when_soffice_missing(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        pptx = tmp / "x.pptx"
        pptx.write_bytes(b"PK\x03\x04fake")
        with patch("app.core.pptx.libreoffice_preview.find_soffice", return_value=None):
            result = export_preview(pptx)
        self.assertTrue(result.ok)
        self.assertTrue(result.skipped)

    def test_find_soffice_type(self) -> None:
        found = find_soffice()
        self.assertTrue(found is None or found.is_file())


class TestPlugins(unittest.TestCase):
    def test_registry_runs_and_isolates_errors(self) -> None:
        reg = PluginRegistry()
        seen = []

        def ok_hook(**kwargs):
            seen.append(kwargs.get("path"))

        def bad_hook(**kwargs):
            raise RuntimeError("boom")

        reg.register(HOOK_AFTER_BUILD, ok_hook)
        reg.register(HOOK_AFTER_BUILD, bad_hook)
        warnings = reg.run(HOOK_AFTER_BUILD, path=Path("a.pptx"))
        self.assertEqual(seen, [Path("a.pptx")])
        self.assertEqual(len(warnings), 1)
        self.assertIn("boom", warnings[0])

    def test_load_plugins_from_dir(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plugin = root / "sample.py"
            plugin.write_text(
                "def register(registry):\n"
                "    registry.register('after_build', lambda **kw: None)\n",
                encoding="utf-8",
            )
            reg = PluginRegistry()
            count = load_plugins_from_dir(root, registry=reg)
            self.assertEqual(count, 1)
            self.assertEqual(len(reg._hooks.get(HOOK_AFTER_BUILD, [])), 1)


class TestPostProcessPipeline(unittest.TestCase):
    def test_pipeline_with_flags_off(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        d = tmp / "flat"
        d.mkdir()
        _write_img(d, "a.jpg")
        job = scan_project_folders(d)[0]
        out = tmp / "out.pptx"
        cfg = PptxOutputSettings(
            output_mode="code",
            write_build_report=False,
            enable_image_zoom=False,
            enable_com_postprocess=False,
            enable_libreoffice_preview=False,
            enable_plugins=False,
        )
        result = HybridEngine().build(job, out, settings=cfg)
        self.assertIsNotNone(result.postprocess)
        self.assertIsNone(result.postprocess.com)
        self.assertIsNone(result.postprocess.preview)

    def test_pipeline_skips_optional_tools(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        d = tmp / "flat"
        d.mkdir()
        _write_img(d, "a.jpg")
        job = scan_project_folders(d)[0]
        out = tmp / "out.pptx"
        HybridEngine().build(
            job,
            out,
            settings=PptxOutputSettings(output_mode="code", write_build_report=False, enable_image_zoom=False),
        )
        cfg = PptxOutputSettings(
            enable_com_postprocess=True,
            enable_libreoffice_preview=True,
            enable_plugins=False,
        )
        with patch("app.core.pptx.postprocess.com_postprocess_pptx") as com_mock, patch(
            "app.core.pptx.postprocess.export_preview"
        ) as prev_mock:
            from app.core.pptx.com_postprocess import ComResult
            from app.core.pptx.libreoffice_preview import PreviewResult

            com_mock.return_value = ComResult(ok=True, skipped=True, message="skip com", output_path=out)
            prev_mock.return_value = PreviewResult(ok=True, skipped=True, message="skip lo")
            post = run_post_build_pipeline(out, job, cfg)
        self.assertTrue(post.com.skipped)
        self.assertTrue(post.preview.skipped)


class TestAvailabilityHelpers(unittest.TestCase):
    def test_availability_bools(self) -> None:
        self.assertIsInstance(powerpoint_available(), bool)
        self.assertIsInstance(libreoffice_available(), bool)


if __name__ == "__main__":
    unittest.main()
