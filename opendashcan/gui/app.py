"""Qt desktop application entry point."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence


def _require_qt() -> None:
    try:
        import PySide6  # noqa: F401
    except ImportError as exc:
        print(
            "OpenDashCAN GUI requires PySide6.\n"
            'Install with:  pip install -e ".[gui,hw]"\n'
            "Then run:      opendashcan-gui   or   opendashcan gui",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


def _want_splash(args: argparse.Namespace) -> bool:
    if args.offscreen or args.no_splash:
        return False
    from opendashcan.gui.splash import splash_disabled

    return not splash_disabled()


def main(argv: Sequence[str] | None = None) -> int:
    """Launch the OpenDashCAN Desktop GUI (LISTEN_ONLY / DOCUMENTATION_ONLY)."""
    parser = argparse.ArgumentParser(
        prog="opendashcan-gui",
        description=(
            "OpenDashCAN Desktop — PC-side OBD/CAN listen + decode research tool. "
            "NOT a website; NOT an ECU flash tool; LISTEN_ONLY (no CAN TX by default). "
            "Not affiliated with Honda Motor Co., Ltd."
        ),
    )
    parser.add_argument(
        "--offscreen",
        action="store_true",
        help="Use Qt offscreen platform (smoke / CI; no visible window)",
    )
    parser.add_argument(
        "--no-splash",
        action="store_true",
        help="Skip Honda-themed boot splash (also: OPENDASHCAN_NO_SPLASH=1)",
    )
    parser.add_argument(
        "--splash-ms",
        type=int,
        default=2000,
        metavar="MS",
        help="Boot splash duration in milliseconds (default 2000)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    _require_qt()

    if args.offscreen:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    from opendashcan.gui.main_window import MainWindow

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    app.setApplicationName("OpenDashCAN")
    app.setOrganizationName("OpenDashCAN")

    if args.offscreen:
        # Smoke path: construct + close, never block on splash/event loop
        os.environ.setdefault("OPENDASHCAN_NO_SPLASH", "1")
        window = MainWindow()
        window.close()
        return 0

    window = MainWindow()

    if _want_splash(args):
        from opendashcan.gui.splash import BootSplash

        splash = BootSplash(duration_ms=args.splash_ms)

        def _show_main() -> None:
            window.show()
            window.raise_()
            window.activateWindow()

        splash.finished.connect(_show_main)
        screen = app.primaryScreen()
        if screen is not None:
            geo = screen.availableGeometry()
            splash.move(
                geo.center().x() - splash.width() // 2,
                geo.center().y() - splash.height() // 2,
            )
        splash.start()
        QTimer.singleShot(
            max(args.splash_ms, 500) + 3000,
            lambda: _ensure_shown(window, splash),
        )
        return int(app.exec())

    window.show()
    return int(app.exec())


def _ensure_shown(window: object, splash: object) -> None:
    """Failsafe if splash never emits finished."""
    try:
        from PySide6.QtWidgets import QWidget

        if isinstance(splash, QWidget) and splash.isVisible():
            skip = getattr(splash, "skip", None)
            if callable(skip):
                skip()
        if isinstance(window, QWidget) and not window.isVisible():
            window.show()
    except Exception:  # noqa: BLE001
        pass


if __name__ == "__main__":
    raise SystemExit(main())
