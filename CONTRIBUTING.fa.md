# مشارکت در Pics2PPT

[English](CONTRIBUTING.md)

از مشارکت شما سپاسگزاریم. این پروژه توسط **Ali Rashidi** نگهداری می‌شود.

---

## روش‌های مشارکت

| نوع | نحوه |
|-----|------|
| گزارش باگ | Issue با مراحل بازتولید + ساختار پوشه نمونه |
| ایده قابلیت | Issue با توضیح use case |
| مستندات | PR روی `README.md`، `docs/`، `README.fa.md` |
| کد | Fork → branch → PR با تست |

---

## راه‌اندازی توسعه

```bash
git clone https://github.com/YOUR_USER/Pics2PPT.git
cd Pics2PPT
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## اصول کد

1. **سبک موجود** — type hint، dataclass، متن فارسی RTL برای UI
2. **حداقل تغییر** — یک موضوع در هر PR
3. **بدون مسیر شخصی** — در تست و placeholder
4. **تست الزامی** برای scanner/builder/worker:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

5. **مستندات** — اول انگلیسی، سپس فارسی

---

## چک‌لیست PR

- [ ] ۳۸ تست پاس
- [ ] README/docs به‌روز
- [ ] بدون secret یا داده شخصی
- [ ] متن فارسی UI صحیح

---

## مجوز

مشارکت‌ها تحت [MIT License](LICENSE) منتشر می‌شوند.
