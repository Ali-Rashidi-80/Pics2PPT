"""Settings page."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QLabel,
)

from app.ui.theme import THEME_LABELS
from app.ui.widgets import FormComboBox, make_page_header, make_stacked_field, make_tip_card
from app.ui.layout_direction import ALIGN_START, mark_path_field
from app.ui.scroll_area import RtlScrollArea, make_page_layout


class SettingsPage(QWidget):
    def __init__(self, parent_window) -> None:
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.parent_window = parent_window
        self._building = False
        self._build_ui()
        self.load_values()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = RtlScrollArea()
        body = QWidget()
        root = make_page_layout(body)
        root.addWidget(
            make_page_header(
                "تنظیمات",
                "ظاهر برنامه، کیفیت تصویر و رفتار ساخت پاورپوینت را اینجا تنظیم کنید. "
                "تغییرات به‌صورت خودکار ذخیره می‌شوند.",
            )
        )

        root.addWidget(
            make_tip_card("تم و اندازهٔ متن را می‌توانید متناسب با محیط کار (روشن یا تیره) تغییر دهید.")
        )

        appearance = QGroupBox("ظاهر برنامه")
        ap_layout = QVBoxLayout(appearance)
        ap_layout.setSpacing(10)
        ap_hint = QLabel("تم تیره برای کار طولانی و تم روشن برای چاپ و نمایش بهتر متن مناسب است.")
        ap_hint.setObjectName("GroupHint")
        ap_hint.setWordWrap(True)
        ap_hint.setAlignment(ALIGN_START)
        ap_layout.addWidget(ap_hint)
        self.theme_combo = FormComboBox()
        self.theme_combo.set_items([(k, v) for k, v in THEME_LABELS.items()])
        self.font_combo = FormComboBox()
        self.font_combo.set_items([
            ("small", "کوچک"),
            ("medium", "متوسط"),
            ("large", "بزرگ"),
        ])
        ap_layout.addWidget(make_stacked_field("تم:", self.theme_combo))
        ap_layout.addWidget(make_stacked_field("اندازهٔ متن:", self.font_combo))
        root.addWidget(appearance)

        output = QGroupBox("خروجی")
        out_layout = QVBoxLayout(output)
        out_layout.setSpacing(10)
        out_hint = QLabel("فایل‌های PPTX همیشه در زیرپوشه‌ای داخل همان مسیر ورودی ذخیره می‌شوند.")
        out_hint.setObjectName("GroupHint")
        out_hint.setWordWrap(True)
        out_hint.setAlignment(ALIGN_START)
        out_layout.addWidget(out_hint)
        self.output_name = QLineEdit()
        self.output_name.setPlaceholderText("Output_PPTX")
        mark_path_field(self.output_name)
        self.open_when_done = QCheckBox("پس از اتمام، پوشهٔ خروجی باز شود")
        out_layout.addWidget(make_stacked_field("نام پوشه خروجی:", self.output_name))
        out_layout.addWidget(self.open_when_done)
        root.addWidget(output)

        quality = QGroupBox("کیفیت تصویر")
        q_layout = QVBoxLayout(quality)
        q_layout.setSpacing(10)
        q_hint = QLabel("مقادیر پیشنهادی: JPEG ۷۵ و حداکثر ۱۲۰۰ پیکسل — تعادل مناسب حجم و کیفیت.")
        q_hint.setObjectName("GroupHint")
        q_hint.setWordWrap(True)
        q_hint.setAlignment(ALIGN_START)
        q_layout.addWidget(q_hint)
        self.jpeg_quality = QSpinBox()
        self.jpeg_quality.setRange(40, 95)
        self.max_dim = QSpinBox()
        self.max_dim.setRange(600, 2400)
        self.max_dim.setSingleStep(100)
        q_layout.addWidget(make_stacked_field("کیفیت JPEG:", self.jpeg_quality))
        q_layout.addWidget(make_stacked_field("حداکثر پیکسل:", self.max_dim))
        root.addWidget(quality)

        slide = QGroupBox("اسلاید")
        s_layout = QVBoxLayout(slide)
        s_layout.setSpacing(10)
        self.images_per = QSpinBox()
        self.images_per.setRange(1, 4)
        self.font_name = QLineEdit()
        self.font_name.setPlaceholderText("B Nazanin")
        mark_path_field(self.font_name)
        s_layout.addWidget(make_stacked_field("تصویر در هر اسلاید:", self.images_per))
        s_layout.addWidget(make_stacked_field("فونت:", self.font_name))
        root.addWidget(slide)

        features = QGroupBox("قابلیت‌های پاورپوینت")
        f_layout = QVBoxLayout(features)
        f_hint = QLabel("بزرگنمایی کلیک/هاور اسلاید جزئیات جداگانه برای هر تصویر می‌سازد.")
        f_hint.setObjectName("GroupHint")
        f_hint.setWordWrap(True)
        f_hint.setAlignment(ALIGN_START)
        f_layout.addWidget(f_hint)
        fl = QVBoxLayout()
        fl.setSpacing(6)
        self.section_div = QCheckBox("اسلاید جداکنندهٔ بخش‌ها")
        self.zoom_click = QCheckBox("بزرگنمایی با کلیک (اسلاید جزئیات)")
        self.zoom_hover = QCheckBox("بزرگنمایی با هاور ماوس")
        self.image_shadow = QCheckBox("سایهٔ تصاویر")
        self.image_border = QCheckBox("حاشیهٔ تصاویر")
        self.caption_name = QCheckBox("عنوان سلول از نام فایل")
        for w in (
            self.section_div,
            self.zoom_click,
            self.zoom_hover,
            self.image_shadow,
            self.image_border,
            self.caption_name,
        ):
            fl.addWidget(w)
        f_layout.addLayout(fl)
        root.addWidget(features)

        btns = QHBoxLayout()
        reset = QPushButton("بازنشانی پیش‌فرض")
        reset.setObjectName("GhostBtn")
        reset.clicked.connect(self._reset)
        btns.addWidget(reset)
        btns.addStretch()
        root.addLayout(btns)

        scroll.setWidget(body)
        outer.addWidget(scroll)

        widgets = [
            self.theme_combo,
            self.font_combo,
            self.output_name,
            self.open_when_done,
            self.jpeg_quality,
            self.max_dim,
            self.images_per,
            self.font_name,
            self.section_div,
            self.zoom_click,
            self.zoom_hover,
            self.image_shadow,
            self.image_border,
            self.caption_name,
        ]
        for w in widgets:
            if hasattr(w, "currentIndexChanged"):
                w.currentIndexChanged.connect(self._changed)
            elif hasattr(w, "valueChanged"):
                w.valueChanged.connect(self._changed)
            elif hasattr(w, "textChanged"):
                w.textChanged.connect(self._changed)
            elif hasattr(w, "toggled"):
                w.toggled.connect(self._changed)

    def load_values(self) -> None:
        self._building = True
        s = self.parent_window.settings
        self.theme_combo.set_current_key(s.get("theme", "dark_cyan"))
        self.font_combo.set_current_key(s.get("font_size", "medium"))
        self.output_name.setText(s.get("output_folder_name", "Output_PPTX"))
        self.open_when_done.setChecked(bool(s.get("open_output_when_done")))
        self.jpeg_quality.setValue(int(s.get("jpeg_quality", 75)))
        self.max_dim.setValue(int(s.get("max_dimension", 1200)))
        self.images_per.setValue(int(s.get("images_per_slide", 4)))
        self.font_name.setText(s.get("font_name", "B Nazanin"))
        self.section_div.setChecked(bool(s.get("enable_section_dividers", True)))
        self.zoom_click.setChecked(bool(s.get("enable_image_zoom", True)))
        self.zoom_hover.setChecked(bool(s.get("enable_hover_zoom", True)))
        self.image_shadow.setChecked(bool(s.get("enable_image_shadow", True)))
        self.image_border.setChecked(bool(s.get("enable_image_border", True)))
        self.caption_name.setChecked(bool(s.get("caption_from_filename", True)))
        self._sync_hover_enabled()
        self._building = False

    def commit(self) -> None:
        """Write current widget values to settings (used on close)."""
        s = self.parent_window.settings
        theme = self.theme_combo.current_key() or "dark_cyan"
        font_size = self.font_combo.current_key() or "medium"
        if theme not in {"dark_cyan", "dark_purple", "light"}:
            theme = "dark_cyan"
        if font_size not in {"small", "medium", "large"}:
            font_size = "medium"
        s.set("theme", theme)
        s.set("font_size", font_size)
        s.set("output_folder_name", self.output_name.text().strip() or "Output_PPTX")
        s.set("open_output_when_done", self.open_when_done.isChecked())
        s.set("jpeg_quality", self.jpeg_quality.value())
        s.set("max_dimension", self.max_dim.value())
        s.set("images_per_slide", self.images_per.value())
        s.set("font_name", self.font_name.text().strip() or "B Nazanin")
        s.set("enable_section_dividers", self.section_div.isChecked())
        s.set("enable_image_zoom", self.zoom_click.isChecked())
        hover = self.zoom_hover.isChecked() and self.zoom_click.isChecked()
        s.set("enable_hover_zoom", hover)
        s.set("enable_image_shadow", self.image_shadow.isChecked())
        s.set("enable_image_border", self.image_border.isChecked())
        s.set("caption_from_filename", self.caption_name.isChecked())
        s.save()

    def _sync_hover_enabled(self) -> None:
        enabled = self.zoom_click.isChecked()
        self.zoom_hover.setEnabled(enabled)
        if not enabled and self.zoom_hover.isChecked():
            self.zoom_hover.setChecked(False)

    def _changed(self) -> None:
        if self._building:
            return
        if not self.zoom_click.isChecked() and self.zoom_hover.isChecked():
            self._building = True
            self.zoom_hover.setChecked(False)
            self._building = False
        self.commit()
        self._sync_hover_enabled()
        self.parent_window.apply_preferences()

    def _reset(self) -> None:
        self.parent_window.settings.reset()
        self.load_values()
        self.parent_window.apply_preferences()
