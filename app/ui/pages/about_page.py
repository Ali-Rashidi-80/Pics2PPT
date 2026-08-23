"""About and Help page."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from app import __version__
from app.ui.help_content import build_help_html
from app.ui.widgets import make_page_header


class AboutPage(QWidget):
    def __init__(self, parent_window) -> None:
        super().__init__()
        self.parent_window = parent_window
        self._build_ui()
        self.refresh_content()

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
        root.addWidget(make_page_header("درباره و آموزش", "راهنمای استفاده، ساختار پوشه‌ها و قابلیت‌های برنامه."))

        hero = QFrame()
        hero.setObjectName("AboutHero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(20, 18, 20, 14)
        title = QLabel("SlideReport")
        title.setObjectName("AboutTitle")
        title.setAlignment(Qt.AlignRight)
        tagline = QLabel("ساخت خودکار گزارش پاورپوینت از پوشه‌های تصویری — فارسی، RTL، شبکه ۲×۲")
        tagline.setObjectName("AboutTagline")
        tagline.setWordWrap(True)
        tagline.setAlignment(Qt.AlignRight)
        version = QLabel(f"نسخه {__version__}")
        version.setAlignment(Qt.AlignRight)
        version.setStyleSheet("color: inherit; opacity: 0.8;")
        creator = QLabel("سازنده: Ali Rashidi")
        creator.setObjectName("AboutCreator")
        creator.setAlignment(Qt.AlignLeft)
        hero_layout.addWidget(title)
        hero_layout.addWidget(tagline)
        hero_layout.addWidget(version)
        hero_layout.addWidget(creator)
        root.addWidget(hero)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setMinimumHeight(360)
        root.addWidget(self.browser)

        actions = QHBoxLayout()
        refresh = QPushButton("بروزرسانی")
        refresh.setObjectName("GhostBtn")
        refresh.clicked.connect(self.refresh_content)
        goto_settings = QPushButton("رفتن به تنظیمات")
        goto_settings.setObjectName("GhostBtn")
        goto_settings.clicked.connect(lambda: self.parent_window.change_page(1))
        actions.addWidget(refresh)
        actions.addWidget(goto_settings)
        actions.addStretch()
        root.addLayout(actions)

        scroll.setWidget(body)
        outer.addWidget(scroll)

    def refresh_content(self) -> None:
        theme = self.parent_window.settings.get("theme", "dark_cyan")
        self.browser.setHtml(build_help_html(theme, __version__))
