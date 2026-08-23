# ممیزی شکاف PPTX — بررسی منابع وب

[English](PPTX_GAP_AUDIT.md) · [نقشه راه](ROADMAP.fa.md)

**هدف:** اطمینان از جامعیت پلن Hybrid Smart در برابر مستندات رسمی python-pptx، مقالات production، و OpenXML.

---

## نتیجه

| حوزه | قبل | بعد |
|------|-----|-----|
| Hybrid Smart | خوب | کامل |
| انضباط Template (run-level) | **نبود** | فاز ۱ |
| insert_picture + crop | جزئی | فاز ۱–۲ |
| p14 sections دقیق | برنامه بود | جزئیات XML اضافه شد |
| امنیت template | **نبود** | فاز ۱ |
| EXIF | فقط Pillow | + کتابخانه exif |

**۱۴ شکاف** شناسایی و به فازها نگاشت شد.

**پاس سوم:** G25–G36 — run-level links، filename `&`، DPI، openxml-audit، `.potx`، partial recovery، long path.

**جمع نهایی: G1–G36** — پس از **۴ پاس مستقل** (آخرین: امنیت XXE/zip، power-pptx، #961، ops)، شکاف بحرانی unmapped باقی نمانده. پاس ۴ فقط **تکمیل G13/G24/G34** — G37 جدید ندارد.

---

## پاس سوم (خلاصه)

| # | موضوع | فاز |
|---|--------|-----|
| G25 | Hyperlink سطح run (متن → اسلاید) | ۳ |
| G26 | Slide duplicate | ۳ |
| G27 | Cross-master — **محدودیت** → یک template | docs |
| G28 | **`&` در نام فایل** — BytesIO | ۰ |
| G29 | DPI-aware sizing | ۲ |
| G30 | **openxml-audit** در CI | ۲ |
| G31 | قرارداد `{{token}}` | ۱ |
| G32 | پشتیبانی `.potx` | ۱ |
| G33 | Notes/Handout master | ۳ opt |
| G34 | Resume partial build | ۳ |
| G35 | Long path / unicode Windows | ۰–۱ |
| G36 | Superscript — optional | ۴ |

---

## شکاف‌های پاس دوم (خلاصه)

| # | موضوع | فاز |
|---|--------|-----|
| G15 | RTL کامل (bidi + txBody rtl) | ۰–۲ |
| G16 | Footer/slide number از master | ۱–۲ |
| G17 | Accessibility (title، contrast، alt text) | ۲–۳ |
| G18 | python-pptx ≥ 1.0.2 | ۰ |
| G19 | compress-pptx اختیاری | ۳ |
| G20 | ooxml-validate | ۲–۳ |
| G21 | Font embed نمی‌شود — fallback chain | ۰–۲ |
| G22 | Text frame margins/auto_size | ۲ |
| G23 | pptx-slide-copier برای merge | ۳ |
| G24 | pptx-raster/Spire — خارج از core | — |

---

## سقف صادقانه (محدودیت پلتفرم)

1. Animation API در python-pptx نیست (از ۲۰۱۸)
2. render اسلاید → PNG نیاز renderer خارجی
3. SmartArt پشتیبانی نمی‌شود
4. Theme inheritance ناقص — RGB صریح
5. PowerPoint Online ممکن است hover نداشته باشد

---

## وضعیت پلن

**جامع برای مأموریت Pics2PPT.** هیچ شکاف بحرانی بدون نگاشت فاز باقی نمانده.

منابع: [python-pptx.readthedocs.io](https://python-pptx.readthedocs.io/)، SourceToDocs، SlideForge، Microsoft Open XML، GitHub #1106.
