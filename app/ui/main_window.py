"""Main window with sidebar navigation."""

from __future__ import annotations

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app import APP_NAME, APP_TAGLINE_FA, __version__
from app.resources import logo_png
from app.services.settings import SettingsManager
from app.ui.fonts import configure_app_typography
from app.ui.layout_direction import ALIGN_START, apply_layout_direction
from app.ui.pages.about_page import AboutPage
from app.ui.pages.home_page import HomePage
from app.ui.pages.settings_page import SettingsPage
from app.ui.theme import build_stylesheet


class MainWindow(QMainWindow):
    NAV_ITEMS = [
        ("◈  ساخت گزارش", 0),
        ("◈  تنظیمات", 1),
        ("◈  درباره و آموزش", 2),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.settings = SettingsManager()
        self._geometry_restored = False
        self.setWindowTitle(f"{APP_NAME} — {APP_TAGLINE_FA}")
        self.setMinimumSize(880, 700)
        self.resize(960, 780)
        self.setLayoutDirection(Qt.RightToLeft)

        self._build_ui()
        self._setup_shortcuts()
        self.apply_preferences()
        self.sidebar.setCurrentRow(0)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+O"), self, self.home_page._browse_root)
        QShortcut(QKeySequence("F5"), self, self._shortcut_start)
        QShortcut(QKeySequence("Escape"), self, self._shortcut_cancel)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.request_shutdown)

    def _shortcut_start(self) -> None:
        if self.stack.currentIndex() == 0 and self.home_page.start_btn.isEnabled():
            self.home_page._start()

    def _shortcut_cancel(self) -> None:
        if self.stack.currentIndex() == 0 and self.home_page.cancel_btn.isEnabled():
            self.home_page._cancel()

    def request_shutdown(self) -> None:
        """Graceful shutdown: cancel worker, save settings, close window."""
        if hasattr(self, "home_page") and self.home_page.worker:
            self.home_page.worker.cancel()
        self.close()
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar_wrap = QFrame()
        sidebar_wrap.setObjectName("SidebarBrand")
        sidebar_wrap.setFixedWidth(250)
        sb_layout = QVBoxLayout(sidebar_wrap)
        sb_layout.setContentsMargins(18, 22, 18, 18)
        sb_layout.setSpacing(10)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)
        logo = QLabel()
        logo.setObjectName("BrandLogo")
        logo.setFixedSize(48, 48)
        logo.setScaledContents(True)
        logo_file = logo_png()
        if logo_file.is_file():
            logo.setPixmap(QPixmap(str(logo_file)))
        brand_col = QVBoxLayout()
        brand_col.setSpacing(2)
        brand = QLabel(APP_NAME)
        brand.setObjectName("BrandTitle")
        brand.setAlignment(ALIGN_START)
        sub = QLabel("عکس‌ها → پاورپوینت")
        sub.setObjectName("BrandSub")
        sub.setAlignment(ALIGN_START)
        brand_col.addWidget(brand)
        brand_col.addWidget(sub)
        brand_row.addWidget(logo)
        brand_row.addLayout(brand_col, stretch=1)
        sb_layout.addLayout(brand_row)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setIconSize(QSize(18, 18))
        self.sidebar.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        for label, _idx in self.NAV_ITEMS:
            item = QListWidgetItem(label)
            self.sidebar.addItem(item)
        self.sidebar.currentRowChanged.connect(self._on_nav)
        sb_layout.addWidget(self.sidebar, stretch=1)

        footer = QFrame()
        footer.setObjectName("SidebarFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(4, 10, 4, 0)
        footer_layout.setSpacing(4)
        hint = QLabel("Ctrl+O انتخاب پوشه  ·  F5 شروع  ·  Esc توقف")
        hint.setObjectName("SidebarHint")
        hint.setWordWrap(True)
        hint.setAlignment(ALIGN_START)
        ver = QLabel(f"نسخه {__version__}")
        ver.setObjectName("SidebarHint")
        ver.setAlignment(ALIGN_START)
        footer_layout.addWidget(hint)
        footer_layout.addWidget(ver)
        sb_layout.addWidget(footer)

        layout.addWidget(sidebar_wrap)

        content_wrap = QFrame()
        content_wrap.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content_wrap)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.home_page = HomePage(self)
        self.settings_page = SettingsPage(self)
        self.about_page = AboutPage(self)
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.about_page)
        content_layout.addWidget(self.stack)

        layout.addWidget(content_wrap, stretch=1)

    def change_page(self, index: int) -> None:
        if 0 <= index < self.stack.count():
            self.sidebar.setCurrentRow(index)
            self.stack.setCurrentIndex(index)

    def _on_nav(self, index: int) -> None:
        if index < 0:
            return
        self.stack.setCurrentIndex(index)
        if index == 1:
            self.settings_page.load_values()
        elif index == 2:
            self.about_page.refresh_content()

    def apply_preferences(self) -> None:
        theme = self.settings.get("theme", "dark_cyan")
        font_key = self.settings.get("font_size", "medium")
        self.setStyleSheet(build_stylesheet(theme, font_key))
        from PySide6.QtWidgets import QApplication

        configure_app_typography(QApplication.instance(), font_key)
        apply_layout_direction(self, rtl=True)
        if hasattr(self, "about_page"):
            self.about_page.refresh_content()

    def closeEvent(self, event) -> None:
        if hasattr(self, "home_page") and self.home_page.worker:
            self.home_page.worker.cancel()
        if hasattr(self, "settings_page"):
            self.settings_page.commit()
        geo = self.saveGeometry().toBase64().data().decode("ascii")
        self.settings.set("window_geometry", geo)
        self.settings.save()
        super().closeEvent(event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._geometry_restored:
            return
        geo = self.settings.get("window_geometry", "")
        if geo:
            try:
                from PySide6.QtCore import QByteArray

                self.restoreGeometry(QByteArray.fromBase64(geo.encode("ascii")))
            except Exception:
                pass
        self._geometry_restored = True
