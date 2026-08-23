"""Application bootstrap: HiDPI, SIGINT/Ctrl+C, frozen runtime helpers."""

from __future__ import annotations

import signal
import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication, QMainWindow


def configure_hidpi() -> None:
    """Configure HiDPI without deprecated Qt5 attributes (Qt6 enables HiDPI by default)."""
    if hasattr(Qt, "HighDpiScaleFactorRoundingPolicy"):
        from PySide6.QtWidgets import QApplication

        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )


def install_sigint_handler(app: "QApplication", window: "QMainWindow | None" = None) -> QTimer:
    """
    Allow Ctrl+C in the terminal to quit gracefully during app.exec().

    Python cannot process signals while the Qt event loop blocks unless we
    periodically wake the interpreter.
    """

    def _handle_sigint(_signum, _frame) -> None:
        if window is not None and hasattr(window, "request_shutdown"):
            window.request_shutdown()
        else:
            app.quit()

    signal.signal(signal.SIGINT, _handle_sigint)

    # Keep reference on app to prevent GC
    timer = QTimer(app)
    timer.setInterval(400)
    timer.timeout.connect(lambda: None)
    timer.start()
    app._sigint_timer = timer  # type: ignore[attr-defined]
    return timer


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def app_root() -> "Path":
    from pathlib import Path

    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[1]
