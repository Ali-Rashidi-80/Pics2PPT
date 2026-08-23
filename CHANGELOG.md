# Changelog

All notable changes to **Pics2PPT** are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.3.0] — 2026-08-23

### Added
- Rebrand from SlideReport to **Pics2PPT**
- 3D app logo (`assets/`, `icon.ico`)
- Single-file portable build: `dist/Pics2PPT.exe`
- UPX integration in `build.bat` with auto-download fallback
- Settings migration from `.slidereport` and `.gen_powerpoint`
- Comprehensive bilingual documentation (EN default + FA)
- `app/resources.py` for dev/frozen asset resolution
- **Output placement** — per-folder (manual-style) or central batch dialog
- **Conflict handling** — Replace / New version `(2)` / Cancel before build
- Native RTL **help panel** (`help_panel.py`) replacing HTML help
- Session input privacy — folder path, footer, logos cleared each launch
- Success dialog with open output / input / PPTX actions
- **Clear inputs** button on Home tab
- `output_paths.py` module for placement and versioning
- **38 automated tests** (was 31)

### Changed
- Output EXE name: `Pics2PPT.exe` (was `SlideReport_Portable.exe`)
- Settings directory: `%USERPROFILE%\.pics2ppt`
- Settings schema: `settings_version: 4`, default theme `dark_cyan`
- README rewritten as professional bilingual docs with expanded diagrams
- Filename captions render below images (not in slide header)

---

## [1.2.0] — 2026-08-23

### Added
- SlideReport branding (later renamed)
- Three UI themes (dark cyan, dark purple, light)
- Settings/About/Help pages
- Keyboard shortcuts (Ctrl+O, F5, Esc, Ctrl+Q)
- Hover zoom via OpenXML `hlinkHover` workaround
- Section divider slides for grouped folders
- Output always inside selected input folder
- 31 automated tests

### Fixed
- Flat leaf folders with images only (no subfolders)
- Person folder with mixed root images + topic subfolders
- Numbered subfolder grouping
- Skip custom output folder during nested scans
- HiDPI deprecation warnings
- Graceful Ctrl+C / SIGINT shutdown

---

## [1.0.0] — Initial

- Core scanner + PPTX 2×2 grid builder
- Persian RTL slides with B Nazanin
- Pillow image compression
- PySide6 desktop GUI

[1.3.0]: https://github.com/YOUR_USER/Pics2PPT/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/YOUR_USER/Pics2PPT/compare/v1.0.0...v1.2.0
[1.0.0]: https://github.com/YOUR_USER/Pics2PPT/releases/tag/v1.0.0
