# راهنمای ساخت و انتشار

[English](BUILD.md) · [بازگشت به README](../README.fa.md)

ساخت **EXE تک‌فایل** `Pics2PPT.exe`.

---

## ساخت سریع

```bat
build.bat
```

خروجی: `dist\Pics2PPT.exe` (~۵۰–۵۵ مگ با UPX)

---

## مراحل `build.bat`

| مرحله | عمل |
|-------|-----|
| ۱ | نصب requirements |
| ۲ | UPX در `tools\upx\` |
| ۳ | پاکسازی build/dist |
| ۴ | PyInstaller با spec |
| ۵ | تأیید **فقط یک فایل** در dist |

---

## spec (تک‌فایل)

`Pics2PPT.portable.spec`

| تنظیم | مقدار |
|-------|-------|
| ورودی | `pics2ppt_entry.py` |
| نوع | one-file (نه onedir) |
| console | False |
| icon | `icon.ico` |
| upx | True |

---

## تأیید

```powershell
Get-ChildItem dist
# فقط Pics2PPT.exe
```

---

## چک‌لیست انتشار

- [ ] نسخه در `app/__init__.py` → `1.4.0`
- [ ] CHANGELOG
- [ ] ۵۹ تست
- [ ] build.bat
- [ ] EXE در GitHub Release (نه در git)
- [ ] تگ: `v1.4.0`

---

## عیب‌یابی

| مشکل | راه‌حل |
|------|--------|
| ModuleNotFound در EXE | hiddenimport در spec |
| EXE بزرگ | UPX نصب کنید |
| SmartScreen | Run anyway یا sign |

---

## چه چیزی توزیع شود

| بله | خیر |
|-----|-----|
| `Pics2PPT.exe` | سورس کامل برای کاربر نهایی |
| لینک README | پوشه build، .venv |

GitHub = **سورس**. Release = **باینری**.
