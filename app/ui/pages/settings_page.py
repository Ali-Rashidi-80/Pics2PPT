"""Settings page."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QLabel,
)

from app.core.pptx.slide_sizes import SLIDE_SIZE_PRESETS, detect_preset, preset_dimensions
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

        pptx_out = QGroupBox()
        po_layout = QVBoxLayout(pptx_out)
        po_layout.setSpacing(10)
        self.po_hint = QLabel()
        self.po_hint.setObjectName("GroupHint")
        self.po_hint.setWordWrap(True)
        self.po_hint.setAlignment(ALIGN_START)
        po_layout.addWidget(self.po_hint)

        self.output_mode_combo = FormComboBox()
        self.template_path = QLineEdit()
        mark_path_field(self.template_path)
        self.slide_size_combo = FormComboBox()
        self.slide_width = QDoubleSpinBox()
        self.slide_width.setRange(5.0, 20.0)
        self.slide_width.setDecimals(2)
        self.slide_width.setSingleStep(0.01)
        self.slide_height = QDoubleSpinBox()
        self.slide_height.setRange(5.0, 20.0)
        self.slide_height.setDecimals(2)
        self.slide_height.setSingleStep(0.01)
        self.title_font_size = QSpinBox()
        self.title_font_size.setRange(8, 72)
        self.caption_font_size = QSpinBox()
        self.caption_font_size.setRange(6, 48)
        self.footer_font_size = QSpinBox()
        self.footer_font_size.setRange(6, 48)

        self.field_output_mode = make_stacked_field("", self.output_mode_combo)
        self.field_template_path = make_stacked_field("", self.template_path)
        tpl_row = QHBoxLayout()
        tpl_row.addWidget(self.field_template_path, stretch=1)
        self.analyze_template_btn = QPushButton()
        self.analyze_template_btn.setObjectName("GhostBtn")
        self.analyze_template_btn.clicked.connect(self._analyze_template)
        tpl_row.addWidget(self.analyze_template_btn)
        self.image_fit_combo = FormComboBox()
        self.field_image_fit = make_stacked_field("", self.image_fit_combo)
        self.field_slide_size = make_stacked_field("", self.slide_size_combo)
        self.field_slide_width = make_stacked_field("", self.slide_width)
        self.field_slide_height = make_stacked_field("", self.slide_height)
        self.field_title_font = make_stacked_field("", self.title_font_size)
        self.field_caption_font = make_stacked_field("", self.caption_font_size)
        self.field_footer_font = make_stacked_field("", self.footer_font_size)

        po_layout.addWidget(self.field_output_mode)
        po_layout.addLayout(tpl_row)

        self.import_template_btn = QPushButton()
        self.import_template_btn.setObjectName("GhostBtn")
        self.import_template_btn.clicked.connect(self._import_template)
        po_layout.addWidget(self.import_template_btn)

        self.preset_combo = FormComboBox()
        self.field_preset = make_stacked_field("", self.preset_combo)
        preset_row = QHBoxLayout()
        preset_row.addWidget(self.field_preset, stretch=1)
        self.apply_preset_btn = QPushButton()
        self.apply_preset_btn.setObjectName("GhostBtn")
        self.apply_preset_btn.clicked.connect(self._apply_preset)
        preset_row.addWidget(self.apply_preset_btn)
        po_layout.addLayout(preset_row)

        self.doc_title = QLineEdit()
        self.doc_author = QLineEdit()
        self.color_title = QLineEdit()
        self.color_accent = QLineEdit()
        self.color_muted = QLineEdit()
        self.color_border = QLineEdit()
        for w in (self.color_title, self.color_accent, self.color_muted, self.color_border):
            w.setMaxLength(7)
            w.setPlaceholderText("#RRGGBB")
        self.field_doc_title = make_stacked_field("", self.doc_title)
        self.field_doc_author = make_stacked_field("", self.doc_author)
        self.field_color_title = make_stacked_field("", self.color_title)
        self.field_color_accent = make_stacked_field("", self.color_accent)
        self.field_color_muted = make_stacked_field("", self.color_muted)
        self.field_color_border = make_stacked_field("", self.color_border)

        po_layout.addWidget(self.field_image_fit)
        for field in (
            self.field_slide_size,
            self.field_slide_width,
            self.field_slide_height,
            self.field_title_font,
            self.field_caption_font,
            self.field_footer_font,
            self.field_doc_title,
            self.field_doc_author,
            self.field_color_title,
            self.field_color_accent,
            self.field_color_muted,
            self.field_color_border,
        ):
            po_layout.addWidget(field)

        self.pptx_output_group = pptx_out
        root.addWidget(pptx_out)

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
        self.auto_rotate = QCheckBox()
        self.strip_gps = QCheckBox()
        self.native_sections = QCheckBox()
        self.write_report = QCheckBox()
        self.index_slide = QCheckBox()
        self.com_postprocess = QCheckBox()
        self.lo_preview = QCheckBox()
        self.enable_plugins = QCheckBox()
        for w in (
            self.section_div,
            self.zoom_click,
            self.zoom_hover,
            self.image_shadow,
            self.image_border,
            self.caption_name,
            self.auto_rotate,
            self.strip_gps,
            self.native_sections,
            self.write_report,
            self.index_slide,
            self.com_postprocess,
            self.lo_preview,
            self.enable_plugins,
        ):
            fl.addWidget(w)
        self.caption_source_combo = FormComboBox()
        self.field_caption_source = make_stacked_field("", self.caption_source_combo)
        fl.addWidget(self.field_caption_source)
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
            self.output_mode_combo,
            self.template_path,
            self.image_fit_combo,
            self.slide_size_combo,
            self.slide_width,
            self.slide_height,
            self.title_font_size,
            self.caption_font_size,
            self.footer_font_size,
            self.section_div,
            self.zoom_click,
            self.zoom_hover,
            self.image_shadow,
            self.image_border,
            self.caption_name,
            self.auto_rotate,
            self.strip_gps,
            self.native_sections,
            self.write_report,
            self.index_slide,
            self.com_postprocess,
            self.lo_preview,
            self.enable_plugins,
            self.caption_source_combo,
            self.preset_combo,
            self.doc_title,
            self.doc_author,
            self.color_title,
            self.color_accent,
            self.color_muted,
            self.color_border,
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
            self.output_mode_combo,
            self.template_path,
            self.image_fit_combo,
            self.slide_size_combo,
            self.slide_width,
            self.slide_height,
            self.title_font_size,
            self.caption_font_size,
            self.footer_font_size,
            self.section_div,
            self.zoom_click,
            self.zoom_hover,
            self.image_shadow,
            self.image_border,
            self.caption_name,
            self.auto_rotate,
            self.strip_gps,
            self.native_sections,
            self.write_report,
            self.index_slide,
            self.com_postprocess,
            self.lo_preview,
            self.enable_plugins,
            self.caption_source_combo,
            self.preset_combo,
            self.doc_title,
            self.doc_author,
            self.color_title,
            self.color_accent,
            self.color_muted,
            self.color_border,
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
        self.pptx_output_group.setTitle(t("settings.group.pptx_output"))
        self.po_hint.setText(t("settings.pptx_output.hint"))
        self.field_output_mode.field_label.setText(t("settings.label.output_mode"))  # type: ignore[attr-defined]
        self.field_template_path.field_label.setText(t("settings.label.template_path"))  # type: ignore[attr-defined]
        self.template_path.setPlaceholderText(t("settings.placeholder.template_path"))
        self.analyze_template_btn.setText(t("settings.btn.analyze_template"))
        self.import_template_btn.setText(t("settings.btn.import_template"))
        self.apply_preset_btn.setText(t("settings.btn.apply_preset"))
        self.field_preset.field_label.setText(t("settings.label.preset"))  # type: ignore[attr-defined]
        self.field_image_fit.field_label.setText(t("settings.label.image_fit"))  # type: ignore[attr-defined]
        self.field_doc_title.field_label.setText(t("settings.label.doc_title"))  # type: ignore[attr-defined]
        self.field_doc_author.field_label.setText(t("settings.label.doc_author"))  # type: ignore[attr-defined]
        self.field_color_title.field_label.setText(t("settings.label.color_title"))  # type: ignore[attr-defined]
        self.field_color_accent.field_label.setText(t("settings.label.color_accent"))  # type: ignore[attr-defined]
        self.field_color_muted.field_label.setText(t("settings.label.color_muted"))  # type: ignore[attr-defined]
        self.field_color_border.field_label.setText(t("settings.label.color_border"))  # type: ignore[attr-defined]
        self._populate_preset_combo()
        self.field_slide_size.field_label.setText(t("settings.label.slide_size"))  # type: ignore[attr-defined]
        self.field_slide_width.field_label.setText(t("settings.label.slide_width"))  # type: ignore[attr-defined]
        self.field_slide_height.field_label.setText(t("settings.label.slide_height"))  # type: ignore[attr-defined]
        self.field_title_font.field_label.setText(t("settings.label.title_font_size"))  # type: ignore[attr-defined]
        self.field_caption_font.field_label.setText(t("settings.label.caption_font_size"))  # type: ignore[attr-defined]
        self.field_footer_font.field_label.setText(t("settings.label.footer_font_size"))  # type: ignore[attr-defined]
        self._populate_output_mode_combo()
        self._populate_image_fit_combo()
        self._populate_slide_size_combo(preserve=True)
        self.features_group.setTitle(t("settings.group.features"))
        self.f_hint.setText(t("settings.features.hint"))
        self.section_div.setText(t("settings.section_div"))
        self.zoom_click.setText(t("settings.zoom_click"))
        self.zoom_hover.setText(t("settings.zoom_hover"))
        self.image_shadow.setText(t("settings.image_shadow"))
        self.image_border.setText(t("settings.image_border"))
        self.caption_name.setText(t("settings.caption_name"))
        self.auto_rotate.setText(t("settings.auto_rotate"))
        self.strip_gps.setText(t("settings.strip_gps"))
        self.native_sections.setText(t("settings.native_sections"))
        self.write_report.setText(t("settings.write_build_report"))
        self.index_slide.setText(t("settings.index_slide"))
        self.com_postprocess.setText(t("settings.com_postprocess"))
        self.lo_preview.setText(t("settings.lo_preview"))
        self.enable_plugins.setText(t("settings.enable_plugins"))
        self.field_caption_source.field_label.setText(t("settings.label.caption_source"))  # type: ignore[attr-defined]
        self._populate_caption_source_combo()
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

    def _populate_output_mode_combo(self) -> None:
        key = self.output_mode_combo.current_key() if not self._building else None
        self.output_mode_combo.blockSignals(True)
        try:
            self.output_mode_combo.set_items([
                ("auto", t("settings.output_mode.auto")),
                ("template", t("settings.output_mode.template")),
                ("code", t("settings.output_mode.code")),
            ])
            if key:
                self.output_mode_combo.set_current_key(key)
        finally:
            self.output_mode_combo.blockSignals(False)

    def _populate_image_fit_combo(self) -> None:
        key = self.image_fit_combo.current_key() if not self._building else None
        self.image_fit_combo.blockSignals(True)
        try:
            self.image_fit_combo.set_items([
                ("fit", t("settings.image_fit.fit")),
                ("fill", t("settings.image_fit.fill")),
                ("native", t("settings.image_fit.native")),
            ])
            if key:
                self.image_fit_combo.set_current_key(key)
        finally:
            self.image_fit_combo.blockSignals(False)

    def _populate_caption_source_combo(self) -> None:
        key = self.caption_source_combo.current_key() if not self._building else None
        self.caption_source_combo.blockSignals(True)
        try:
            self.caption_source_combo.set_items([
                ("filename", t("settings.caption_source.filename")),
                ("exif", t("settings.caption_source.exif")),
                ("both", t("settings.caption_source.both")),
                ("none", t("settings.caption_source.none")),
            ])
            if key:
                self.caption_source_combo.set_current_key(key)
        finally:
            self.caption_source_combo.blockSignals(False)

    def _populate_preset_combo(self) -> None:
        from app.core.pptx.presets import list_builtin_presets

        key = self.preset_combo.current_key() if not self._building else None
        self.preset_combo.blockSignals(True)
        try:
            items = [("", t("settings.preset.none"))]
            for pid in list_builtin_presets():
                items.append((pid, t(f"settings.preset.{pid}")))
            self.preset_combo.set_items(items)
            if key:
                self.preset_combo.set_current_key(key)
        finally:
            self.preset_combo.blockSignals(False)

    def _populate_slide_size_combo(self, *, preserve: bool = False) -> None:
        key = self.slide_size_combo.current_key() if preserve and not self._building else None
        self.slide_size_combo.blockSignals(True)
        try:
            self.slide_size_combo.set_items([
                ("widescreen_16_9", t("settings.slide_size.widescreen_16_9")),
                ("standard_4_3", t("settings.slide_size.standard_4_3")),
                ("a4_landscape", t("settings.slide_size.a4_landscape")),
                ("custom", t("settings.slide_size.custom")),
            ])
            if preserve and key:
                self.slide_size_combo.set_current_key(key)
        finally:
            self.slide_size_combo.blockSignals(False)

    def _apply_slide_preset(self, preset_key: str) -> None:
        dims = preset_dimensions(preset_key)
        custom = preset_key == "custom"
        self.slide_width.setEnabled(custom)
        self.slide_height.setEnabled(custom)
        if dims is not None:
            self.slide_width.setValue(dims[0])
            self.slide_height.setValue(dims[1])

    def _sync_template_path_enabled(self) -> None:
        mode = self.output_mode_combo.current_key() or "auto"
        enabled = mode in {"auto", "template"}
        self.template_path.setEnabled(enabled)
        self.field_template_path.setEnabled(enabled)

    def _on_slide_size_changed(self) -> None:
        if self._building:
            return
        preset_key = self.slide_size_combo.current_key() or "widescreen_16_9"
        self._apply_slide_preset(preset_key)

    def _on_output_mode_changed(self) -> None:
        if self._building:
            return
        self._sync_template_path_enabled()

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
            self._populate_output_mode_combo()
            self.output_mode_combo.set_current_key(s.get("output_mode", "auto"))
            self.template_path.setText(s.get("template_path", ""))
            self._populate_image_fit_combo()
            self.image_fit_combo.set_current_key(s.get("image_fit", "fit"))
            preset = s.get("slide_size_preset")
            if not preset:
                preset = detect_preset(
                    float(s.get("slide_width_inches", 13.33)),
                    float(s.get("slide_height_inches", 7.5)),
                )
            self._populate_slide_size_combo()
            self.slide_size_combo.set_current_key(preset)
            self.slide_width.setValue(float(s.get("slide_width_inches", 13.33)))
            self.slide_height.setValue(float(s.get("slide_height_inches", 7.5)))
            self.title_font_size.setValue(int(s.get("title_font_size", 22)))
            self.caption_font_size.setValue(int(s.get("caption_font_size", 11)))
            self.footer_font_size.setValue(int(s.get("footer_font_size", 12)))
            self._apply_slide_preset(preset)
            self._sync_template_path_enabled()
            self.section_div.setChecked(bool(s.get("enable_section_dividers", True)))
            self.zoom_click.setChecked(bool(s.get("enable_image_zoom", True)))
            self.zoom_hover.setChecked(bool(s.get("enable_hover_zoom", True)))
            self.image_shadow.setChecked(bool(s.get("enable_image_shadow", True)))
            self.image_border.setChecked(bool(s.get("enable_image_border", True)))
            self.caption_name.setChecked(bool(s.get("caption_from_filename", True)))
            self.auto_rotate.setChecked(bool(s.get("enable_auto_rotate", True)))
            self.strip_gps.setChecked(bool(s.get("strip_gps", True)))
            self.native_sections.setChecked(bool(s.get("enable_native_sections", True)))
            self.write_report.setChecked(bool(s.get("write_build_report", True)))
            self.index_slide.setChecked(bool(s.get("enable_index_slide", False)))
            self.com_postprocess.setChecked(bool(s.get("enable_com_postprocess", False)))
            self.lo_preview.setChecked(bool(s.get("enable_libreoffice_preview", False)))
            self.enable_plugins.setChecked(bool(s.get("enable_plugins", False)))
            self._populate_caption_source_combo()
            self.caption_source_combo.set_current_key(s.get("caption_source", "filename"))
            self._populate_preset_combo()
            self.preset_combo.set_current_key(s.get("active_preset", "") or "")
            self.doc_title.setText(s.get("doc_title", ""))
            self.doc_author.setText(s.get("doc_author", ""))
            self.color_title.setText(s.get("color_title", "000000"))
            self.color_accent.setText(s.get("color_accent", "0F3D2E"))
            self.color_muted.setText(s.get("color_muted", "505050"))
            self.color_border.setText(s.get("color_border", "B4B4B4"))
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
        output_mode = self.output_mode_combo.current_key() or "auto"
        if output_mode not in {"auto", "template", "code"}:
            output_mode = "auto"
        s.set("output_mode", output_mode)
        s.set("template_path", self.template_path.text().strip())
        image_fit = self.image_fit_combo.current_key() or "fit"
        if image_fit not in {"fit", "fill", "native"}:
            image_fit = "fit"
        s.set("image_fit", image_fit)
        preset_key = self.slide_size_combo.current_key() or "widescreen_16_9"
        s.set("slide_size_preset", preset_key)
        if preset_key != "custom":
            dims = preset_dimensions(preset_key)
            if dims:
                s.set("slide_width_inches", dims[0])
                s.set("slide_height_inches", dims[1])
            else:
                s.set("slide_width_inches", self.slide_width.value())
                s.set("slide_height_inches", self.slide_height.value())
        else:
            s.set("slide_width_inches", self.slide_width.value())
            s.set("slide_height_inches", self.slide_height.value())
        s.set("title_font_size", self.title_font_size.value())
        s.set("caption_font_size", self.caption_font_size.value())
        s.set("footer_font_size", self.footer_font_size.value())
        s.set("enable_section_dividers", self.section_div.isChecked())
        s.set("enable_image_zoom", self.zoom_click.isChecked())
        hover = self.zoom_hover.isChecked() and self.zoom_click.isChecked()
        s.set("enable_hover_zoom", hover)
        s.set("enable_image_shadow", self.image_shadow.isChecked())
        s.set("enable_image_border", self.image_border.isChecked())
        s.set("caption_from_filename", self.caption_name.isChecked())
        s.set("enable_auto_rotate", self.auto_rotate.isChecked())
        s.set("strip_gps", self.strip_gps.isChecked())
        s.set("enable_native_sections", self.native_sections.isChecked())
        s.set("write_build_report", self.write_report.isChecked())
        s.set("enable_index_slide", self.index_slide.isChecked())
        s.set("enable_com_postprocess", self.com_postprocess.isChecked())
        s.set("enable_libreoffice_preview", self.lo_preview.isChecked())
        s.set("enable_plugins", self.enable_plugins.isChecked())
        cap_src = self.caption_source_combo.current_key() or "filename"
        if cap_src not in {"filename", "exif", "both", "none"}:
            cap_src = "filename"
        s.set("caption_source", cap_src)
        s.set("active_preset", self.preset_combo.current_key() or "")
        s.set("doc_title", self.doc_title.text().strip())
        s.set("doc_author", self.doc_author.text().strip())
        from app.core.pptx.themes import DEFAULT_HEX, normalize_hex

        s.set("color_title", normalize_hex(self.color_title.text(), DEFAULT_HEX["color_title"]))
        s.set("color_accent", normalize_hex(self.color_accent.text(), DEFAULT_HEX["color_accent"]))
        s.set("color_muted", normalize_hex(self.color_muted.text(), DEFAULT_HEX["color_muted"]))
        s.set("color_border", normalize_hex(self.color_border.text(), DEFAULT_HEX["color_border"]))
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
        sender = self.sender()
        if sender is self.slide_size_combo:
            self._on_slide_size_changed()
        if sender is self.output_mode_combo:
            self._on_output_mode_changed()
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

    def _analyze_template(self) -> None:
        from app.core.pptx.template_import import layout_wizard_report
        from app.core.pptx.template_loader import bundled_template_if_available, is_template_file

        path_text = self.template_path.text().strip()
        path = Path(path_text) if path_text else bundled_template_if_available()
        if path is None or not is_template_file(path):
            chosen, _ = QFileDialog.getOpenFileName(
                self,
                t("settings.file_dialog.template"),
                "",
                t("settings.file_filter.template"),
            )
            if not chosen:
                return
            path = Path(chosen)
            self.template_path.setText(str(path))
        try:
            report = layout_wizard_report(path)
        except Exception as exc:
            QMessageBox.warning(self, t("settings.analyze.title"), str(exc))
            return
        QMessageBox.information(self, t("settings.analyze.title"), report)

    def _import_template(self) -> None:
        from app.core.pptx.template_import import import_template

        chosen, _ = QFileDialog.getOpenFileName(
            self,
            t("settings.file_dialog.template"),
            "",
            t("settings.file_filter.template"),
        )
        if not chosen:
            return
        try:
            dest = import_template(chosen)
        except Exception as exc:
            QMessageBox.warning(self, t("settings.import.title"), str(exc))
            return
        self.template_path.setText(str(dest))
        self.commit()
        QMessageBox.information(
            self,
            t("settings.import.title"),
            t("settings.import.done", path=str(dest)),
        )

    def _apply_preset(self) -> None:
        from app.core.pptx.presets import apply_preset_to_mapping

        preset_id = self.preset_combo.current_key() or ""
        if not preset_id:
            return
        s = self.parent_window.settings
        merged = apply_preset_to_mapping(s.all(), preset_id, base_dir=s._dir)
        for key, value in merged.items():
            if key in {
                "settings_version",
                "theme",
                "font_size",
                "ui_language",
                "ui_language_confirmed",
                "window_geometry",
            }:
                continue
            s.set(key, value)
        s.save()
        self.load_values()
        self.parent_window.apply_preferences()

    def _reset(self) -> None:
        self.parent_window.settings.reset()
        self.load_values()
        self.parent_window.apply_preferences()
