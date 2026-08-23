# Contributing to Pics2PPT

[Persian](CONTRIBUTING.fa.md)

Thank you for considering a contribution. This project is maintained by **Ali Rashidi** and welcomes bug reports, documentation improvements, and tested feature PRs.

---

## Ways to contribute

| Type | How |
|------|-----|
| Bug report | Open an issue with steps to reproduce + sample folder layout |
| Feature idea | Open an issue describing the folder/PPTX use case first |
| Documentation | PRs to `README.md`, `docs/`, or `README.fa.md` |
| Code | Fork → branch → PR with tests |

---

## Development setup

```bash
git clone https://github.com/YOUR_USER/Pics2PPT.git
cd Pics2PPT
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Code guidelines

1. **Match existing style** — dataclasses, type hints, RTL-aware UI strings in Persian where user-facing.
2. **Minimal scope** — one logical change per PR.
3. **No personal paths** — never commit real user folders, names, or machine-specific paths in tests or placeholders.
4. **Tests required** for scanner/builder/worker logic changes:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

5. **Documentation** — update EN docs first; mirror critical changes in `.fa.md` files.

---

## Project areas

| Area | Path | Notes |
|------|------|-------|
| Scanner | `app/core/scanner.py` | Folder classification — highest regression risk |
| PPTX builder | `app/core/pptx_builder.py` | OpenXML, RTL, zoom links |
| Worker | `app/core/worker.py` | Threading, progress signals |
| UI | `app/ui/` | PySide6, themes in `theme.py` |
| Settings | `app/services/settings.py` | JSON persistence |

---

## Pull request checklist

- [ ] All 38 tests pass locally
- [ ] No new linter warnings in touched files
- [ ] README or docs updated if behavior changed
- [ ] No secrets, `.env`, or personal data committed
- [ ] Persian UI strings remain grammatically correct RTL

---

## Commit messages

Use clear, imperative subjects:

```
fix(scanner): skip custom output folder in nested person scan
docs: add folder pattern diagrams to USER_GUIDE
feat(ui): remember last input directory across sessions
```

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
