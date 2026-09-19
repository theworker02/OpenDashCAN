"""Wiring / harness panel — diagrams + swap checklist (DOCUMENTATION_ONLY)."""

from __future__ import annotations

import webbrowser
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from opendashcan.gui import services
from opendashcan.gui.styles import CONFIDENCE_COLORS


class WiringPanel(QWidget):
    """Evidence-safe wiring diagrams and Civic8→Civic10 switch checklist."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        hdr = QLabel("WIRING & HARNESS")
        hdr.setObjectName("SectionHeader")
        root.addWidget(hdr)

        disc = QLabel(
            f"{services.AFFILIATION_DISCLAIMER}\n"
            "Not OEM service instructions. OBD listen path is DOCUMENTED; "
            "donor-cluster pinouts remain UNKNOWN / REQUIRES_BENCH. "
            "LISTEN_ONLY PC path today — dual-bus bridge is FUTURE / NO TX default."
        )
        disc.setObjectName("Subtitle")
        disc.setWordWrap(True)
        root.addWidget(disc)

        split = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(0, 0, 0, 0)
        left_l.addWidget(self._section("Diagrams"))
        self.diagram_list = QListWidget()
        self.diagram_list.currentRowChanged.connect(self._show_diagram)
        left_l.addWidget(self.diagram_list, stretch=1)
        left_l.addWidget(self._section("Docs"))
        self.doc_list = QListWidget()
        self.doc_list.itemDoubleClicked.connect(self._open_doc_item)
        left_l.addWidget(self.doc_list, stretch=1)
        btn_row = QHBoxLayout()
        open_doc = QPushButton("Open selected doc")
        open_doc.clicked.connect(self._open_selected_doc)
        open_pi = QPushButton("Pi recorder")
        open_pi.setObjectName("Teal")
        open_pi.clicked.connect(self._open_pi_recorder)
        btn_row.addWidget(open_doc)
        btn_row.addWidget(open_pi)
        left_l.addLayout(btn_row)
        split.addWidget(left)

        right = QWidget()
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(0, 0, 0, 0)
        right_l.addWidget(self._section("Selected diagram"))
        self.diagram_title = QLabel("Select a diagram")
        self.diagram_title.setObjectName("Subtitle")
        right_l.addWidget(self.diagram_title)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(220)
        self.diagram_label = QLabel()
        self.diagram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.diagram_label.setMinimumSize(320, 180)
        self.diagram_label.setStyleSheet("background-color: #101214;")
        scroll.setWidget(self.diagram_label)
        right_l.addWidget(scroll, stretch=2)

        right_l.addWidget(self._section("What you may need to switch"))
        hint = QLabel(
            "Civic8→Civic10-style interfaces — confidence labels are authoritative."
        )
        hint.setObjectName("Subtitle")
        hint.setWordWrap(True)
        right_l.addWidget(hint)
        self.check_table = QTableWidget(0, 4)
        self.check_table.setHorizontalHeaderLabels(
            ["Interface", "Meaning", "Notes", "Confidence"]
        )
        self.check_table.setAlternatingRowColors(True)
        self.check_table.horizontalHeader().setStretchLastSection(True)
        right_l.addWidget(self.check_table, stretch=3)
        split.addWidget(right)
        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 5)
        root.addWidget(split, stretch=1)

        self._populate()

    @staticmethod
    def _section(text: str) -> QLabel:
        lab = QLabel(text.upper())
        lab.setObjectName("SectionHeader")
        return lab

    def _populate(self) -> None:
        self.diagram_list.clear()
        self._diagram_paths: list[Path] = []
        for title, path, exists in services.wiring_diagram_paths():
            mark = "✓" if exists else "✗"
            item = QListWidgetItem(f"{mark}  {title}")
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            if not exists:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.diagram_list.addItem(item)
            self._diagram_paths.append(path)

        self.doc_list.clear()
        for doc in services.wiring_docs():
            mark = "✓" if doc.exists else "✗"
            item = QListWidgetItem(f"{mark}  {doc.title}")
            item.setData(Qt.ItemDataRole.UserRole, str(doc.path))
            item.setToolTip(str(doc.path))
            if not doc.exists:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.doc_list.addItem(item)

        self.check_table.setRowCount(0)
        for row in services.wiring_checklist():
            r = self.check_table.rowCount()
            self.check_table.insertRow(r)
            vals = [row.interface, row.meaning, row.status, row.confidence]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(val)
                if c == 3:
                    tier = services.confidence_tier(val)
                    if "REQUIRES" in val.upper() or "UNKNOWN" in val.upper():
                        tier = "mid" if "REQUIRES" in val.upper() else "unknown"
                    if "DOCUMENTED" in val.upper() and "UNKNOWN" not in val.upper():
                        tier = "high"
                    hex_c = CONFIDENCE_COLORS.get(tier, CONFIDENCE_COLORS["unknown"])
                    item.setForeground(QColor(hex_c))
                self.check_table.setItem(r, c, item)
        self.check_table.resizeColumnsToContents()

        if self.diagram_list.count():
            self.diagram_list.setCurrentRow(0)

    def _show_diagram(self, row: int) -> None:
        if row < 0 or row >= len(self._diagram_paths):
            return
        path = self._diagram_paths[row]
        item = self.diagram_list.item(row)
        self.diagram_title.setText(item.text() if item else path.name)
        if not path.is_file():
            self.diagram_label.setText(
                f"Missing diagram:\n{path}\n\n"
                "Run: python tools/generate_wiring_diagrams.py"
            )
            self.diagram_label.setPixmap(QPixmap())
            return
        pm = QPixmap(str(path))
        if pm.isNull():
            self.diagram_label.setText(f"Could not load:\n{path}")
            return
        scaled = pm.scaled(
            900,
            420,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.diagram_label.setPixmap(scaled)

    def _open_doc_item(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self._open_path(Path(str(path)))

    def _open_selected_doc(self) -> None:
        item = self.doc_list.currentItem()
        if item is None:
            QMessageBox.information(self, "Wiring", "Select a document first.")
            return
        self._open_doc_item(item)

    def _open_pi_recorder(self) -> None:
        path = services.REPO_ROOT / "hardware" / "can_recorder_rpi" / "README.md"
        self._open_path(path)

    def _open_path(self, path: Path) -> None:
        if not path.is_file():
            QMessageBox.warning(self, "Missing file", f"Not found:\n{path}")
            return
        qurl = QUrl.fromLocalFile(str(path.resolve()))
        if not QDesktopServices.openUrl(qurl):
            webbrowser.open(path.resolve().as_uri())
