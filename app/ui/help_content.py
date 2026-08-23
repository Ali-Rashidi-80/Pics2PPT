"""Theme-aware HTML for Help / About page."""

from __future__ import annotations

from app.ui.theme import palette


def build_help_html(theme_id: str, app_version: str = "1.1.0") -> str:
    p = palette(theme_id)
    return f"""
<html dir="rtl" lang="fa">
<head>
<style>
body {{
  font-family: 'B Nazanin', Tahoma, sans-serif;
  color: {p['text']};
  background: transparent;
  line-height: 1.85;
  font-size: 14px;
}}
h2 {{ color: {p['accent_bright']}; margin-top: 22px; font-size: 18px; }}
h3 {{ color: {p['text']}; margin-top: 16px; font-size: 15px; }}
p, li {{ color: {p['text_secondary']}; }}
code {{ background: {p['accent_muted']}; padding: 2px 6px; border-radius: 4px; }}
.tip {{
  background: {p['accent_muted']};
  border-right: 3px solid {p['accent']};
  padding: 10px 14px;
  border-radius: 8px;
  margin: 12px 0;
}}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
td, th {{
  border: 1px solid {p['border']};
  padding: 8px 10px;
  text-align: right;
}}
th {{ background: {p['surface_hover']}; color: {p['text']}; }}
</style>
</head>
<body>
<h2>شروع سریع</h2>
<ol>
  <li>در تب «ساخت گزارش»، پوشهٔ ورودی را انتخاب یا رها کنید.</li>
  <li>لوگو و متن پاورقی را در صورت نیاز تنظیم کنید.</li>
  <li>دکمهٔ «شروع ساخت» را بزنید و پیشرفت را در گزارش عملیات دنبال کنید.</li>
  <li>خروجی در پوشهٔ <code>Output_PPTX</code> داخل همان مسیر ورودی ذخیره می‌شود.</li>
</ol>

<h2>ساختار پوشه‌ها</h2>
<table>
<tr><th>الگو</th><th>رفتار برنامه</th></tr>
<tr><td>پوشهٔ ریشه با زیرپوشه‌های تصویری</td><td>برای هر زیرپوشه یک فایل PPTX</td></tr>
<tr><td>پوشهٔ نفر + موضوعات داخلی</td><td>یک PPTX با بخش‌بندی موضوعی</td></tr>
<tr><td>پوشهٔ تخت با عکس مستقیم</td><td>یک PPTX ساده</td></tr>
<tr><td>زیرپوشه‌های شماره‌دار</td><td>گروه‌بندی «گروه ۱، گروه ۲…»</td></tr>
</table>

<h2>قابلیت‌های پاورپوینت</h2>
<ul>
  <li><b>بزرگنمایی کلیک:</b> در حالت نمایش، روی هر تصویر کلیک کنید تا اسلاید جزئیات باز شود.</li>
  <li><b>هاور:</b> با قرار دادن ماوس روی تصویر (در صورت فعال بودن در تنظیمات) همان اسلاید جزئیات نمایش داده می‌شود.</li>
  <li><b>شبکه ۲×۲:</b> حداکثر ۴ تصویر در هر اسلید با حفظ نسبت ابعاد.</li>
  <li><b>RTL فارسی:</b> متن‌ها راست‌به‌چپ با فونت B Nazanin.</li>
  <li><b>سایه و حاشیه:</b> قابل تنظیم در تب تنظیمات.</li>
</ul>

<div class="tip">
  <b>نکته:</b> برای پروژهٔ کامل، پوشهٔ ریشهٔ پروژه را انتخاب کنید
  تا همهٔ بخش‌ها به‌صورت خودکار شناسایی شوند.
</div>

<h2>تنظیمات پیشنهادی</h2>
<ul>
  <li>کیفیت JPEG: ۷۵ (تعادل حجم و کیفیت)</li>
  <li>حداکثر ابعاد: ۱۲۰۰ پیکسل</li>
  <li>تم روشن برای چاپ و تم تیره برای کار طولانی</li>
</ul>

<h2>سؤالات متداول</h2>
<h3>چرا خروجی در پوشهٔ دیگری ساخته شد؟</h3>
<p>خروجی همیشه در زیرپوشهٔ <code>Output_PPTX</code> داخل همان مسیری است که انتخاب کردید.</p>
<h3>فایل‌های rar و Thumbs.db چه می‌شوند؟</h3>
<p>نادیده گرفته می‌شوند.</p>
<h3>نسخه</h3>
<p>SlideReport v{app_version}</p>
</body>
</html>
"""
