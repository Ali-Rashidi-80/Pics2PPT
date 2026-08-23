"""Main window with sidebar navigation."""

from __future__ import annotations

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeySequence, QShortcut
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

from app.services.settings import SettingsManager
from app.ui.fonts import configure_app_typography
from app.ui.layout_direction import apply_layout_direction
from app.ui.pages.about_page import AboutPage
from app.ui.pages.home_page import HomePage
from app.ui.pages.settings_page import SettingsPage
from app.ui.theme import build_stylesheet


class MainWindow(QMainWindow):
    NAV_ITEMS = [
        ("ساخت گزارش", 0),
        ("تنظیمات", 1),
        ("درباره و آموزش", 2),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.settings = SettingsManager()
        self._geometry_restored = False
        self.setWindowTitle("SlideReport — ساخت خودکار گزارش پاورپوینت")
        self.setMinimumSize(860, 680)
        self.resize(920, 760)
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
        sidebar_wrap.setFixedWidth(240)
        sb_layout = QVBoxLayout(sidebar_wrap)
        sb_layout.setContentsMargins(16, 20, 16, 16)
        sb_layout.setSpacing(8)

        brand = QLabel("SlideReport")
        brand.setObjectName("BrandTitle")
        brand.setAlignment(Qt.AlignRight)
        sub = QLabel("گزارش‌ساز پاورپوینت")
        sub.setObjectName("BrandSub")
        sub.setAlignment(Qt.AlignRight)
        sb_layout.addWidget(brand)
        sb_layout.addWidget(sub)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setIconSize(QSize(18, 18))
        for label, _idx in self.NAV_ITEMS:
            item = QListWidgetItem(label)
            self.sidebar.addItem(item)
        self.sidebar.currentRowChanged.connect(self._on_nav)
        sb_layout.addWidget(self.sidebar, stretch=1)

        layout.addWidget(sidebar_wrap)

        self.stack = QStackedWidget()
        self.home_page = HomePage(self)
        self.settings_page = SettingsPage(self)
        self.about_page = AboutPage(self)
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.about_page)
        layout.addWidget(self.stack, stretch=1)

    def change_page(self, index: int) -> None:
        if 0 <= index < self.stack.count():
            self.sidebar.setCurrentRow(index)
            self.stack.setCurrentIndex(index)

    def _on_nav(self, index: int) -> None:
        if index < 0:
            return
        self.stack.setCurrentIndex(index)
        if index == 2:
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
