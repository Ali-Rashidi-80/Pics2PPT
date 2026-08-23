"""Phase 2 — properties, EXIF, OpenXML sections, validator."""

from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image
from pptx import Presentation

from app.core.image_processor import compress_image_to_bytes, read_exif_caption
from app.core.models import BuildSettings, PptxOutputSettings
from app.core.pptx.engine import HybridEngine
from app.core.pptx.openxml_ext import inject_p14_sections, sections_from_markers
from app.core.pptx.properties import apply_core_properties
from app.core.pptx.validator import validate_pptx, write_build_report
from app.core.scanner import ImageGroup, PresentationJob, scan_project_folders


def _write_img(folder: Path, name: str) -> Path:
    path = folder / name
    Image.new("RGB", (40, 30), color=(90, 110, 130)).save(path)
    return path


class TestCoreProperties(unittest.TestCase):
    def test_core_properties_on_build(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        d = tmp / "flat"
        d.mkdir()
        _write_img(d, "a.jpg")
        job = scan_project_folders(d)[0]
        out = tmp / "out.pptx"
        cfg = PptxOutputSettings(
            output_mode="code",
            doc_title="My Title",
            doc_author="Tester",
            write_build_report=True,
            enable_image_zoom=False,
        )
        result = HybridEngine().build(job, out, settings=cfg)
        prs = Presentation(str(result.output_path))
        self.assertEqual(prs.core_properties.title, "My Title")
        self.assertEqual(prs.core_properties.author, "Tester")
        self.assertIn("Pics2PPT", prs.core_properties.comments or "")
        self.assertTrue(result.report_path and result.report_path.is_file())
        payload = json.loads(result.report_path.read_text(encoding="utf-8"))
        self.assertTrue(payload["validation"]["ok"])


class TestNativeSections(unittest.TestCase):
    def test_sections_from_markers(self) -> None:
        ranges = sections_from_markers([("A", 0), ("B", 3)], 7)
        self.assertEqual(ranges[0], ("A", [0, 1, 2]))
        self.assertEqual(ranges[1], ("B", [3, 4, 5, 6]))

    def test_inject_p14_in_grouped_build(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        root = tmp / "person"
        g1 = root / "topic1"
        g2 = root / "topic2"
        g1.mkdir(parents=True)
        g2.mkdir(parents=True)
        _write_img(g1, "a.jpg")
        _write_img(g2, "b.jpg")
        jobs = scan_project_folders(tmp)
        self.assertTrue(jobs)
        job = jobs[0]
        self.assertTrue(job.grouped)
        out = tmp / "grouped.pptx"
        cfg = PptxOutputSettings(
            output_mode="code",
            enable_section_dividers=True,
            enable_native_sections=True,
            enable_image_zoom=False,
            write_build_report=False,
        )
        HybridEngine().build(job, out, settings=cfg)
        with zipfile.ZipFile(out) as zf:
            xml = zf.read("ppt/presentation.xml")
        self.assertIn(b"sectionLst", xml)


class TestValidator(unittest.TestCase):
    def test_validate_and_report(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        d = tmp / "x"
        d.mkdir()
        _write_img(d, "a.jpg")
        job = scan_project_folders(d)[0]
        out = tmp / "v.pptx"
        HybridEngine().build(
            job,
            out,
            settings=PptxOutputSettings(output_mode="code", write_build_report=False, enable_image_zoom=False),
        )
        result = validate_pptx(out)
        self.assertTrue(result.ok)
        self.assertGreaterEqual(result.metrics.get("slide_count", 0), 1)
        report = write_build_report(out, validation=result, extra={"path_used": "code"})
        self.assertTrue(report.is_file())


class TestExifPipeline(unittest.TestCase):
    def test_compress_auto_rotate_runs(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        path = _write_img(tmp, "plain.jpg")
        buf = compress_image_to_bytes(path, auto_rotate=True, strip_gps=True)
        self.assertGreater(len(buf.getvalue()), 0)

    def test_read_exif_caption_empty_for_plain(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        path = _write_img(tmp, "plain.jpg")
        self.assertEqual(read_exif_caption(path), "")


class TestApplyPropertiesUnit(unittest.TestCase):
    def test_apply_core_properties_direct(self) -> None:
        prs = Presentation()
        job = PresentationJob(
            name="Job",
            source=Path("."),
            groups=[ImageGroup(name="G", images=[])],
            grouped=False,
        )
        apply_core_properties(prs, job, BuildSettings(), path_used="code")
        self.assertEqual(prs.core_properties.title, "Job")


if __name__ == "__main__":
    unittest.main()
