"""Main window for the OpenDashCAN desktop research tool."""

from __future__ import annotations

import json
import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QFont, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from opendashcan import __version__
from opendashcan.gui import services
from opendashcan.gui.live_panel import LivePanel
from opendashcan.gui.splash import (
    DISCLAIMER,
    TRADEMARK_NOTICE,
    rounded_logo_pixmap,
)
from opendashcan.gui.styles import CONFIDENCE_COLORS, STYLESHEET
from opendashcan.gui.wiring_panel import WiringPanel


def _apply_confidence_color(item: QTableWidgetItem, label: str) -> None:
    tier = services.confidence_tier(label)
    hex_c = CONFIDENCE_COLORS.get(tier, CONFIDENCE_COLORS["unknown"])
    item.setForeground(QColor(hex_c))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"OpenDashCAN Desktop {__version__} — LISTEN_ONLY")
        self.resize(1100, 700)
        self.setMinimumSize(900, 560)
        self.setStyleSheet(STYLESHEET)

        icon_pm = rounded_logo_pixmap()
        if icon_pm is not None and not icon_pm.isNull():
            self.setWindowIcon(QIcon(icon_pm))

        self._build_menu()

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title = QLabel("OpenDashCAN Desktop")
        title.setObjectName("Title")
        subtitle = QLabel(
            "Installable PC program — OBD/CAN listen → decode → VehicleState "
            "(not a website · not an ECU flash tool)"
        )
        subtitle.setObjectName("Subtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addLayout(title_col, stretch=1)
        mode = QLabel("LISTEN_ONLY")
        mode.setObjectName("ModeTag")
        mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(mode, alignment=Qt.AlignmentFlag.AlignTop)
        evidence_btn = QPushButton("Submit evidence")
        evidence_btn.setObjectName("Teal")
        evidence_btn.setToolTip(services.EVIDENCE_SUBMISSION_URL)
        evidence_btn.clicked.connect(self._open_evidence_form)
        header.addWidget(evidence_btn, alignment=Qt.AlignmentFlag.AlignTop)
        about_btn = QPushButton("About")
        about_btn.clicked.connect(self._show_about)
        header.addWidget(about_btn, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)

        banner = QLabel(services.project_mode_banner())
        banner.setObjectName("Banner")
        banner.setWordWrap(True)
        layout.addWidget(banner)

        disc = QLabel(DISCLAIMER)
        disc.setObjectName("Subtitle")
        disc.setWordWrap(True)
        layout.addWidget(disc)

        tm = QLabel(TRADEMARK_NOTICE)
        tm.setObjectName("Subtitle")
        tm.setWordWrap(True)
        layout.addWidget(tm)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, stretch=1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        plat_hdr = QLabel("PLATFORMS / CLUSTERS")
        plat_hdr.setObjectName("SectionHeader")
        left_layout.addWidget(plat_hdr)
        self.browser = QTreeWidget()
        self.browser.setHeaderLabels(["ID", "Roles", "Years", "Status"])
        self.browser.setAlternatingRowColors(True)
        self.browser.itemSelectionChanged.connect(self._on_browser_select)
        left_layout.addWidget(self.browser)
        splitter.addWidget(left)

        self.tabs = QTabWidget()
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)
        splitter.setSizes([280, 820])

        self.live_panel = LivePanel()
        self.live_panel.status_changed.connect(self._on_live_status)
        self.tabs.addTab(self.live_panel, "Live")
        self.tabs.setTabToolTip(0, "LISTEN_ONLY sniff / virtual / offline play")
        self._build_detail_tab()
        self._build_lookup_tab()
        self._build_gaps_tab()
        self._build_plan_tab()
        self.wiring_panel = WiringPanel()
        self.tabs.addTab(self.wiring_panel, "Wiring")
        self.tabs.setTabToolTip(
            self.tabs.indexOf(self.wiring_panel),
            "OBD listen tap, harness checklist, diagrams (DOCUMENTATION_ONLY)",
        )
        self._build_research_tab()

        self._listen_status = QLabel("Idle — LISTEN_ONLY")
        self._listen_status.setObjectName("StatusIdle")
        self.statusBar().addWidget(self._listen_status, stretch=1)
        self.statusBar().showMessage(
            "LISTEN_ONLY — no CAN TX · decode documented layouts only"
        )

        deps = services.gui_missing_deps_message()
        if deps:
            self.statusBar().showMessage(deps.split("\n")[0], 8000)

        self._populate_browser()
        self._reload_gaps()
        self._reload_plan()
        self._populate_research()

    def _build_menu(self) -> None:
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("Submit evidence…", self._open_evidence_form)
        help_menu.addAction("Open evidence guide…", self._open_evidence_guide)
        help_menu.addSeparator()
        help_menu.addAction("About OpenDashCAN…", self._show_about)

    def closeEvent(self, event) -> None:  # noqa: N802
        self.live_panel.shutdown()
        super().closeEvent(event)

    def _on_live_status(self, text: str, kind: str) -> None:
        self._listen_status.setText(text)
        self._listen_status.setObjectName(
            "StatusLive" if kind == "live" else ("StatusError" if kind == "error" else "StatusIdle")
        )
        self._listen_status.style().unpolish(self._listen_status)
        self._listen_status.style().polish(self._listen_status)
        self.statusBar().showMessage(text, 0)

    def _show_about(self) -> None:
        QMessageBox.about(self, "About OpenDashCAN Desktop", services.about_text())

    def _open_evidence_form(self) -> None:
        webbrowser.open(services.EVIDENCE_SUBMISSION_URL)

    def _open_evidence_guide(self) -> None:
        path = services.REPO_ROOT / services.EVIDENCE_GUIDE_REL
        if path.is_file():
            self._open_path(path)
        else:
            webbrowser.open(services.EVIDENCE_SUBMISSION_URL)

    def _build_detail_tab(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        hdr = QLabel("PLATFORM DETAIL")
        hdr.setObjectName("SectionHeader")
        lay.addWidget(hdr)
        hint = QLabel("Select a platform or cluster in the left browser.")
        hint.setObjectName("Subtitle")
        lay.addWidget(hint)
        self.detail_view = QTextEdit()
        self.detail_view.setReadOnly(True)
        self.detail_view.setFont(QFont("Consolas", 11))
        lay.addWidget(self.detail_view)
        self.tabs.addTab(page, "Platform")
        self.tabs.setTabToolTip(1, "Registry detail for the selected platform/cluster")

    def _build_lookup_tab(self) -> None:
        page = QWidget()
        self.lookup_page = page
        lay = QVBoxLayout(page)
        hdr = QLabel("SIGNAL / MESSAGE / DBC INDEX")
        hdr.setObjectName("SectionHeader")
        lay.addWidget(hdr)
        row = QHBoxLayout()
        self.lookup_input = QLineEdit()
        self.lookup_input.setPlaceholderText(
            "Signal or message (e.g. engine_rpm, ENGINE_DATA, 0x158, vehicle.speed)"
        )
        self.lookup_input.returnPressed.connect(self._run_lookup)
        btn = QPushButton("Lookup")
        btn.setObjectName("Primary")
        btn.clicked.connect(self._run_lookup)
        row.addWidget(self.lookup_input, stretch=1)
        row.addWidget(btn)
        lay.addLayout(row)

        self.signal_table = QTableWidget(0, 5)
        self.signal_table.setHorizontalHeaderLabels(
            ["Platform", "Signal", "Arb ID", "Confidence", "Notes"]
        )
        self.signal_table.setAlternatingRowColors(True)
        self.signal_table.horizontalHeader().setStretchLastSection(True)
        sig_l = QLabel("Registry signals")
        sig_l.setObjectName("SectionHeader")
        lay.addWidget(sig_l)
        lay.addWidget(self.signal_table)

        self.message_table = QTableWidget(0, 5)
        self.message_table.setHorizontalHeaderLabels(
            ["Platform", "Message", "Arb ID", "Confidence", "Period ms"]
        )
        self.message_table.setAlternatingRowColors(True)
        self.message_table.horizontalHeader().setStretchLastSection(True)
        msg_l = QLabel("Registry messages")
        msg_l.setObjectName("SectionHeader")
        lay.addWidget(msg_l)
        lay.addWidget(self.message_table)

        self.dbc_table = QTableWidget(0, 6)
        self.dbc_table.setHorizontalHeaderLabels(
            ["Taxonomy", "Vehicle", "Message", "Arb ID", "DBC signal", "Knowledge"]
        )
        self.dbc_table.setAlternatingRowColors(True)
        self.dbc_table.horizontalHeader().setStretchLastSection(True)
        dbc_l = QLabel("opendbc index (DOCUMENTATION_ONLY — not cluster RX)")
        dbc_l.setObjectName("SectionHeader")
        lay.addWidget(dbc_l)
        lay.addWidget(self.dbc_table)
        self.tabs.addTab(page, "Lookup")
        self.tabs.setTabToolTip(2, "Registry + imported DBC taxonomy search")

    def _build_gaps_tab(self) -> None:
        page = QWidget()
        self.gaps_page = page
        lay = QVBoxLayout(page)
        hdr = QLabel("CLUSTER GAPS (PHASE 4)")
        hdr.setObjectName("SectionHeader")
        lay.addWidget(hdr)
        row = QHBoxLayout()
        self.gaps_cluster = QLineEdit(services.DEFAULT_CLUSTER)
        refresh = QPushButton("Refresh gaps")
        refresh.setObjectName("Primary")
        refresh.clicked.connect(self._reload_gaps)
        row.addWidget(QLabel("Cluster id"))
        row.addWidget(self.gaps_cluster, stretch=1)
        row.addWidget(refresh)
        lay.addLayout(row)
        hint = QLabel(
            "DOCUMENTATION_ONLY gap axes from Phase 4 APIs when present — "
            "not hardware failure counts."
        )
        hint.setObjectName("Subtitle")
        hint.setWordWrap(True)
        lay.addWidget(hint)

        split = QSplitter(Qt.Orientation.Vertical)
        self.gaps_view = QTextEdit()
        self.gaps_view.setReadOnly(True)
        self.gaps_view.setFont(QFont("Consolas", 10))
        split.addWidget(self.gaps_view)

        self.gaps_table = QTableWidget(0, 5)
        self.gaps_table.setHorizontalHeaderLabels(
            ["Signal", "Overall", "Donor enc.", "Cluster RX", "Note"]
        )
        self.gaps_table.setAlternatingRowColors(True)
        self.gaps_table.horizontalHeader().setStretchLastSection(True)
        split.addWidget(self.gaps_table)
        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 3)
        lay.addWidget(split, stretch=1)
        self.tabs.addTab(page, "Cluster gaps")
        self.tabs.setTabToolTip(3, "Phase 4 eight-axis cluster gaps")

    def _build_plan_tab(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        hdr = QLabel("ADAPTATION PLAN")
        hdr.setObjectName("SectionHeader")
        lay.addWidget(hdr)
        row = QHBoxLayout()
        self.plan_source = QLineEdit(services.DEFAULT_SOURCE)
        self.plan_cluster = QLineEdit(services.DEFAULT_CLUSTER)
        refresh = QPushButton("Build plan")
        refresh.setObjectName("Primary")
        refresh.clicked.connect(self._reload_plan)
        row.addWidget(QLabel("Source"))
        row.addWidget(self.plan_source, stretch=1)
        row.addWidget(QLabel("Cluster"))
        row.addWidget(self.plan_cluster, stretch=1)
        row.addWidget(refresh)
        lay.addLayout(row)
        self.plan_summary = QLabel()
        self.plan_summary.setWordWrap(True)
        self.plan_summary.setObjectName("Subtitle")
        lay.addWidget(self.plan_summary)
        self.plan_view = QTextEdit()
        self.plan_view.setReadOnly(True)
        self.plan_view.setFont(QFont("Consolas", 10))
        lay.addWidget(self.plan_view)
        self.tabs.addTab(page, "Adaptation")
        self.tabs.setTabToolTip(4, "Civic8→Civic10 documentation-only plan")

    def _build_research_tab(self) -> None:
        page = QWidget()
        lay = QVBoxLayout(page)
        hdr = QLabel("RESEARCH / EVIDENCE")
        hdr.setObjectName("SectionHeader")
        lay.addWidget(hdr)
        lay.addWidget(QLabel("Local reports (double-click or Open)"))
        self.research_list = QListWidget()
        self.research_list.itemDoubleClicked.connect(self._open_research_item)
        lay.addWidget(self.research_list)
        btn_row = QHBoxLayout()
        open_btn = QPushButton("Open selected report")
        open_btn.clicked.connect(self._open_selected_research)
        evidence_btn = QPushButton("Submit evidence on GitHub")
        evidence_btn.setObjectName("Teal")
        evidence_btn.clicked.connect(self._open_evidence_form)
        btn_row.addWidget(open_btn)
        btn_row.addWidget(evidence_btn)
        lay.addLayout(btn_row)
        self.tabs.addTab(page, "Research")
        self.tabs.setTabToolTip(
            self.tabs.indexOf(page),
            "Open local research markdown + evidence form",
        )

    def _populate_browser(self) -> None:
        self.browser.clear()
        platforms = QTreeWidgetItem(["Platforms", "", "", ""])
        clusters = QTreeWidgetItem(["Clusters", "", "", ""])
        self.browser.addTopLevelItem(platforms)
        self.browser.addTopLevelItem(clusters)
        for row in services.list_browser_rows():
            if row.kind == "platform":
                item = QTreeWidgetItem(
                    [row.platform_id, row.roles, row.years, row.display]
                )
                item.setData(
                    0,
                    Qt.ItemDataRole.UserRole,
                    {"kind": "platform", "id": row.platform_id},
                )
                platforms.addChild(item)
            else:
                item = QTreeWidgetItem(
                    [
                        row.cluster_id or row.platform_id,
                        "cluster",
                        row.years,
                        row.status or "",
                    ]
                )
                item.setData(
                    0,
                    Qt.ItemDataRole.UserRole,
                    {
                        "kind": "cluster",
                        "id": row.cluster_id,
                        "platform_id": row.platform_id,
                    },
                )
                if row.status:
                    item.setForeground(3, QColor(CONFIDENCE_COLORS["mid"]))
                clusters.addChild(item)
        platforms.setExpanded(True)
        clusters.setExpanded(True)
        self.browser.resizeColumnToContents(0)

    def _on_browser_select(self) -> None:
        items = self.browser.selectedItems()
        if not items:
            return
        data = items[0].data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, dict):
            return
        pid = data.get("platform_id") or data.get("id")
        if not pid:
            return
        try:
            detail = services.platform_detail(str(pid))
        except KeyError as exc:
            self.detail_view.setPlainText(f"Lookup failed: {exc}")
            self.tabs.setCurrentIndex(1)
            return
        lines = [
            f"MODE: {detail.get('mode', 'DOCUMENTATION_ONLY')}",
            "",
            f"platform_id: {detail['platform_id']}",
            f"vehicle:     {detail['manufacturer']} {detail['model']} gen{detail['generation']}",
            f"years:       {detail['years']}",
            f"roles:       {', '.join(detail['roles'])}",
            f"physical:    {detail['physical_validation']}",
            f"research:    {'active' if detail['research_active'] else 'inactive'}",
            "",
            f"counts: messages={detail['message_count']} "
            f"signals={detail['signal_count']} modules={detail['module_count']}",
            "",
            "BUSES",
        ]
        for b in detail["buses"]:
            lines.append(
                f"  {b['name']}: bitrate={b['bitrate']}  confidence={b['confidence']}"
            )
        if "cluster" in detail:
            c = detail["cluster"]
            lines += [
                "",
                "CLUSTER",
                f"  id:     {c['cluster_id']}",
                f"  display:{c['display_type']}",
                f"  status: {c['compatibility_status']}",
                f"  reqs:   {c['requirements']}",
            ]
        lines += [
            "",
            "Evidence labels on signals/messages are authoritative.",
            "Never treat DOCUMENTATION_ONLY plans as hardware validation.",
            DISCLAIMER,
            TRADEMARK_NOTICE,
        ]
        self.detail_view.setPlainText("\n".join(lines))
        self.tabs.setCurrentIndex(1)
        if data.get("kind") == "cluster" and data.get("id"):
            self.gaps_cluster.setText(str(data["id"]))
            self.plan_cluster.setText(str(data["id"]))

    def _fill_table(
        self,
        table: QTableWidget,
        rows: list[list[str]],
        *,
        confidence_col: int | None = 3,
    ) -> None:
        table.setRowCount(0)
        for row in rows:
            r = table.rowCount()
            table.insertRow(r)
            for c, val in enumerate(row):
                item = QTableWidgetItem(val)
                if confidence_col is not None and c == confidence_col:
                    _apply_confidence_color(item, val)
                    item.setToolTip(val)
                table.setItem(r, c, item)

    def _run_lookup(self) -> None:
        q = self.lookup_input.text().strip()
        sigs = services.lookup_signals(q)
        msgs = services.lookup_messages(q)
        dbc = services.lookup_dbc_index(q)
        self._fill_table(
            self.signal_table,
            [
                [s.platform_id, s.signal, s.arbitration_id, s.confidence, s.notes]
                for s in sigs
            ],
        )
        self._fill_table(
            self.message_table,
            [
                [m.platform_id, m.name, m.arbitration_id, m.confidence, m.period_ms]
                for m in msgs
            ],
        )
        self._fill_table(
            self.dbc_table,
            [
                [
                    d.taxonomy,
                    d.vehicle_id,
                    d.message,
                    d.arbitration_id,
                    d.dbc_signal,
                    d.knowledge_level,
                ]
                for d in dbc
            ],
            confidence_col=5,
        )
        self.statusBar().showMessage(
            f"Lookup '{q}': {len(sigs)} signals, {len(msgs)} messages, "
            f"{len(dbc)} DBC index hits (DOCUMENTATION_ONLY)"
        )
        self.tabs.setCurrentWidget(self.lookup_page)

    def _reload_gaps(self) -> None:
        cid = self.gaps_cluster.text().strip() or services.DEFAULT_CLUSTER
        try:
            report = services.cluster_gaps(cid)
        except Exception as exc:  # noqa: BLE001
            self.gaps_view.setPlainText(f"Gaps failed: {exc}")
            self.gaps_table.setRowCount(0)
            return
        text = report.get("text")
        if isinstance(text, str) and text.strip():
            body = text
        else:
            body = json.dumps(
                {
                    k: v
                    for k, v in report.items()
                    if k not in ("rows", "text") or not isinstance(v, list)
                },
                indent=2,
                default=str,
            )
        header = (
            f"MODE: {report.get('label', 'DOCUMENTATION_ONLY')}\n"
            f"source API: {report.get('source', 'unknown')}\n\n"
        )
        if report.get("error"):
            header += f"ERROR: {report['error']}\n\n"
        self.gaps_view.setPlainText(header + body)
        gap_rows = services.gap_table_rows(report)
        self._fill_table(self.gaps_table, gap_rows, confidence_col=1)
        self.statusBar().showMessage(
            f"Cluster gaps for {cid} ({report.get('source')}) — {len(gap_rows)} rows"
        )

    def _reload_plan(self) -> None:
        source = self.plan_source.text().strip() or services.DEFAULT_SOURCE
        cluster = self.plan_cluster.text().strip() or services.DEFAULT_CLUSTER
        try:
            plan = services.adaptation_plan(source, cluster)
        except Exception as exc:  # noqa: BLE001
            self.plan_view.setPlainText(f"Plan failed: {exc}")
            self.plan_summary.setText("")
            return
        summary = plan["readiness_summary"]
        summary_bits = ", ".join(f"{k}={v}" for k, v in sorted(summary.items()))
        self.plan_summary.setText(
            f"Mode: {plan['mode']}  |  protocol: {plan['protocol_compatibility']}  |  "
            f"physical: {plan['physical_compatibility']}  |  "
            f"electrical: {plan['electrical_compatibility']}\n"
            f"Readiness: {summary_bits or '(none)'}\n"
            f"Evidence/confidence labels are per-signal — DOCUMENTATION_ONLY."
        )
        self.plan_view.setPlainText(plan["text"])
        self.statusBar().showMessage(
            f"Adaptation plan {plan['source_id']} → {plan['cluster_id']} ({plan['mode']})"
        )

    def _populate_research(self) -> None:
        self.research_list.clear()
        for doc in services.research_docs():
            mark = "✓" if doc.exists else "✗"
            item = QListWidgetItem(f"{mark}  {doc.title}  —  {doc.path.name}")
            item.setData(Qt.ItemDataRole.UserRole, str(doc.path))
            item.setToolTip(str(doc.path))
            if not doc.exists:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.research_list.addItem(item)

    def _open_research_item(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self._open_path(Path(str(path)))

    def _open_selected_research(self) -> None:
        item = self.research_list.currentItem()
        if item is None:
            QMessageBox.information(self, "Research", "Select a report first.")
            return
        self._open_research_item(item)

    def _open_path(self, path: Path) -> None:
        if not path.is_file():
            QMessageBox.warning(self, "Missing file", f"Not found:\n{path}")
            return
        qurl = QUrl.fromLocalFile(str(path.resolve()))
        if not QDesktopServices.openUrl(qurl):
            webbrowser.open(path.resolve().as_uri())
