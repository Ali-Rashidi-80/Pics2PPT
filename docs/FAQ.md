# Frequently Asked Questions (FAQ)

[فارسی](FAQ.fa.md) · [Back to README](../README.md)

---

## General

### What does Pics2PPT do?

It converts folders of photos into PowerPoint presentation files with a 2×2 grid layout, Persian RTL text support, and optional click/hover zoom slides.

### Is it free?

Yes. MIT License. Created by Ali Rashidi.

### Does it need internet?

No. Fully offline after install/build.

---

## Input & folders

### Which folder should I select?

| Structure | Select |
|-----------|--------|
| Photos in one folder only | That folder |
| Person with topic subfolders | Person folder |
| Multiple people/units | Project root folder |

See [FOLDER_PATTERNS.md](FOLDER_PATTERNS.md).

### Why does it say no images found?

Common causes:
1. Selected parent folder with no images in tree.
2. Only `.rar`/`.zip` present (ignored).
3. Wrong file extensions (only `.jpg`, `.jpeg`, `.png`).

### Are `.rar` archives processed?

No. Extract images first.

### What happens to photos in the output folder?

The output folder (default `Output_PPTX`) is **skipped** during scanning so generated files are not re-imported.

---

## Output

### Where are PPTX files saved?

Depends on **output placement** chosen before build (multi-job) or defaults to per-folder (single job):

| Mode | Path |
|------|------|
| **Per-folder** | `<job.source>\<Output_PPTX>\<job.name>.pptx` |
| **Central** | `<selected-root>\<Output_PPTX>\<job.name>.pptx` |

Never in the parent directory above the selected root.

### Can I change the output folder name?

Yes — Settings → output folder name. The scanner skips that name during input scan.

### Will it overwrite existing files?

Only if you choose **Replace** in the conflict dialog. **New version** writes `Name (2).pptx`, `Name (3).pptx`, etc. **Cancel** aborts the build.

---

## PowerPoint behavior

### Click zoom works but hover does not?

- Hover requires desktop Microsoft PowerPoint.
- PowerPoint Online / mobile viewers often ignore hover actions.
- Ensure **Enable hover zoom** and **Enable image zoom** are both on in Settings.

### Font looks wrong?

Install **B Nazanin** on Windows or change font in Settings.

### Section divider slides missing?

Enable **section dividers** in Settings. Job must be `grouped` (multiple sections).

---

## Application

### Settings file location?

```text
%USERPROFILE%\.pics2ppt\settings.json
```

Legacy paths (`.slidereport`, `.gen_powerpoint`) migrate automatically.

Current schema: `settings_version: 4`.

### Do folder path and footer persist after restart?

**No.** Only Settings-tab values (theme, quality, output folder name, toggles) and window geometry persist. Home-tab inputs — last folder, footer text, logo paths — are cleared on every launch for privacy on shared machines.

### Portable EXE vs source?

| | EXE | Source |
|---|-----|--------|
| Needs Python | No | Yes |
| File count | 1 | Many |
| For developers | Optional | Yes |
| For end users | **Recommended** | No |

### Windows SmartScreen warning?

Community builds are often unsigned. Click **More info → Run anyway** or build locally with `build.bat`.

### Antivirus flagged the EXE?

PyInstaller + UPX sometimes trigger heuristics. Build from source if you prefer.

---

## Development

### How to run tests?

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### How to contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Honest limitations

| Limitation | Detail |
|------------|--------|
| Windows-first | Built and tested on Windows; source may run elsewhere with manual setup |
| No macOS EXE | PyInstaller spec is Windows-oriented |
| 4 images per slide max | By design (2×2 grid) |
| No video/audio | Images only |
| No cloud sync | Manual folder copy |
| Filename captions | Stem only — no EXIF metadata captions |

We document limits openly so expectations stay realistic.
