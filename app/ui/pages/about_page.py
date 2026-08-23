"""About and Help page."""

from __future__ import annotations

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app import APP_NAME, __version__
from app.i18n import t, ui_language
from app.resources import logo_png
from app.ui.help_panel import build_help_panel
from app.ui.layout_direction import ALIGN_START
from app.ui.scroll_area import RtlScrollArea, make_page_layout, mark_expanding
from app.ui.widgets import make_page_header, make_responsive_button_bar


class AboutPage(QWidget):
    def __init__(self, parent_window) -> None:
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.parent_window = parent_window
        self._build_ui()
        self.refresh_content()

    def _build_ui(self) -> None:
        root = make_page_layout(self)
        self.page_header = make_page_header("", "")
        root.addWidget(self.page_header)

        hero = QFrame()
        hero.setObjectName("AboutHero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(24, 20, 24, 18)
        hero_layout.setSpacing(20)

        logo = QLabel()
        logo.setObjectName("BrandLogo")
        logo.setFixedSize(88, 88)
        logo.setScaledContents(True)
        logo_file = logo_png()
        if logo_file.is_file():
            logo.setPixmap(QPixmap(str(logo_file)))
        hero_layout.addWidget(logo)

        text_col = QVBoxLayout()
        text_col.setSpacing(8)
        title = QLabel(APP_NAME)
        title.setObjectName("AboutTitle")
        title.setAlignment(ALIGN_START)
        self.tagline = QLabel()
        self.tagline.setObjectName("AboutTagline")
        self.tagline.setWordWrap(True)
        self.tagline.setAlignment(ALIGN_START)
        self.version_label = QLabel()
        self.version_label.setObjectName("AboutVersion")
        self.version_label.setAlignment(ALIGN_START)
        self.creator_label = QLabel()
        self.creator_label.setObjectName("AboutCreator")
        self.creator_label.setAlignment(ALIGN_START)

        text_col.addWidget(title)
        text_col.addWidget(self.tagline)
        text_col.addWidget(self.version_label)
        text_col.addWidget(self.creator_label)
        hero_layout.addLayout(text_col, stretch=1)
        root.addWidget(hero)

        help_card = QFrame()
        help_card.setObjectName("HelpCard")
        mark_expanding(help_card, vertical=True)
        help_layout = QVBoxLayout(help_card)
        help_layout.setContentsMargins(12, 12, 12, 12)
        help_layout.setSpacing(0)

        self.help_scroll = RtlScrollArea()
        self.help_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        help_layout.addWidget(self.help_scroll, stretch=1)
        root.addWidget(help_card, stretch=1)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setObjectName("GhostBtn")
        self.refresh_btn.clicked.connect(self.refresh_content)
        self.goto_settings_btn = QPushButton()
        self.goto_settings_btn.setObjectName("GhostBtn")
        self.goto_settings_btn.clicked.connect(lambda: self.parent_window.change_page(1))
        self.goto_home_btn = QPushButton()
        self.goto_home_btn.setObjectName("GhostBtn")
        self.goto_home_btn.clicked.connect(lambda: self.parent_window.change_page(0))
        self.action_bar = make_responsive_button_bar(
            self.refresh_btn, self.goto_settings_btn, self.goto_home_btn
        )
        root.addWidget(self.action_bar)
        self.retranslate_ui()

    def apply_direction(self, rtl: bool) -> None:
        self.help_scroll.apply_direction(rtl)

    def retranslate_ui(self) -> None:
        self.page_header.title_label.setText(t("about.title"))  # type: ignore[attr-defined]
        self.page_header.subtitle_label.setText(t("about.subtitle"))  # type: ignore[attr-defined]
        self.tagline.setText(f"{t('window.tagline')} — {t('about.tagline_extra')}")
        self.version_label.setText(t("about.version", version=__version__))
        self.creator_label.setText(t("about.creator"))
        self.refresh_btn.setText(t("about.btn.refresh"))
        self.goto_settings_btn.setText(t("about.btn.settings"))
        self.goto_home_btn.setText(t("about.btn.home"))

    def refresh_content(self) -> None:
        theme = self.parent_window.settings.get("theme", "dark_cyan")
        lang = ui_language()
        self.help_scroll.setWidget(build_help_panel(theme, __version__, lang=lang))
