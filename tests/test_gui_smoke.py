"""GUI smoke tests — import + optional offscreen Qt (no display required)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from opendashcan.gui import services

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "captures" / "synthetic" / "idle_scenario.log"


def test_services_list_platforms() -> None:
    rows = services.list_browser_rows()
    assert any(r.kind == "platform" for r in rows)
    assert any(r.kind == "cluster" for r in rows)


def test_services_lookup_and_plan() -> None:
    sigs = services.lookup_signals("engine")
    assert isinstance(sigs, list)
    plan = services.adaptation_plan()
    assert plan["mode"] == "DOCUMENTATION_ONLY"
    assert "text" in plan
    assert plan["source_id"]
    assert plan["cluster_id"]


def test_services_cluster_gaps() -> None:
    report = services.cluster_gaps()
    assert report.get("label") or report.get("cluster_id")
    assert "DOCUMENTATION_ONLY" in str(report.get("label", "DOCUMENTATION_ONLY"))


def test_research_docs() -> None:
    docs = services.research_docs()
    assert docs
    assert any(d.exists for d in docs)


def test_about_and_listen_ids() -> None:
    text = services.about_text()
    assert "NOT a website" in text
    assert "LISTEN" in text.upper() or "listen" in text
    assert "OpenDashCAN Desktop" in text
    assert "Not affiliated" in text
    assert "Honda Motor Co" in text
    assert "trademark" in text.lower() or "copyright" in text.lower()
    ids = services.listen_vehicle_ids()
    assert "honda.civic.gen10.us" in ids


def test_evidence_url() -> None:
    assert "evidence_submission" in services.EVIDENCE_SUBMISSION_URL


def test_wiring_services_and_docs() -> None:
    items = services.wiring_checklist()
    assert len(items) >= 5
    assert any("CAN" in i.interface for i in items)
    docs = services.wiring_docs()
    assert docs
    assert all(d.exists for d in docs)
    assert (ROOT / "docs" / "wiring" / "README.md").is_file()


def test_virtual_listen_session_headless() -> None:
    summary = services.run_virtual_listen_session(max_frames=12)
    assert summary["mode"] == "LISTEN_ONLY"
    assert summary["frame_count"] >= 8
    assert summary["id_rows"]
    assert summary["signal_rows"]


def test_dbc_lookup_optional() -> None:
    hits = services.lookup_dbc_index("vehicle.speed")
    assert isinstance(hits, list)
    # Index may be present in checkout
    if (ROOT / "dbc" / "opendbc" / "index").is_dir():
        assert hits


def test_gui_modules_importable() -> None:
    from opendashcan.gui import app, styles

    assert callable(app.main)
    assert "background-color" in styles.STYLESHEET
    assert "ListenBanner" in styles.STYLESHEET
    assert "Teal" in styles.STYLESHEET


def test_splash_importable() -> None:
    pytest.importorskip("PySide6")
    from opendashcan.gui import splash

    assert splash.DISCLAIMER.startswith("Not affiliated")
    assert "Honda Motor Co" in splash.TRADEMARK_NOTICE
    assert "copyright" in splash.TRADEMARK_NOTICE.lower() or "trademark" in splash.TRADEMARK_NOTICE.lower()
    assert callable(splash.splash_disabled)
    assert callable(splash.honda_splash_logo_path)
    assert callable(splash.rounded_logo_pixmap)
    assert splash.DEFAULT_SPLASH_MS >= 1000


def test_rounded_logo_pixmap_optional() -> None:
    """Window-icon helper returns a rounded pixmap when brand PNG exists."""
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from opendashcan.gui.splash import rounded_logo_pixmap, repo_logo_path

    _ = QApplication.instance() or QApplication([])
    path = repo_logo_path()
    if path is None:
        assert rounded_logo_pixmap() is None
        return
    pm = rounded_logo_pixmap(path)
    assert pm is not None
    assert not pm.isNull()
    assert pm.width() > 0 and pm.height() > 0


def test_gui_offscreen_optional() -> None:
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ["OPENDASHCAN_NO_SPLASH"] = "1"
    from PySide6.QtWidgets import QApplication

    from opendashcan.gui.app import main

    # Reuse any existing QApplication from earlier GUI tests
    _ = QApplication.instance() or QApplication([])
    assert main(["--offscreen"]) == 0
    assert main(["--offscreen", "--no-splash"]) == 0


def test_live_tab_offline_play_smoke() -> None:
    """Live tab can load synthetic capture without hardware."""
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ["OPENDASHCAN_NO_SPLASH"] = "1"
    assert SYNTH.is_file()

    from PySide6.QtWidgets import QApplication, QLabel

    from opendashcan.gui.live_panel import LivePanel
    from opendashcan.gui.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    assert window.tabs.tabText(0) == "Live"
    panel = window.live_panel
    assert isinstance(panel, LivePanel)
    banners = [w for w in panel.findChildren(QLabel) if w.objectName() == "ListenBanner"]
    assert banners
    assert "LISTEN ONLY" in banners[0].text()

    panel.capture_path.setText(str(SYNTH))
    panel.vehicle.setCurrentText("honda.civic.gen10.us")
    panel._start_offline(synthetic=True)
    for _ in range(20):
        panel._play_next_offline()
        if panel._session and panel._session.frame_count >= 8:
            break
    assert panel._session is not None
    assert panel._session.frame_count >= 8
    panel._refresh_tables()
    assert panel.id_table.rowCount() >= 1
    assert panel.sig_table.rowCount() >= 1
    panel.shutdown()
    window.close()
    _ = app


def test_wiring_panel_smoke() -> None:
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ["OPENDASHCAN_NO_SPLASH"] = "1"

    from PySide6.QtWidgets import QApplication

    from opendashcan.gui.main_window import MainWindow
    from opendashcan.gui.wiring_panel import WiringPanel

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    labels = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    assert "Wiring" in labels
    assert isinstance(window.wiring_panel, WiringPanel)
    assert window.wiring_panel.check_table.rowCount() >= 5
    window.close()
    _ = app


def test_splash_offscreen_construct() -> None:
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from opendashcan.gui.splash import BootSplash

    app = QApplication.instance() or QApplication([])
    splash = BootSplash(duration_ms=500)
    splash._opacity.setOpacity(1.0)
    splash.show()
    splash.skip()
    _ = app
