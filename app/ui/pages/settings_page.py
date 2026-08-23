"""Settings page."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.ui.theme import THEME_LABELS
from app.ui.widgets import FormComboBox, make_page_header


class SettingsPage(QWidget):
    def __init__(self, parent_window) -> None:
        super().__init__()
        self.parent_window = parent_window
        self._building = False
        self._build_ui()
        self.load_values()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        body = QWidget()
        root = QVBoxLayout(body)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(14)
        root.addWidget(make_page_header("تنظیمات", "ظاهر برنامه، کیفیت تصویر و رفتار ساخت پاورپوینت را اینجا تنظیم کنید."))

        appearance = QGroupBox("ظاهر برنامه")
        af = QFormLayout(appearance)
        af.setLabelAlignment(Qt.AlignRight)
        self.theme_combo = FormComboBox()
        self.theme_combo.set_items([(k, v) for k, v in THEME_LABELS.items()])
        self.theme_combo.setToolTip("تم تیره فیروزه‌ای، تیره ارغوانی یا روشن")
        self.font_combo = FormComboBox()
        self.font_combo.set_items([
            ("small", "کوچک"),
            ("medium", "متوسط"),
            ("large", "بزرگ"),
        ])
        af.addRow("تم:", self.theme_combo)
        af.addRow("اندازهٔ متن:", self.font_combo)
        root.addWidget(appearance)

        output = QGroupBox("خروجی")
        of = QFormLayout(output)
        of.setLabelAlignment(Qt.AlignRight)
        self.output_name = QLineEdit()
        self.output_name.setPlaceholderText("Output_PPTX")
        self.output_name.setToolTip("نام پوشهٔ خروجی داخل همان مسیر ورودی")
        self.open_when_done = QCheckBox("پس از اتمام، پوشهٔ خروجی باز شود")
        of.addRow("نام پوشه خروجی:", self.output_name)
        of.addRow("", self.open_when_done)
        root.addWidget(output)

        quality = QGroupBox("کیفیت تصویر")
        qf = QFormLayout(quality)
        qf.setLabelAlignment(Qt.AlignRight)
        self.jpeg_quality = QSpinBox()
        self.jpeg_quality.setRange(40, 95)
        self.jpeg_quality.setToolTip("کیفیت فشرده‌سازی JPEG (پیشنهاد: ۷۵)")
        self.max_dim = QSpinBox()
        self.max_dim.setRange(600, 2400)
        self.max_dim.setSingleStep(100)
        self.max_dim.setToolTip("حداکثر ابعاد تصویر قبل از درج در PPTX")
        qf.addRow("کیفیت JPEG:", self.jpeg_quality)
        qf.addRow("حداکثر پیکسل:", self.max_dim)
        root.addWidget(quality)

        slide = QGroupBox("اسلاید")
        sf = QFormLayout(slide)
        sf.setLabelAlignment(Qt.AlignRight)
        self.images_per = QSpinBox()
        self.images_per.setRange(1, 4)
        self.images_per.setToolTip("تعداد تصویر در هر اسلید (شبکه ۲×۲ = ۴)")
        self.font_name = QLineEdit()
        self.font_name.setPlaceholderText("B Nazanin")
        sf.addRow("تصویر در هر اسلاید:", self.images_per)
        sf.addRow("فونت:", self.font_name)
        root.addWidget(slide)

        features = QGroupBox("قابلیت‌های پاورپوینت")
        fl = QVBoxLayout(features)
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
        root.addWidget(features)

        btns = QHBoxLayout()
        reset = QPushButton("بازنشانی پیش‌فرض")
        reset.setObjectName("GhostBtn")
        reset.clicked.connect(self._reset)
        btns.addWidget(reset)
        btns.addStretch()
        root.addLayout(btns)
        root.addStretch()

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

    def _sync_hover_enabled(self) -> None:
        enabled = self.zoom_click.isChecked()
        self.zoom_hover.setEnabled(enabled)
        if not enabled and self.zoom_hover.isChecked():
            self.zoom_hover.setChecked(False)

    def _changed(self) -> None:
        if self._building:
            return
        s = self.parent_window.settings
        s.set("theme", self.theme_combo.current_key())
        s.set("font_size", self.font_combo.current_key())
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
        if not self.zoom_click.isChecked() and self.zoom_hover.isChecked():
            self._building = True
            self.zoom_hover.setChecked(False)
            self._building = False
        s.set("enable_image_shadow", self.image_shadow.isChecked())
        s.set("enable_image_border", self.image_border.isChecked())
        s.set("caption_from_filename", self.caption_name.isChecked())
        s.save()
        self._sync_hover_enabled()
        self.parent_window.apply_preferences()

    def _reset(self) -> None:
        self.parent_window.settings.reset()
        self.load_values()
        self.parent_window.apply_preferences()
