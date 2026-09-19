"""Capture GUI screenshots and short demo GIFs for the README.

Runs offscreen-capable Qt grabs. Original OpenDashCAN branding only.

Usage:
  python tools/capture_gui_demo.py
  python tools/capture_gui_demo.py --with-splash

Env:
  QT_QPA_PLATFORM=offscreen   (defaulted here for CI/headless)
  OPENDASHCAN_NO_SPLASH=1     (overridden when --with-splash)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "assets" / "screenshots"
DEMOS = ROOT / "assets" / "demo"
SYNTH = ROOT / "captures" / "synthetic" / "idle_scenario.log"


def _ensure_dirs() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    DEMOS.mkdir(parents=True, exist_ok=True)


def _save_widget(widget, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pm = widget.grab()
    if not pm.save(str(path), "PNG"):
        raise RuntimeError(f"Failed to save {path}")
    print(f"wrote {path.relative_to(ROOT)}")


def _frames_to_gif(frames: list[Path], out: Path, duration_ms: int = 180) -> None:
    from PIL import Image

    images = [Image.open(p).convert("RGB") for p in frames]
    if not images:
        raise RuntimeError("no frames for GIF")
    # Downscale wide grabs for GitHub-friendly size
    w = min(images[0].width, 960)
    scaled = []
    for im in images:
        if im.width > w:
            h = int(im.height * (w / im.width))
            im = im.resize((w, h), Image.Resampling.LANCZOS)
        scaled.append(im)
    out.parent.mkdir(parents=True, exist_ok=True)
    scaled[0].save(
        out,
        save_all=True,
        append_images=scaled[1:],
        duration=duration_ms,
        loop=0,
        optimize=True,
    )
    print(f"wrote {out.relative_to(ROOT)} ({len(scaled)} frames)")


def capture(with_splash: bool) -> int:
    # Prefer native platform with WA_DontShowOnScreen so fonts render (offscreen
    # on Windows often draws glyph boxes). Fall back to offscreen for CI.
    if "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "windows"
    if with_splash:
        os.environ.pop("OPENDASHCAN_NO_SPLASH", None)
    else:
        os.environ["OPENDASHCAN_NO_SPLASH"] = "1"

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication

    from opendashcan.gui.main_window import MainWindow
    from opendashcan.gui.splash import BootSplash
    from opendashcan.gui import services

    _ensure_dirs()
    gen = ROOT / "tools" / "generate_wiring_diagrams.py"
    if gen.is_file():
        import runpy

        try:
            runpy.run_path(str(gen), run_name="__main__")
        except Exception as exc:  # noqa: BLE001
            print(f"wiring diagram gen note: {exc}")

    app = QApplication.instance() or QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    def _prep(w) -> None:
        w.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        w.show()
        app.processEvents()

    # Splash frame
    splash = BootSplash(duration_ms=800)
    splash._opacity.setOpacity(1.0)
    splash._emblem.glow = 1.0
    _prep(splash)
    app.processEvents()
    _save_widget(splash, SHOTS / "05_boot_splash.png")
    splash_frames = []
    for g in (0.2, 0.5, 0.8, 1.0):
        splash._emblem.glow = g
        splash._opacity.setOpacity(0.4 + 0.6 * g)
        app.processEvents()
        fp = DEMOS / f"_splash_frame_{int(g*10)}.png"
        _save_widget(splash, fp)
        splash_frames.append(fp)
    splash.skip()

    window = MainWindow()
    window.resize(1100, 700)
    _prep(window)
    app.processEvents()

    # Platforms
    window.tabs.setCurrentIndex(1)
    if window.browser.topLevelItemCount() > 0:
        plats = window.browser.topLevelItem(0)
        if plats and plats.childCount() > 0:
            window.browser.setCurrentItem(plats.child(0))
    app.processEvents()
    _save_widget(window, SHOTS / "01_main_platforms.png")

    # Live virtual listen frames
    window.tabs.setCurrentWidget(window.live_panel)
    app.processEvents()
    panel = window.live_panel
    if SYNTH.is_file():
        panel.capture_path.setText(str(SYNTH))
        panel.vehicle.setCurrentText("honda.civic.gen10.us")
        panel._start_offline(synthetic=True)
        live_frames = []
        for i in range(12):
            for _ in range(6):
                panel._play_next_offline()
            panel._refresh_tables()
            app.processEvents()
            fp = DEMOS / f"_live_frame_{i:02d}.png"
            _save_widget(window, fp)
            live_frames.append(fp)
        panel.shutdown()
        _save_widget(window, SHOTS / "02_live_listen.png")
        _frames_to_gif(live_frames, DEMOS / "live_virtual_listen.gif", duration_ms=160)
        for fp in live_frames:
            fp.unlink(missing_ok=True)
    else:
        _save_widget(window, SHOTS / "02_live_listen.png")

    # Gaps
    window.tabs.setCurrentWidget(window.gaps_page)
    window._reload_gaps()
    app.processEvents()
    _save_widget(window, SHOTS / "03_cluster_gaps.png")

    # Adaptation
    for i in range(window.tabs.count()):
        if window.tabs.tabText(i) == "Adaptation":
            window.tabs.setCurrentIndex(i)
            break
    window._reload_plan()
    app.processEvents()
    _save_widget(window, SHOTS / "04_adaptation_plan.png")

    # Wiring
    window.tabs.setCurrentWidget(window.wiring_panel)
    app.processEvents()
    _save_widget(window, SHOTS / "06_wiring.png")

    # Lookup sample
    window.lookup_input.setText("engine")
    window._run_lookup()
    app.processEvents()
    _save_widget(window, SHOTS / "07_lookup.png")

    _frames_to_gif(splash_frames, DEMOS / "boot_splash.gif", duration_ms=220)
    for fp in splash_frames:
        fp.unlink(missing_ok=True)

    summary = services.run_virtual_listen_session(max_frames=16)
    print(
        f"virtual session: frames={summary['frame_count']} "
        f"ids={len(summary['id_rows'])} sigs={len(summary['signal_rows'])}"
    )

    window.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--with-splash",
        action="store_true",
        help="Allow splash env (still uses offscreen platform)",
    )
    args = parser.parse_args(argv)
    return capture(with_splash=args.with_splash)


if __name__ == "__main__":
    raise SystemExit(main())
