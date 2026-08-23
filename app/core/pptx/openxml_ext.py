"""Raw OpenXML helpers — sections (p14) and picture shadow (G6)."""

from __future__ import annotations

import uuid
from typing import Sequence

from lxml import etree
from pptx.oxml.ns import qn

P14_NS = "http://schemas.microsoft.com/office/powerpoint/2010/main"
SECTION_URI = "{521415D9-36F7-43E2-AB2F-B90AF26B5E84}"
NSMAP_P14 = {"p14": P14_NS}


def _ensure_ext_list(presentation_elm):
    ext_lst = presentation_elm.find(qn("p:extLst"))
    if ext_lst is None:
        ext_lst = etree.SubElement(presentation_elm, qn("p:extLst"))
    return ext_lst


def _remove_existing_section_ext(ext_lst) -> None:
    for ext in list(ext_lst.findall(qn("p:ext"))):
        if ext.get("uri") == SECTION_URI:
            ext_lst.remove(ext)


def _sld_id_values(prs) -> list[str]:
    """Return presentation sldId @id values in slide order."""
    sld_id_lst = prs.part._element.find(qn("p:sldIdLst"))
    if sld_id_lst is None:
        return []
    return [str(sld.get("id")) for sld in sld_id_lst.findall(qn("p:sldId"))]


def inject_p14_sections(
    prs,
    sections: Sequence[tuple[str, Sequence[int]]],
) -> int:
    """
    Inject native PowerPoint sections (p14:sectionLst).

    ``sections`` is a sequence of ``(name, slide_indices)`` where indices are
    0-based positions in ``prs.slides``.
    Returns number of sections written.
    """
    if not sections:
        return 0
    sld_ids = _sld_id_values(prs)
    if not sld_ids:
        return 0

    presentation_elm = prs.part._element
    ext_lst = _ensure_ext_list(presentation_elm)
    _remove_existing_section_ext(ext_lst)

    ext = etree.SubElement(ext_lst, qn("p:ext"))
    ext.set("uri", SECTION_URI)
    section_lst = etree.SubElement(ext, f"{{{P14_NS}}}sectionLst", nsmap=NSMAP_P14)

    written = 0
    for name, indices in sections:
        ids = []
        for idx in indices:
            if 0 <= int(idx) < len(sld_ids):
                ids.append(sld_ids[int(idx)])
        if not ids:
            continue
        section = etree.SubElement(section_lst, f"{{{P14_NS}}}section")
        section.set("name", str(name)[:255] or f"Section {written + 1}")
        section.set("id", "{" + str(uuid.uuid4()).upper() + "}")
        sld_id_lst = etree.SubElement(section, f"{{{P14_NS}}}sldIdLst")
        for sid in ids:
            sld = etree.SubElement(sld_id_lst, f"{{{P14_NS}}}sldId")
            sld.set("id", sid)
        written += 1
    return written


def sections_from_markers(
    markers: Sequence[tuple[str, int]],
    total_slides: int,
) -> list[tuple[str, list[int]]]:
    """Convert [(name, start_index), ...] to contiguous slide index ranges."""
    if total_slides <= 0 or not markers:
        return []
    ordered = sorted(markers, key=lambda m: m[1])
    result: list[tuple[str, list[int]]] = []
    for i, (name, start) in enumerate(ordered):
        start = max(0, int(start))
        end = ordered[i + 1][1] if i + 1 < len(ordered) else total_slides
        end = max(start, min(int(end), total_slides))
        result.append((name, list(range(start, end))))
    return result


def apply_outer_shadow(pic, *, blur_pt: float = 4.0, dist_pt: float = 3.0, alpha: float = 0.45) -> None:
    """Attach a soft outer shadow via a:effectLst (richer than inherit=False)."""
    sp_pr = pic._element.spPr
    # Remove existing effectLst to avoid duplicates
    for child in list(sp_pr):
        if child.tag == qn("a:effectLst"):
            sp_pr.remove(child)
    effect_lst = etree.SubElement(sp_pr, qn("a:effectLst"))
    shdw = etree.SubElement(effect_lst, qn("a:outerShdw"))
    shdw.set("blurRad", str(int(blur_pt * 12700)))
    shdw.set("dist", str(int(dist_pt * 12700)))
    shdw.set("dir", "2700000")
    shdw.set("algn", "tl")
    shdw.set("rotWithShape", "0")
    srgb = etree.SubElement(shdw, qn("a:srgbClr"))
    srgb.set("val", "000000")
    alpha_el = etree.SubElement(srgb, qn("a:alpha"))
    alpha_el.set("val", str(int(max(0.0, min(1.0, alpha)) * 100000)))
