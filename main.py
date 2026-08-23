"""Entry point."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app import APP_NAME, APP_ORG
from app.bootstrap import configure_hidpi, install_sigint_handler
from app.i18n.locale_detect import detect
from app.resources import icon_ico, logo_png
from app.services.settings import SettingsManager
from app.ui.fonts import configure_app_typography
from app.ui.language_dialog import prompt_ui_language
from app.ui.main_window import MainWindow


def _load_app_icon() -> QIcon:
    ico = icon_ico()
    if ico.is_file():
        return QIcon(str(ico))
    png = logo_png()
    if png.is_file():
        return QIcon(str(png))
    return QIcon()


def main() -> int:
    configure_hidpi()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ORG)
    app.setWindowIcon(_load_app_icon())
    configure_app_typography(app, "medium")

    # Ask language once before MainWindow builds (avoids close/commit overwriting confirmation).
    bootstrap_settings = SettingsManager()
    if bootstrap_settings.needs_language_prompt():
        chosen = prompt_ui_language(suggested=detect())
        bootstrap_settings.confirm_ui_language(chosen)

    window = MainWindow()
    window.setWindowIcon(app.windowIcon())
    install_sigint_handler(app, window)
    window.show()
    window.ensure_language_chosen()

    try:
        return app.exec()
    except KeyboardInterrupt:
        window.request_shutdown()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
