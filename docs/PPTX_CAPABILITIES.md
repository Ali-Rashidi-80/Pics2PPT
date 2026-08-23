# PPTX Capabilities & Limits

[فارسی](PPTX_CAPABILITIES.fa.md) · [Roadmap](ROADMAP.md) · [Gap audit](PPTX_GAP_AUDIT.md)

Honest map of what **Pics2PPT** uses, plans, and **deliberately excludes** — cross-checked against [python-pptx docs](https://python-pptx.readthedocs.io/) and production literature.

---

## Strategy: Hybrid Smart

| Path | When | Animations | Branding |
|------|------|------------|----------|
| **Template** | `.pptx` template loaded | Yes (from template) | Master/theme |
| **Code** | Fallback / `output_mode=code` | No | Code + settings |

Default `auto` picks template when file exists, else code.

---

## python-pptx — official API coverage map

| API area | Today | Planned | Notes |
|----------|-------|---------|-------|
| `Presentation()` load/save | Code only | Template load | Phase 1 |
| Slide layouts / masters | No | Yes | Phase 1 |
| Placeholders by `idx` | No | Yes | Stable key per layout |
| `PicturePlaceholder.insert_picture` | No | Yes | Better than add_picture in templates |
| Placeholder crop props | No | Yes | fill vs fit — StackOverflow pattern |
| `add_textbox` + RTL OpenXML | Yes | Yes | Keep |
| Run-level text / bullets | Partial | Phase 2–3 | Never use `.text` on styled placeholders |
| `add_picture` + fit box | Yes | Yes | Code path |
| Click / hover slide jump | Yes | Yes | Hover = OpenXML |
| Line / shadow on pictures | Partial | Phase 2 | Full shadow via OpenXML |
| `core_properties` | No | Phase 2 | title, author, subject, keywords |
| Background fill | No | Phase 2 | solid / gradient |
| `add_table` / TablePlaceholder | No | Phase 3 | Index slide |
| Charts (bar/line/pie) | No | **Non-goal** | Not photo-report mission |
| Autoshapes | No | Phase 3 | Dividers, badges |
| Notes slide | No | Phase 3 | Speaker notes |
| URL hyperlinks on runs | No | Phase 2–3 | `run.hyperlink.address` |
| Group shapes | No | Low priority | — |
| SmartArt | No | **Unsupported** | python-pptx gap |
| Video / audio | No | **Non-goal** | — |

---

## OpenXML layer (beyond API)

| Feature | Status | Source |
|---------|--------|--------|
| Hover `hlinkHover` | Done | python-pptx bug workaround |
| p14 `sectionLst` | Phase 2 | [Wang blog](https://blog.wangxm.com/2026/04/adding-sections-to-powerpoint-files-with-python-and-lxml/) |
| Transition XML insert | Phase 2 optional | [GitHub #1106](https://github.com/scanny/python-pptx/issues/1106) — fragile |
| Animation timing clone | Phase 3 optional | SlideForge — shape id must match |
| ECMA-376 timing tree | Template only | [Microsoft docs](https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-animation) |

---

## Pillow + complementary Python

| Library | Role | Phase |
|---------|------|-------|
| **Pillow** | JPEG compress, resize, RGBA→RGB | Done |
| **Pillow getexif** | Basic EXIF read | Phase 2 |
| **`exif` package** | Human-readable EXIF keys | Phase 2 (optional dep) |
| **exifread** | Alternative read-only | Phase 2 fallback |
| **pydantic** | Settings validation | Phase 1–2 |
| **jinja2** | Caption/footer templates | Phase 3 |

---

## Production workflows (literature)

| Workflow | Description |
|----------|-------------|
| **Template fill** | Load designer `.pptx`, run-safe token replace, insert_picture |
| **Slide surgery** | Merge jobs, reorder, duplicate section slides |
| **Raw XML** | Sections, hover, optional transitions |

---

## Hard limits (platform — not plan holes)

| Feature | Why | Workaround |
|---------|-----|------------|
| Animation timeline in code | No API since 2018 | Template path |
| Slide transitions in code | Same | Template or fragile XML |
| Slide → PNG | No renderer in library | Phase 4 LibreOffice/COM |
| Theme color inheritance | API gaps | Explicit RGB in Expert Panel |
| Picture placeholder fidelity | crop/zoom differs from UI | insert_picture + crop math |
| Font embedding | Names only — no embed | Install B Nazanin + fallback chain (G21) |
| PowerPoint Online hover | Viewer limitation | Click zoom still works |
| python-pptx maintenance | Last release Aug 2024 | OpenXML layer + pin ≥1.0.2 (G18) |

---

## Alternatives not chosen (documented)

| Tool | Why not core |
|------|--------------|
| Aspose.Slides | Commercial, heavy |
| Google Slides API | Cloud, not offline EXE |
| pptxforge / betteroffice-pptx | Immature vs python-pptx |
| COM / win32com | Phase 4 optional only |

---

## QA requirements (from audit)

- Template round-trip: animation XML byte-stable after fill
- Run-split token tests for `{{placeholders}}`
- RTL flag on every text shape
- Validator on every build → `build_report.json`
- Template zip security limits

Full gap list: [PPTX_GAP_AUDIT.md](PPTX_GAP_AUDIT.md)

---

## Related

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [ROADMAP.md](ROADMAP.md)
