"""Entry point."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.bootstrap import configure_hidpi, install_sigint_handler
from app.ui.fonts import configure_app_typography
from app.ui.main_window import MainWindow


def main() -> int:
    configure_hidpi()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("SlideReport")
    app.setOrganizationName("SlideReport")
    app.setLayoutDirection(Qt.RightToLeft)
    configure_app_typography(app, "medium")

    window = MainWindow()
    install_sigint_handler(app, window)
    window.show()

    try:
        return app.exec()
    except KeyboardInterrupt:
        window.request_shutdown()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
