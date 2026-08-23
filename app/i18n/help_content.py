"""Structured help content for FA and EN."""

from __future__ import annotations

from typing import Any

HelpSection = dict[str, Any]


def get_help_sections(lang: str) -> list[HelpSection]:
    if lang == "en":
        return _SECTIONS_EN
    return _SECTIONS_FA


_SECTIONS_FA: list[HelpSection] = [
    {"type": "heading", "text": "شروع سریع"},
    {
        "type": "numbered",
        "items": [
            "در تب «ساخت گزارش»، پوشهٔ ورودی را انتخاب کنید یا بکشید و رها کنید.",
            "در صورت نیاز لوگو و متن پاورقی را تنظیم کنید.",
            "«شروع ساخت» را بزنید (یا کلید F5).",
            "اگر چند گزارش ساخته شود، محل ذخیره را انتخاب کنید: داخل هر پوشه یا یکجا.",
            "اگر فایل قبلی وجود داشته باشد، بین جایگزین و نسخه جدید یکی را برگزینید.",
            "پیشرفت را در «گزارش عملیات» دنبال کنید.",
        ],
    },
    {
        "type": "tip",
        "text": (
            "پیشنهاد: برای ساخت همهٔ گزارش‌ها یکجا، همان پوشهٔ ریشهٔ پروژه را انتخاب کنید "
            "(پوشه‌ای که زیرپوشه‌های تصویری داخل آن هستند)."
        ),
    },
    {"type": "heading", "text": "محل ذخیرهٔ خروجی"},
    {
        "type": "paragraph",
        "text": "نام زیرپوشهٔ خروجی پیش‌فرض Output_PPTX است و در تنظیمات قابل تغییر است.",
    },
    {
        "type": "table",
        "headers": ["گزینه", "مسیر نمونه", "کاربرد"],
        "rows": [
            ["داخل هر پوشه", "unit\\Output_PPTX\\unit.pptx", "مثل کار دستی — هر فایل کنار همان پوشه"],
            ["یکجا", "root\\Output_PPTX\\unit.pptx", "همهٔ فایل‌ها در یک پوشه زیر ریشه"],
        ],
    },
    {
        "type": "paragraph",
        "text": (
            "اگر فقط یک پوشه انتخاب شود، خروجی همان‌جا ساخته می‌شود و سؤال «یکجا / داخل هر پوشه» "
            "معمولاً مطرح نمی‌شود."
        ),
    },
    {"type": "heading", "text": "ساختار پوشه‌ها"},
    {"type": "paragraph", "text": "برنامه این الگوها را به‌صورت خودکار تشخیص می‌دهد:"},
    {
        "type": "table",
        "headers": ["الگو", "ساختار", "نتیجه"],
        "rows": [
            ["پوشهٔ تخت", "عکس‌ها مستقیم داخل یک پوشه", "یک PPTX ساده"],
            ["واحد + موضوعات", "زیرپوشه‌های موضوعی", "یک PPTX با بخش‌بندی"],
            ["گروه شماره‌دار", "زیرپوشه‌های 1/، 2/", "بخش‌های «گروه ۱»، «گروه ۲»"],
            ["ریشهٔ پروژه", "چند پوشهٔ سطح اول", "یک PPTX برای هر پوشهٔ سطح اول"],
        ],
    },
    {
        "type": "code",
        "text": (
            "ProjectRoot/\n"
            "├── Team_Alpha/          → Team_Alpha.pptx\n"
            "├── SiteVisit/           → SiteVisit.pptx\n"
            "└── Output_PPTX/         ← skipped"
        ),
    },
    {"type": "warn", "text": "پوشهٔ خروجی (Output_PPTX) هرگز به‌عنوان ورودی اسکن نمی‌شود."},
    {"type": "heading", "text": "زبان رابط و اسلاید"},
    {
        "type": "bullet",
        "items": [
            "در تنظیمات می‌توانید زبان رابط (فارسی / English) را تغییر دهید.",
            "زبان محتوای اسلاید می‌تواند «همان زبان رابط» یا جداگانه فارسی/English باشد.",
            "اسلاید فارسی: RTL و B Nazanin — اسلاید English: LTR و Calibri.",
        ],
    },
    {"type": "heading", "text": "میانبرهای صفحه‌کلید"},
    {
        "type": "table",
        "headers": ["کلید", "عمل"],
        "rows": [
            ["Ctrl+O", "انتخاب پوشهٔ ورودی"],
            ["F5", "شروع ساخت"],
            ["Esc", "توقف"],
            ["Ctrl+Q", "خروج"],
        ],
    },
    {"type": "heading", "text": "سؤالات متداول"},
    {"type": "subheading", "text": "اینترنت لازم است؟"},
    {"type": "paragraph", "text": "خیر. برنامه کاملاً آفلاین کار می‌کند."},
]

_SECTIONS_EN: list[HelpSection] = [
    {"type": "heading", "text": "Quick start"},
    {
        "type": "numbered",
        "items": [
            "On Build Report, select or drag-and-drop the input folder.",
            "Optionally set logos and footer text.",
            "Press Start build (or F5).",
            "For multiple jobs, choose inside each folder or central output.",
            "If files exist, choose Replace, New version, or Cancel.",
            "Watch progress in the Activity log.",
        ],
    },
    {
        "type": "tip",
        "text": "Tip: select the project root containing all unit subfolders to batch-build every report.",
    },
    {"type": "heading", "text": "Output location"},
    {
        "type": "paragraph",
        "text": "Default output subfolder is Output_PPTX (configurable in Settings).",
    },
    {
        "type": "table",
        "headers": ["Option", "Sample path", "Use case"],
        "rows": [
            ["Inside each folder", "unit\\Output_PPTX\\unit.pptx", "Manual-style — file beside source photos"],
            ["Central", "root\\Output_PPTX\\unit.pptx", "All decks in one folder under root"],
        ],
    },
    {"type": "heading", "text": "Folder patterns"},
    {"type": "paragraph", "text": "The scanner auto-detects these layouts:"},
    {
        "type": "table",
        "headers": ["Pattern", "Structure", "Result"],
        "rows": [
            ["Flat", "Images directly in one folder", "One simple PPTX"],
            ["Unit + topics", "Topic subfolders", "One grouped PPTX"],
            ["Numbered groups", "Subfolders 1/, 2/", "Sections Group 1, Group 2"],
            ["Project root", "Multiple first-level folders", "One PPTX per top-level folder"],
        ],
    },
    {
        "type": "code",
        "text": (
            "ProjectRoot/\n"
            "├── Team_Alpha/          → Team_Alpha.pptx\n"
            "├── SiteVisit/           → SiteVisit.pptx\n"
            "└── Output_PPTX/         ← skipped"
        ),
    },
    {"type": "warn", "text": "The output folder (Output_PPTX) is never scanned as input."},
    {"type": "heading", "text": "UI & slide language"},
    {
        "type": "bullet",
        "items": [
            "Change UI language (Persian / English) in Settings.",
            "Slide content can follow UI or be set separately (Persian / English).",
            "Persian slides: RTL + B Nazanin. English slides: LTR + Calibri.",
        ],
    },
    {"type": "heading", "text": "Keyboard shortcuts"},
    {
        "type": "table",
        "headers": ["Key", "Action"],
        "rows": [
            ["Ctrl+O", "Select input folder"],
            ["F5", "Start build"],
            ["Esc", "Cancel"],
            ["Ctrl+Q", "Quit"],
        ],
    },
    {"type": "heading", "text": "FAQ"},
    {"type": "subheading", "text": "Need internet?"},
    {"type": "paragraph", "text": "No. The app works fully offline."},
]
