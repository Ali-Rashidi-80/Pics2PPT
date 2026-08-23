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

from app import APP_NAME, __version__
from app.i18n import is_rtl, set_ui_language, t
from app.i18n.locale_detect import detect, normalize as normalize_lang
from app.resources import logo_png
from app.services.settings import SettingsManager
from app.ui.fonts import configure_app_typography
from app.ui.language_dialog import prompt_ui_language
from app.ui.layout_direction import ALIGN_START, apply_layout_direction
from app.ui.pages.about_page import AboutPage
from app.ui.pages.home_page import HomePage
from app.ui.pages.settings_page import SettingsPage
from app.ui.theme import build_stylesheet


class MainWindow(QMainWindow):
    NAV_KEYS = ("nav.home", "nav.settings", "nav.about")

    def __init__(self) -> None:
        super().__init__()
        self.settings = SettingsManager()
        self._geometry_restored = False
        self._language_prompt_scheduled = False
        self.setMinimumSize(880, 700)
        self.resize(960, 780)

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
        self.brand_sub = QLabel()
        self.brand_sub.setObjectName("BrandSub")
        self.brand_sub.setAlignment(ALIGN_START)
        brand_col.addWidget(brand)
        brand_col.addWidget(self.brand_sub)
        brand_row.addWidget(logo)
        brand_row.addLayout(brand_col, stretch=1)
        sb_layout.addLayout(brand_row)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setIconSize(QSize(18, 18))
        self.sidebar.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        for _idx in range(len(self.NAV_KEYS)):
            self.sidebar.addItem(QListWidgetItem(""))
        self.sidebar.currentRowChanged.connect(self._on_nav)
        sb_layout.addWidget(self.sidebar, stretch=1)

        footer = QFrame()
        footer.setObjectName("SidebarFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(4, 10, 4, 0)
        footer_layout.setSpacing(4)
        self.sidebar_hint = QLabel()
        self.sidebar_hint.setObjectName("SidebarHint")
        self.sidebar_hint.setWordWrap(True)
        self.sidebar_hint.setAlignment(ALIGN_START)
        self.sidebar_version = QLabel()
        self.sidebar_version.setObjectName("SidebarHint")
        self.sidebar_version.setAlignment(ALIGN_START)
        footer_layout.addWidget(self.sidebar_hint)
        footer_layout.addWidget(self.sidebar_version)
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

    def retranslate_ui(self) -> None:
        ui_lang = normalize_lang(self.settings.get("ui_language", "fa"))
        self.setWindowTitle(f"{APP_NAME} — {t('window.tagline', lang=ui_lang)}")
        self.brand_sub.setText(t("brand.subtitle", lang=ui_lang))
        self.sidebar_hint.setText(t("sidebar.hint", lang=ui_lang))
        self.sidebar_version.setText(t("sidebar.version", lang=ui_lang, version=__version__))
        current = self.sidebar.currentRow()
        for idx, key in enumerate(self.NAV_KEYS):
            item = self.sidebar.item(idx)
            if item is not None:
                item.setText(t(key, lang=ui_lang))
        if current >= 0:
            self.sidebar.setCurrentRow(current)
        self.home_page.retranslate_ui()
        self.settings_page.retranslate_ui()
        self.about_page.retranslate_ui()

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
        ui_lang = normalize_lang(self.settings.get("ui_language", "fa"))
        set_ui_language(ui_lang)
        theme = self.settings.get("theme", "dark_cyan")
        font_key = self.settings.get("font_size", "medium")
        self.setStyleSheet(build_stylesheet(theme, font_key))
        app = QApplication.instance()
        configure_app_typography(app, font_key)
        if app is not None:
            app.setLayoutDirection(
                Qt.LayoutDirection.RightToLeft if is_rtl() else Qt.LayoutDirection.LeftToRight
            )
        rtl = is_rtl()
        apply_layout_direction(self, rtl=rtl)
        self.home_page.apply_direction(rtl)
        self.settings_page.apply_direction(rtl)
        self.about_page.apply_direction(rtl)
        self.retranslate_ui()
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
        if not self._geometry_restored:
            geo = self.settings.get("window_geometry", "")
            if geo:
                try:
                    from PySide6.QtCore import QByteArray

                    self.restoreGeometry(QByteArray.fromBase64(geo.encode("ascii")))
                except Exception:
                    pass
            self._geometry_restored = True

    def ensure_language_chosen(self) -> None:
        """Call after show() so the first-run picker is not missed."""
        if self._language_prompt_scheduled:
            return
        if not self.settings.needs_language_prompt():
            return
        self._language_prompt_scheduled = True
        self._prompt_first_run_language()

    def _prompt_first_run_language(self) -> None:
        if not self.settings.needs_language_prompt():
            return
        suggested = detect()
        chosen = prompt_ui_language(self, suggested=suggested)
        self.settings.confirm_ui_language(chosen)
        self.settings_page.load_values()
        self.apply_preferences()
