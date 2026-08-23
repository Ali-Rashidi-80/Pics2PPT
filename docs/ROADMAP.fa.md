# نقشه راه توسعه

[English](ROADMAP.md) · [بازگشت به README](../README.fa.md)

جهت رسمی توسعه موتور PPTX در **Pics2PPT**.

---

## هدف

بهترین ابزار **پوشه عکس → گزارش PPTX فارسی RTL** با:

- **Hybrid Smart** (قالب + fallback کد)
- **Expert Panel** (کنترل کامل)
- python-pptx + OpenXML + Pillow
- **QA** خودکار

---

## استراتژی اصلی: Hybrid Smart

| حالت | رفتار |
|------|--------|
| `auto` (پیش‌فرض) | قالب معتبر → Template؛ وگرنه → Code |
| `template` | فقط قالب؛ خطا اگر نباشد |
| `code` | فقط موتور کد (مثل نسخه فعلی) |

**Animation/Transition:** فقط در مسیر Template (در PowerPoint طراحی شده).

**COM:** Phase 4 اختیاری — Windows + PowerPoint نصب.

---

## Expert Panel

تب **خروجی PPTX** — preset برای کاربر ساده، Expert برای حرفه‌ای.

---

## فازها

| فاز | محتوا | وضعیت |
|-----|-------|--------|
| **۰** | Refactor، HybridEngine، settings v6، Expert پایه، docs | انجام شد |
| **۱** | TemplateLoader + قالب پیش‌فرض + fallback | انجام شد |
| **۲** | metadata، EXIF، OpenXML، validator | انجام شد |
| **۳** | Expert کامل، import قالب، preset، ۵۰+ تست | انجام شد |
| **۴** | COM اختیاری، پیش‌نمایش LibreOffice، پلاگین | انجام شد |

جزئیات: [PPTX_CAPABILITIES.md](PPTX_CAPABILITIES.fa.md)

---

## معیار موفقیت

- بدون قالب هم build موفق
- Animation با قالب حفظ شود
- ۳۱ → ۵۰+ تست
- validator در هر build

---

## آنچه وعده نمی‌دهیم

- Animation در مسیر Code (محدودیت python-pptx)
- Render اسلاید به PNG در هسته
- EXE macOS/Linux در فاز فعلی
