"""Native RTL help panel for the About page (no QTextBrowser HTML)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.ui.layout_direction import ALIGN_START, ALIGN_START_TOP
from app.ui.theme import palette


def _heading(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("HelpHeading")
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START)
    return lbl


def _subheading(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("HelpSubheading")
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START)
    return lbl


def _paragraph(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("HelpParagraph")
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START_TOP)
    return lbl


def _list_item(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("HelpParagraph")
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START_TOP)
    lbl.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    return lbl


def _bullet_list(items: list[str]) -> QWidget:
    box = QWidget()
    box.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    for item in items:
        layout.addWidget(_list_item(f"• {item}"))
    return box


def _numbered_list(items: list[str]) -> QWidget:
    box = QWidget()
    box.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    for index, item in enumerate(items, start=1):
        layout.addWidget(_list_item(f"{index}. {item}"))
    return box


def _tip(text: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName("HelpTip")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 12, 14, 12)
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START_TOP)
    lbl.setObjectName("HelpParagraph")
    layout.addWidget(lbl)
    return frame


def _warn(text: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName("HelpWarn")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 12, 14, 12)
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setAlignment(ALIGN_START_TOP)
    lbl.setObjectName("HelpParagraph")
    layout.addWidget(lbl)
    return frame


def _code_block(text: str) -> QPlainTextEdit:
    edit = QPlainTextEdit()
    edit.setObjectName("HelpCode")
    edit.setReadOnly(True)
    edit.setPlainText(text)
    edit.setFixedHeight(min(180, 16 + text.count("\n") * 18))
    edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    edit.setProperty("forceLtr", True)
    return edit


def _path_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("HelpPath")
    lbl.setWordWrap(True)
    lbl.setProperty("forceLtr", True)
    lbl.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    return lbl


def _table(headers: list[str], rows: list[list[str | QWidget]]) -> QFrame:
    frame = QFrame()
    frame.setObjectName("HelpTable")
    frame.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    grid = QGridLayout(frame)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(0)
    grid.setVerticalSpacing(0)

    cols = len(headers)
    for col, title in enumerate(headers):
        head = QLabel(title)
        head.setObjectName("HelpTableHeader")
        head.setWordWrap(True)
        head.setAlignment(ALIGN_START_TOP)
        grid.addWidget(head, 0, col)

    for row_idx, row in enumerate(rows, start=1):
        for col, cell in enumerate(row):
            widget: QWidget
            if isinstance(cell, QWidget):
                widget = cell
            else:
                widget = QLabel(cell)
                widget.setObjectName("HelpTableCell")
                widget.setWordWrap(True)
                widget.setAlignment(ALIGN_START_TOP)
            grid.addWidget(widget, row_idx, col)

    for col in range(cols):
        grid.setColumnStretch(col, 1)
    return frame


def build_help_panel(theme_id: str, app_version: str = "1.3.0") -> QWidget:
    """Build structured Persian RTL help content as native widgets."""
    _ = palette(theme_id)  # reserved for future per-theme inline styling

    root = QWidget()
    root.setObjectName("HelpPanel")
    root.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    layout = QVBoxLayout(root)
    layout.setContentsMargins(4, 4, 4, 12)
    layout.setSpacing(16)

    layout.addWidget(_heading("شروع سریع"))
    layout.addWidget(
        _numbered_list(
            [
                "در تب «ساخت گزارش»، پوشهٔ ورودی را انتخاب کنید یا بکشید و رها کنید.",
                "در صورت نیاز لوگو و متن پاورقی را تنظیم کنید.",
                "«شروع ساخت» را بزنید (یا کلید F5).",
                "اگر چند گزارش ساخته شود، محل ذخیره را انتخاب کنید: داخل هر پوشه یا یکجا.",
                "اگر فایل قبلی وجود داشته باشد، بین جایگزین و نسخه جدید یکی را برگزینید.",
                "پیشرفت را در «گزارش عملیات» دنبال کنید.",
            ]
        )
    )
    layout.addWidget(
        _tip(
            "پیشنهاد: برای ساخت همهٔ گزارش‌ها یکجا، همان پوشهٔ ریشهٔ پروژه را انتخاب کنید "
            "(پوشه‌ای که زیرپوشه‌های تصویری داخل آن هستند)."
        )
    )

    layout.addWidget(_heading("محل ذخیرهٔ خروجی"))
    layout.addWidget(_paragraph("نام زیرپوشهٔ خروجی پیش‌فرض Output_PPTX است و در تنظیمات قابل تغییر است."))
    layout.addWidget(
        _table(
            ["گزینه", "مسیر نمونه", "کاربرد"],
            [
                ["داخل هر پوشه", _path_label("واحد\\Output_PPTX\\واحد.pptx"), "مثل کار دستی — هر فایل کنار همان پوشه"],
                ["یکجا", _path_label("ریشه\\Output_PPTX\\واحد.pptx"), "همهٔ فایل‌ها در یک پوشه زیر ریشه"],
            ],
        )
    )
    layout.addWidget(
        _paragraph(
            "اگر فقط یک پوشه انتخاب شود، خروجی همان‌جا ساخته می‌شود و سؤال «یکجا / داخل هر پوشه» معمولاً مطرح نمی‌شود."
        )
    )

    layout.addWidget(_heading("ساختار پوشه‌ها"))
    layout.addWidget(_paragraph("برنامه این الگوها را به‌صورت خودکار تشخیص می‌دهد:"))
    layout.addWidget(
        _table(
            ["الگو", "ساختار", "نتیجه"],
            [
                ["پوشهٔ تخت", "عکس‌ها مستقیم داخل یک پوشه", "یک PPTX ساده"],
                ["واحد + موضوعات", "زیرپوشه‌های موضوعی (و اختیاری عکس در سطح واحد)", "یک PPTX با بخش‌بندی و اسلاید جداکننده"],
                ["گروه شماره‌دار", "زیرپوشه‌های 1/، 2/ و …", "یک PPTX با بخش‌های «گروه ۱»، «گروه ۲» و …"],
                ["ریشهٔ پروژه", "چند پوشهٔ سطح اول با تصویر (نام‌دار)", "یک PPTX جدا برای هر پوشهٔ سطح اول"],
            ],
        )
    )
    layout.addWidget(
        _code_block(
            "ProjectRoot/\n"
            "├── Team_Alpha/          → Team_Alpha.pptx\n"
            "│   ├── overview.jpg\n"
            "│   ├── topic_a/\n"
            "│   └── topic_b/\n"
            "├── SiteVisit/           → SiteVisit.pptx\n"
            "│   ├── photo_001.jpg\n"
            "│   └── photo_002.jpg\n"
            "└── Output_PPTX/         ← نادیده گرفته می‌شود"
        )
    )
    layout.addWidget(_warn("پوشهٔ خروجی (Output_PPTX یا نام دلخواه شما) هرگز به‌عنوان ورودی اسکن نمی‌شود."))

    layout.addWidget(_heading("فایل‌های قبلی و نسخهٔ جدید"))
    layout.addWidget(
        _bullet_list(
            [
                "جایگزین: فایل هم‌نام بازنویسی می‌شود.",
                "نسخه جدید: کنار فایل قبلی با نام‌هایی مانند نام (2).pptx و نام (3).pptx ساخته می‌شود.",
                "انصراف: ساخت لغو می‌شود.",
            ]
        )
    )

    layout.addWidget(_heading("قابلیت‌های پاورپوینت"))
    layout.addWidget(
        _bullet_list(
            [
                "بزرگنمایی با کلیک: در نمایش اسلاید، روی تصویر کلیک کنید تا اسلاید جزئیات باز شود.",
                "هاور ماوس: با قرار دادن نشانگر روی تصویر (در صورت فعال بودن) همان اسلاید جزئیات دیده می‌شود — روی PowerPoint دسکتاپ.",
                "شبکه ۲×۲: حداکثر ۴ تصویر در هر اسلاید با حفظ نسبت ابعاد.",
                "RTL فارسی: متن‌ها راست‌به‌چپ؛ فونت پیشنهادی B Nazanin.",
                "سایه و حاشیه: در تب تنظیمات قابل روشن/خاموش کردن است.",
                "عنوان از نام فایل: زیر تصویر می‌تواند نام فایل نمایش داده شود.",
            ]
        )
    )

    layout.addWidget(_heading("میانبرهای صفحه‌کلید"))
    layout.addWidget(
        _table(
            ["کلید", "عمل"],
            [
                [_path_label("Ctrl+O"), "انتخاب پوشهٔ ورودی"],
                [_path_label("F5"), "شروع ساخت"],
                [_path_label("Esc"), "توقف عملیات در حال اجرا"],
                [_path_label("Ctrl+Q"), "خروج از برنامه"],
            ],
        )
    )

    layout.addWidget(_heading("ورودی‌ها و تنظیمات"))
    layout.addWidget(
        _bullet_list(
            [
                "پاک کردن ورودی‌ها: پوشه، لوگوها و پاورقی را خالی می‌کند.",
                "مسیر پوشه و لوگو/پاورقی بین اجرای برنامه ذخیره نمی‌شوند؛ هر بار از نو وارد می‌کنید.",
                "تم، کیفیت تصویر، زوم و … در تب تنظیمات ذخیره می‌شوند و ماندگارند.",
            ]
        )
    )

    layout.addWidget(_heading("تنظیمات پیشنهادی"))
    layout.addWidget(
        _bullet_list(
            [
                "کیفیت JPEG: ۷۵ (تعادل حجم و کیفیت)",
                "حداکثر ابعاد: ۱۲۰۰ پیکسل",
                "تم تیره برای کار طولانی؛ تم روشن برای نمایش/چاپ متن",
            ]
        )
    )

    layout.addWidget(_heading("سؤالات متداول"))
    layout.addWidget(_subheading("کدام پوشه را انتخاب کنم؟"))
    layout.addWidget(
        _paragraph(
            "اگر چند واحد دارید، ریشه را انتخاب کنید تا برای هر واحد یک فایل ساخته شود. "
            "اگر فقط یک مجموعه عکس دارید، همان پوشه کافی است."
        )
    )
    layout.addWidget(_subheading("چرا عکسی پیدا نشد؟"))
    layout.addWidget(
        _bullet_list(
            [
                "سطح پوشه اشتباه انتخاب شده باشد.",
                "فقط فایل‌های فشرده (.rar / .zip) باشند — ابتدا Extract کنید.",
                "پسوند غیر از .jpg / .jpeg / .png باشد.",
            ]
        )
    )
    layout.addWidget(_subheading("فایل‌های Thumbs.db چه می‌شوند؟"))
    layout.addWidget(_paragraph("نادیده گرفته می‌شوند."))
    layout.addWidget(_subheading("هاور کار نمی‌کند؟"))
    layout.addWidget(
        _paragraph("برای هاور معمولاً PowerPoint دسکتاپ لازم است؛ نسخهٔ وب یا موبایل ممکن است هاور نداشته باشد.")
    )
    layout.addWidget(_subheading("فونت‌ها درست دیده نمی‌شوند؟"))
    layout.addWidget(_paragraph("فونت B Nazanin (یا فونت فارسی انتخابی در تنظیمات) را روی سیستم نصب کنید."))
    layout.addWidget(_subheading("اینترنت لازم است؟"))
    layout.addWidget(_paragraph("خیر. برنامه کاملاً آفلاین کار می‌کند."))
    layout.addWidget(_subheading("نسخه"))
    layout.addWidget(_paragraph(f"Pics2PPT — نسخهٔ {app_version} — سازنده: Ali Rashidi"))

    root.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
    return root
