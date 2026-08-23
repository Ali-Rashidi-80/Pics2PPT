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

from app.i18n import t
from app.ui.widgets import FormComboBox, make_page_header, make_stacked_field, make_tip_card
from app.ui.layout_direction import ALIGN_START, mark_path_field
from app.ui.scroll_area import RtlScrollArea, make_page_layout


class SettingsPage(QWidget):
    SLIDE_LANG_KEYS = ("same_as_ui", "fa", "en")

    def __init__(self, parent_window) -> None:
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.parent_window = parent_window
        self._building = True
        self._build_ui()
        self.load_values()
        self.retranslate_ui()
        self._building = False

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll = RtlScrollArea()
        body = QWidget()
        root = make_page_layout(body)

        self.page_header = make_page_header("", "")
        root.addWidget(self.page_header)
        self.tip_card = make_tip_card("")
        root.addWidget(self.tip_card)

        appearance = QGroupBox()
        ap_layout = QVBoxLayout(appearance)
        ap_layout.setSpacing(10)
        self.ap_hint = QLabel()
        self.ap_hint.setObjectName("GroupHint")
        self.ap_hint.setWordWrap(True)
        self.ap_hint.setAlignment(ALIGN_START)
        ap_layout.addWidget(self.ap_hint)

        self.theme_combo = FormComboBox()
        self.font_combo = FormComboBox()
        self.ui_lang_combo = FormComboBox()
        self.slide_lang_combo = FormComboBox()

        self.field_theme = make_stacked_field("", self.theme_combo)
        self.field_font = make_stacked_field("", self.font_combo)
        self.field_ui_lang = make_stacked_field("", self.ui_lang_combo)
        self.field_slide_lang = make_stacked_field("", self.slide_lang_combo)
        ap_layout.addWidget(self.field_theme)
        ap_layout.addWidget(self.field_font)
        ap_layout.addWidget(self.field_ui_lang)
        ap_layout.addWidget(self.field_slide_lang)
        self.appearance_group = appearance
        root.addWidget(appearance)

        output = QGroupBox()
        out_layout = QVBoxLayout(output)
        out_layout.setSpacing(10)
        self.out_hint = QLabel()
        self.out_hint.setObjectName("GroupHint")
        self.out_hint.setWordWrap(True)
        self.out_hint.setAlignment(ALIGN_START)
        out_layout.addWidget(self.out_hint)
        self.output_name = QLineEdit()
        mark_path_field(self.output_name)
        self.open_when_done = QCheckBox()
        self.field_output = make_stacked_field("", self.output_name)
        out_layout.addWidget(self.field_output)
        out_layout.addWidget(self.open_when_done)
        self.output_group = output
        root.addWidget(output)

        quality = QGroupBox()
        q_layout = QVBoxLayout(quality)
        q_layout.setSpacing(10)
        self.q_hint = QLabel()
        self.q_hint.setObjectName("GroupHint")
        self.q_hint.setWordWrap(True)
        self.q_hint.setAlignment(ALIGN_START)
        q_layout.addWidget(self.q_hint)
        self.jpeg_quality = QSpinBox()
        self.jpeg_quality.setRange(40, 95)
        self.max_dim = QSpinBox()
        self.max_dim.setRange(600, 2400)
        self.max_dim.setSingleStep(100)
        self.field_jpeg = make_stacked_field("", self.jpeg_quality)
        self.field_max_dim = make_stacked_field("", self.max_dim)
        q_layout.addWidget(self.field_jpeg)
        q_layout.addWidget(self.field_max_dim)
        self.quality_group = quality
        root.addWidget(quality)

        slide = QGroupBox()
        s_layout = QVBoxLayout(slide)
        s_layout.setSpacing(10)
        self.images_per = QSpinBox()
        self.images_per.setRange(1, 4)
        self.font_name = QLineEdit()
        mark_path_field(self.font_name)
        self.field_images_per = make_stacked_field("", self.images_per)
        self.field_font_name = make_stacked_field("", self.font_name)
        s_layout.addWidget(self.field_images_per)
        s_layout.addWidget(self.field_font_name)
        self.slide_group = slide
        root.addWidget(slide)

        features = QGroupBox()
        f_layout = QVBoxLayout(features)
        self.f_hint = QLabel()
        self.f_hint.setObjectName("GroupHint")
        self.f_hint.setWordWrap(True)
        self.f_hint.setAlignment(ALIGN_START)
        f_layout.addWidget(self.f_hint)
        fl = QVBoxLayout()
        fl.setSpacing(6)
        self.section_div = QCheckBox()
        self.zoom_click = QCheckBox()
        self.zoom_hover = QCheckBox()
        self.image_shadow = QCheckBox()
        self.image_border = QCheckBox()
        self.caption_name = QCheckBox()
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
        self.features_group = features
        root.addWidget(features)

        btns = QHBoxLayout()
        self.reset_btn = QPushButton()
        self.reset_btn.setObjectName("GhostBtn")
        self.reset_btn.clicked.connect(self._reset)
        btns.addWidget(self.reset_btn)
        btns.addStretch()
        root.addLayout(btns)

        self.scroll.setWidget(body)
        outer.addWidget(self.scroll)

        widgets = [
            self.theme_combo,
            self.font_combo,
            self.ui_lang_combo,
            self.slide_lang_combo,
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

    def _signal_widgets(self):
        return (
            self.theme_combo,
            self.font_combo,
            self.ui_lang_combo,
            self.slide_lang_combo,
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
        )

    def _block_widget_signals(self) -> None:
        for w in self._signal_widgets():
            w.blockSignals(True)

    def _unblock_widget_signals(self) -> None:
        for w in self._signal_widgets():
            w.blockSignals(False)

    def apply_direction(self, rtl: bool) -> None:
        self.scroll.apply_direction(rtl)

    def retranslate_ui(self) -> None:
        self.page_header.title_label.setText(t("settings.title"))  # type: ignore[attr-defined]
        self.page_header.subtitle_label.setText(t("settings.subtitle"))  # type: ignore[attr-defined]
        self.tip_card.body_label.setText(t("settings.tip"))  # type: ignore[attr-defined]
        self.appearance_group.setTitle(t("settings.group.appearance"))
        self.ap_hint.setText(t("settings.appearance.hint"))
        self.field_theme.field_label.setText(t("settings.label.theme"))  # type: ignore[attr-defined]
        self.field_font.field_label.setText(t("settings.label.font_size"))  # type: ignore[attr-defined]
        self.field_ui_lang.field_label.setText(t("settings.label.ui_language"))  # type: ignore[attr-defined]
        self.field_slide_lang.field_label.setText(t("settings.label.slide_language"))  # type: ignore[attr-defined]
        self._populate_theme_combo()
        self._populate_font_combo()
        self._populate_ui_lang_combo()
        self._populate_slide_lang_combo(preserve=True)
        self.output_group.setTitle(t("settings.group.output"))
        self.out_hint.setText(t("settings.output.hint"))
        self.field_output.field_label.setText(t("settings.label.output_folder"))  # type: ignore[attr-defined]
        self.output_name.setPlaceholderText(t("settings.placeholder.output_folder"))
        self.open_when_done.setText(t("settings.open_when_done"))
        self.quality_group.setTitle(t("settings.group.quality"))
        self.q_hint.setText(t("settings.quality.hint"))
        self.field_jpeg.field_label.setText(t("settings.label.jpeg"))  # type: ignore[attr-defined]
        self.field_max_dim.field_label.setText(t("settings.label.max_dim"))  # type: ignore[attr-defined]
        self.slide_group.setTitle(t("settings.group.slide"))
        self.field_images_per.field_label.setText(t("settings.label.images_per"))  # type: ignore[attr-defined]
        self.field_font_name.field_label.setText(t("settings.label.font_name"))  # type: ignore[attr-defined]
        self.font_name.setPlaceholderText(t("settings.placeholder.font_name"))
        self.features_group.setTitle(t("settings.group.features"))
        self.f_hint.setText(t("settings.features.hint"))
        self.section_div.setText(t("settings.section_div"))
        self.zoom_click.setText(t("settings.zoom_click"))
        self.zoom_hover.setText(t("settings.zoom_hover"))
        self.image_shadow.setText(t("settings.image_shadow"))
        self.image_border.setText(t("settings.image_border"))
        self.caption_name.setText(t("settings.caption_name"))
        self.reset_btn.setText(t("settings.btn.reset"))

    def _populate_theme_combo(self) -> None:
        key = self.theme_combo.current_key() if not self._building else None
        self.theme_combo.blockSignals(True)
        try:
            self.theme_combo.set_items([
                ("dark_cyan", t("theme.dark_cyan")),
                ("dark_purple", t("theme.dark_purple")),
                ("light", t("theme.light")),
            ])
            if key:
                self.theme_combo.set_current_key(key)
        finally:
            self.theme_combo.blockSignals(False)

    def _populate_font_combo(self) -> None:
        key = self.font_combo.current_key() if not self._building else None
        self.font_combo.blockSignals(True)
        try:
            self.font_combo.set_items([
                ("small", t("font.small")),
                ("medium", t("font.medium")),
                ("large", t("font.large")),
            ])
            if key:
                self.font_combo.set_current_key(key)
        finally:
            self.font_combo.blockSignals(False)

    def _populate_ui_lang_combo(self) -> None:
        key = self.ui_lang_combo.current_key() if not self._building else None
        self.ui_lang_combo.blockSignals(True)
        try:
            self.ui_lang_combo.set_items([
                ("fa", t("settings.lang.fa")),
                ("en", t("settings.lang.en")),
            ])
            if key:
                self.ui_lang_combo.set_current_key(key)
        finally:
            self.ui_lang_combo.blockSignals(False)

    def _populate_slide_lang_combo(self, *, preserve: bool = False) -> None:
        current = self.slide_lang_combo.currentData() if preserve and not self._building else None
        self.slide_lang_combo.blockSignals(True)
        try:
            self.slide_lang_combo.set_items([
                ("same_as_ui", t("settings.lang.same_as_ui")),
                ("fa", t("settings.lang.fa")),
                ("en", t("settings.lang.en")),
            ])
            if preserve and current is not None:
                idx = self.slide_lang_combo.findData(current)
                if idx >= 0:
                    self.slide_lang_combo.setCurrentIndex(idx)
        finally:
            self.slide_lang_combo.blockSignals(False)

    def _slide_lang_selection(self) -> tuple[str, str]:
        key = str(self.slide_lang_combo.currentData() or "same_as_ui")
        if key == "same_as_ui":
            return "same_as_ui", self.ui_lang_combo.current_key() or "fa"
        return "fixed", key

    def load_values(self) -> None:
        was_building = self._building
        self._building = True
        self._block_widget_signals()
        try:
            s = self.parent_window.settings
            self._populate_theme_combo()
            self._populate_font_combo()
            self._populate_ui_lang_combo()
            self._populate_slide_lang_combo()
            self.theme_combo.set_current_key(s.get("theme", "dark_cyan"))
            self.font_combo.set_current_key(s.get("font_size", "medium"))
            self.ui_lang_combo.set_current_key(s.get("ui_language", "fa"))
            mode = s.get("slide_language_mode", "same_as_ui")
            if mode == "same_as_ui":
                self.slide_lang_combo.set_current_key("same_as_ui")
            else:
                self.slide_lang_combo.set_current_key(s.get("slide_language", "fa"))
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
        finally:
            self._unblock_widget_signals()
            self._building = was_building

    def commit(self) -> None:
        from app.services import language_prefs

        s = self.parent_window.settings
        keep_confirmed = s._data.get("ui_language_confirmed")
        if language_prefs.is_confirmed(s._dir):
            keep_confirmed = True
        theme = self.theme_combo.current_key() or "dark_cyan"
        font_size = self.font_combo.current_key() or "medium"
        if theme not in {"dark_cyan", "dark_purple", "light"}:
            theme = "dark_cyan"
        if font_size not in {"small", "medium", "large"}:
            font_size = "medium"
        slide_mode, slide_lang = self._slide_lang_selection()
        s.set("theme", theme)
        s.set("font_size", font_size)
        s.set("ui_language", self.ui_lang_combo.current_key() or "fa")
        s.set("slide_language_mode", slide_mode)
        s.set("slide_language", slide_lang)
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
        if keep_confirmed is True:
            s.set("ui_language_confirmed", True)
        s.save()

    def _sync_hover_enabled(self) -> None:
        enabled = self.zoom_click.isChecked()
        self.zoom_hover.setEnabled(enabled)
        if not enabled and self.zoom_hover.isChecked():
            self.zoom_hover.setChecked(False)

    def _changed(self) -> None:
        if self._building:
            return
        if not getattr(self.parent_window, "stack", None):
            return
        if not self.zoom_click.isChecked() and self.zoom_hover.isChecked():
            self._building = True
            self.zoom_hover.blockSignals(True)
            try:
                self.zoom_hover.setChecked(False)
            finally:
                self.zoom_hover.blockSignals(False)
            self._building = False
        self.commit()
        self._sync_hover_enabled()
        self.parent_window.apply_preferences()

    def _reset(self) -> None:
        self.parent_window.settings.reset()
        self.load_values()
        self.parent_window.apply_preferences()
