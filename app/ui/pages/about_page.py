"""About and Help page."""

from __future__ import annotations

from PySide6.QtCore import Qt
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

from app import APP_NAME, APP_TAGLINE_FA, __version__
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
        root.addWidget(
            make_page_header(
                "درباره و آموزش",
                "راهنمای استفاده، الگوهای ساختار پوشه و قابلیت‌های برنامه.",
            )
        )

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
        tagline = QLabel(f"{APP_TAGLINE_FA} — فارسی، RTL، شبکه ۲×۲")
        tagline.setObjectName("AboutTagline")
        tagline.setWordWrap(True)
        tagline.setAlignment(ALIGN_START)

        version = QLabel(f"نسخه {__version__}")
        version.setObjectName("AboutVersion")
        version.setAlignment(ALIGN_START)

        creator = QLabel("سازنده: Ali Rashidi")
        creator.setObjectName("AboutCreator")
        creator.setAlignment(ALIGN_START)

        text_col.addWidget(title)
        text_col.addWidget(tagline)
        text_col.addWidget(version)
        text_col.addWidget(creator)
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

        refresh = QPushButton("بروزرسانی راهنما")
        refresh.setObjectName("GhostBtn")
        refresh.clicked.connect(self.refresh_content)
        goto_settings = QPushButton("رفتن به تنظیمات")
        goto_settings.setObjectName("GhostBtn")
        goto_settings.clicked.connect(lambda: self.parent_window.change_page(1))
        goto_home = QPushButton("رفتن به ساخت گزارش")
        goto_home.setObjectName("GhostBtn")
        goto_home.clicked.connect(lambda: self.parent_window.change_page(0))
        root.addWidget(make_responsive_button_bar(refresh, goto_settings, goto_home))

    def refresh_content(self) -> None:
        theme = self.parent_window.settings.get("theme", "dark_cyan")
        self.help_scroll.setWidget(build_help_panel(theme, __version__))
