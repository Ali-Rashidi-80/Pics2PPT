"""PyInstaller entry point for SlideReport."""

from __future__ import annotations

import multiprocessing

from main import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
