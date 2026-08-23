# User Guide

[فارسی](USER_GUIDE.fa.md) · [Back to README](../README.md)

Complete walkthrough for **Pics2PPT** end users and power users.

---

## 1. Installation options

### Portable EXE (recommended for field staff)

1. Obtain `Pics2PPT.exe` from Releases or `dist\` after building.
2. Place anywhere (Desktop, USB drive).
3. No installer, no admin required for per-user run.
4. First launch on Windows may show SmartScreen — choose **Run anyway** for unsigned community builds.

### From source (IT / developers)

Requires Python 3.11+ and pip.

```bash
pip install -r requirements.txt
python main.py
```

---

## 2. Main window overview

```text
┌─────────────────────────────────────────────────────────┐
│ Sidebar          │  Home / Settings / About             │
│ ┌──────────────┐ │                                      │
│ │ Logo Pics2PPT│ │  [Input folder path        ] [Browse]│
│ │ عکس→پاورپوینت│ │  [Footer text              ]         │
│ ├──────────────┤ │  [Logo left] [Logo right]            │
│ │ ساخت گزارش   │ │  [Start] [Cancel]                    │
│ │ تنظیمات      │ │  Progress + log                      │
│ │ درباره       │ │                                      │
│ └──────────────┘ │                                      │
└─────────────────────────────────────────────────────────┘
```

| Tab | Purpose |
|-----|---------|
| **Home** | Select folder, footer/logos per run, start build |
| **Settings** | Theme, defaults, output folder name, PPTX options |
| **About** | Version, native RTL help panel, folder pattern reference |

---

## 3. Workflow step by step

### Step 1 — Prepare your photo folders

Organize images before opening Pics2PPT. See [FOLDER_PATTERNS.md](FOLDER_PATTERNS.md).

**Rules of thumb:**
- Use `.jpg` / `.png` only in leaf folders.
- Remove or ignore `.rar` archives (not scanned).
- Do not put photos only in the output folder.

### Step 2 — Select input path

| Method | Action |
|--------|--------|
| Browse | `Ctrl+O` or **Select folder** button |
| Drag & drop | Drop folder onto path field |

**What to select:**

| Your goal | Select this path |
|-----------|------------------|
| One flat topic | The folder containing images directly |
| One person with topics | The person's folder |
| Full project | The **project root** containing all person/topic folders |

### Step 3 — Optional per-run options (Home tab)

- **Footer text** — appears bottom of every slide (e.g. project title + date)
- **Logo left / right** — header logos (PNG/JPG recommended, square-ish)

Settings tab defaults apply if Home fields are empty.

### Step 4 — Start build

Press **Start** or `F5`. Progress log shows each job and file path.

Press **Cancel** or `Esc` to stop between jobs (current job may finish writing).

**Multi-job projects** (pattern 4): a dialog asks where to save:

| Choice | Result |
|--------|--------|
| **Inside each folder** (داخل هر پوشه) | `<unit>\Output_PPTX\<unit>.pptx` — manual-style |
| **Central** (یکجا) | `<selected-root>\Output_PPTX\*.pptx` |

Single-job runs use per-folder placement automatically.

**Existing PPTX conflict:** Replace · New version `(2)` · Cancel.

Use **Clear inputs** on Home to reset folder, footer, and logos without restarting.

> Session inputs (folder path, footer, logos) are **not saved** when you close the app.

### Step 5 — Open output

After success, use the dialog buttons:

- **Open output folder**
- **Open input folder**
- **Open PPTX** (or first PPTX when several were created)

Or enable **Open output when done** in Settings.

Paths depend on placement mode:

```text
Per-folder:  <unit-folder>\Output_PPTX\<unit>.pptx
Central:     <selected-root>\Output_PPTX\<job>.pptx
```

---

## 4. Settings explained

### Appearance

| Setting | Values | Effect |
|---------|--------|--------|
| Theme | dark_cyan, dark_purple, light | UI colors |
| Font size | small, medium, large | UI text scale |

### Output

| Setting | Default | Effect |
|---------|---------|--------|
| Output folder name | `Output_PPTX` | Subfolder name inside input |
| Open when done | off | Explorer opens after success |

### Slide content

| Setting | Recommendation |
|---------|----------------|
| JPEG quality 75 | Best balance for reports |
| Max dimension 1200 | Good for projection |
| Section dividers | On for multi-topic jobs |
| Click zoom | On for review meetings |
| Hover zoom | On for desktop PowerPoint |
| Shadow + border | On for print-friendly look |
| Caption from filename | On unless filenames are meaningless |

---

## 5. Presenting the generated deck

1. Open `.pptx` in **Microsoft PowerPoint** (desktop recommended).
2. Start Slideshow (`F5` in PowerPoint).
3. **Click** any grid image → jumps to detail slide.
4. **Hover** (if enabled) → same detail slide on mouse-over.

> PowerPoint Online and some viewers may not support hover actions. Click zoom always works.

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| "No images found" | Wrong folder level selected | Select folder that directly or indirectly contains images |
| Empty PPTX | All files ignored (.rar, wrong ext) | Use .jpg/.png |
| Missing Persian glyphs | B Nazanin not installed | Install font on Windows |
| Huge file size | max_dimension too high | Lower to 1200 or quality to 75 |
| Output in wrong place | Placement mode misunderstood | Re-check per-folder vs central choice at build time |
| EXE won't start | AV quarantine | Allowlist or rebuild locally |

---

## 7. Related docs

- [Folder patterns](FOLDER_PATTERNS.md)
- [FAQ](FAQ.md)
- [Build portable EXE](BUILD.md)
