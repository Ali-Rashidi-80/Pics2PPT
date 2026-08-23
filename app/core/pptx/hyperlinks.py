"""Click and hover slide hyperlinks."""

from pptx.opc.constants import RELATIONSHIP_TYPE as RT


def link_shape_to_slide(shape, target_slide) -> None:
    shape.click_action.target_slide = target_slide


def link_shape_hover(shape, target_slide) -> None:
    """Hover jump via OpenXML (avoids python-pptx hover ActionSetting bug)."""
    cNvPr = shape._element._nvXxPr.cNvPr
    hlink = cNvPr.get_or_add_hlinkHover()
    hlink.action = "ppaction://hlinksldjump"
    hlink.rId = shape.part.relate_to(target_slide.part, RT.SLIDE)
