# Build & Release Guide

[Persian](BUILD.fa.md) · [Back to README](../README.md)

How to produce the **single-file portable** `Pics2PPT.exe`.

---

## Quick build

```bat
build.bat
```

Output: `dist\Pics2PPT.exe` (~50–55 MB with UPX on Windows 64-bit).

---

## What `build.bat` does

| Step | Action |
|------|--------|
| 1 | `pip install -r requirements.txt` |
| 2 | Locate or download UPX 4.2.4 to `tools\upx\` |
| 3 | Clean `build\` and old `dist\Pics2PPT.exe` |
| 4 | Run PyInstaller with `Pics2PPT.portable.spec` |
| 5 | Verify **only one file** exists in `dist\` |

---

## PyInstaller spec (one-file)

File: `Pics2PPT.portable.spec`

| Setting | Value | Meaning |
|---------|-------|---------|
| Entry | `pics2ppt_entry.py` | Imports `main.main()` |
| `EXE(...)` all-in-one | binaries + datas in one file | **Not onedir** |
| `console=False` | No black terminal window |
| `icon=icon.ico` | Windows executable icon |
| `upx=True` | Compress eligible DLLs/pyd |
| `upx_exclude` | `python*.dll`, `Qt6*.dll` | Stability over size |

Bundled data:

```python
datas=[
    ("assets/app_icon_256.png", "assets"),
    ("assets/pics2ppt_logo.png", "assets"),
    ("icon.ico", "."),
]
```

---

## Manual build (without batch pause)

```bat
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --clean --upx-dir tools\upx Pics2PPT.portable.spec
```

---

## UPX notes

- UPX reduces size of many native binaries.
- Qt6 and Python DLLs are **excluded** from UPX (spec + PyInstaller heuristics).
- If UPX missing, build still succeeds — larger EXE.
- Antivirus may scan UPX-packed binaries longer — normal for portable Python apps.

---

## Verify the artifact

```powershell
# Must be exactly one file
Get-ChildItem dist

# Launch smoke test
.\dist\Pics2PPT.exe
```

Expected `dist` contents:

```text
dist/
└── Pics2PPT.exe    ← only this file
```

If you see `dist/Pics2PPT/` folder with many DLLs, the spec was changed to onedir — revert to current spec.

---

## Release checklist

- [ ] Bump `__version__` in `app/__init__.py`
- [ ] Update `CHANGELOG.md` and `CHANGELOG.fa.md`
- [ ] Run full test suite (59 tests)
- [ ] Run `build.bat` on clean machine or CI
- [ ] Smoke test EXE: select sample folder, build, open pptx
- [ ] Attach `Pics2PPT.exe` to GitHub Release (not committed to git)
- [ ] Tag: `v1.4.0`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` in EXE | Add hidden import to spec |
| Missing logo in About | Check `datas` in spec |
| EXE huge (>80 MB) | UPX unavailable — install to `tools\upx` |
| SmartScreen blocks run | Sign EXE (costly) or document "Run anyway" |
| Qt platform plugin error | Rebuild on target Windows arch (64-bit) |

---

## What NOT to ship

| Do ship | Do not ship |
|---------|-------------|
| `dist/Pics2PPT.exe` | Full git repo to end users |
| Optional sample screenshots | User photo folders |
| README link | `build/`, `.venv/`, source `.py` files |

The GitHub repository is **source**. Releases hold the **binary**.
