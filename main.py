"""Entry point."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app import APP_NAME, APP_ORG
from app.bootstrap import configure_hidpi, install_sigint_handler
from app.resources import icon_ico, logo_png
from app.ui.fonts import configure_app_typography
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
    app.setLayoutDirection(Qt.RightToLeft)
    configure_app_typography(app, "medium")

    window = MainWindow()
    window.setWindowIcon(app.windowIcon())
    install_sigint_handler(app, window)
    window.show()

    try:
        return app.exec()
    except KeyboardInterrupt:
        window.request_shutdown()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
