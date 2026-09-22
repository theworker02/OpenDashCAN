"""Live listen tab — LISTEN ONLY CAN sniff / offline replay into VehicleState."""

from __future__ import annotations

import contextlib
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from opendashcan.gui import services
from opendashcan.gui.styles import CONFIDENCE_COLORS
from opendashcan.hw.listen import (
    DEFAULT_BITRATE,
    DEFAULT_VEHICLE,
    SUPPORTED_BUSTYPES,
    HardwareUnavailableError,
    open_listen_bus,
    python_can_available,
    resolve_virtual_fixture,
)
from opendashcan.hw.session import ListenSession
from opendashcan.hw.tx_guard import refuse_send_message
from opendashcan.registry import get_decoder
from opendashcan.replay.reader import read_capture


class _BusWorker(QObject):
    """Background RX loop for a live ListenOnlyBus."""

    frame = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, bustype: str, channel: str, bitrate: int) -> None:
        super().__init__()
        self._bustype = bustype
        self._channel = channel
        self._bitrate = bitrate
        self._stop = False
        self._bus = None

    @Slot()
    def run(self) -> None:
        try:
            self._bus = open_listen_bus(
                bustype=self._bustype,
                channel=self._channel,
                bitrate=self._bitrate,
            )
        except HardwareUnavailableError as exc:
            self.error.emit(str(exc))
            self.finished.emit()
            return
        try:
            while not self._stop:
                fr = self._bus.recv(timeout=0.25)
                if fr is not None:
                    self.frame.emit(fr)
        except Exception as exc:  # noqa: BLE001
            if not self._stop:
                self.error.emit(str(exc))
        finally:
            if self._bus is not None:
                with contextlib.suppress(Exception):
                    self._bus.shutdown()
            self.finished.emit()

    def request_stop(self) -> None:
        self._stop = True


class LivePanel(QWidget):
    """Connect panel + ID rate table + decoded signals (listen-only)."""

    status_changed = Signal(str, str)  # text, kind: idle|live|error

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session: ListenSession | None = None
        self._thread: QThread | None = None
        self._worker: _BusWorker | None = None
        self._offline_frames: list = []
        self._offline_index = 0
        self._play_timer = QTimer(self)
        self._play_timer.timeout.connect(self._play_next_offline)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        banner = QLabel("LISTEN ONLY — NO TRANSMIT")
        banner.setObjectName("ListenBanner")
        banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        banner.setToolTip(refuse_send_message())
        root.addWidget(banner)

        hint = QLabel(
            "PC-side OBD/CAN sniff → decode documented layouts only. "
            "Not an ECU flash tool. No TX to vehicle or cluster. "
            "Hardware capture path: hardware/can_recorder_rpi/  ·  Wiring tab for harness docs."
        )
        hint.setObjectName("Subtitle")
        hint.setWordWrap(True)
        root.addWidget(hint)

        connect = QGroupBox("Connect")
        form = QFormLayout(connect)
        self.iface = QComboBox()
        for name in SUPPORTED_BUSTYPES:
            self.iface.addItem(name)
        self.iface.setCurrentText("socketcan")
        self.channel = QLineEdit("can0")
        self.bitrate = QSpinBox()
        self.bitrate.setRange(10_000, 1_000_000)
        self.bitrate.setSingleStep(10_000)
        self.bitrate.setValue(DEFAULT_BITRATE)
        self.vehicle = QComboBox()
        self.vehicle.setEditable(True)
        for vid in services.listen_vehicle_ids():
            self.vehicle.addItem(vid)
        self.vehicle.setCurrentText(DEFAULT_VEHICLE)
        form.addRow("Interface", self.iface)
        form.addRow("Channel", self.channel)
        form.addRow("Bitrate", self.bitrate)
        form.addRow("Vehicle profile", self.vehicle)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("Start Listen")
        self.start_btn.setObjectName("Primary")
        self.start_btn.clicked.connect(self._start_live)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("Danger")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_all)
        self.virtual_btn = QPushButton("Virtual / synthetic")
        self.virtual_btn.setObjectName("Teal")
        self.virtual_btn.clicked.connect(self._start_virtual)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addWidget(self.virtual_btn)
        form.addRow(btn_row)

        offline_row = QHBoxLayout()
        self.capture_path = QLineEdit()
        self.capture_path.setPlaceholderText("Offline candump / ASC file…")
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse_capture)
        play = QPushButton("Play file")
        play.clicked.connect(lambda: self._start_offline())
        offline_row.addWidget(self.capture_path, stretch=1)
        offline_row.addWidget(browse)
        offline_row.addWidget(play)
        form.addRow("Offline", offline_row)
        root.addWidget(connect)

        self.status = QLabel("Idle — LISTEN_ONLY")
        self.status.setObjectName("StatusIdle")
        root.addWidget(self.status)
        self._emit_status("Idle — LISTEN_ONLY", "idle")

        split = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        left_l = QVBoxLayout(left)
        left_l.addWidget(QLabel("Arbitration ID rates"))
        self.id_table = QTableWidget(0, 4)
        self.id_table.setHorizontalHeaderLabels(["ID", "Count", "Rate Hz", "Last data"])
        self.id_table.setAlternatingRowColors(True)
        self.id_table.horizontalHeader().setStretchLastSection(True)
        left_l.addWidget(self.id_table)
        split.addWidget(left)

        right = QWidget()
        right_l = QVBoxLayout(right)
        right_l.addWidget(QLabel("Decoded signals (documented layouts only)"))
        self.sig_table = QTableWidget(0, 4)
        self.sig_table.setHorizontalHeaderLabels(["Signal", "Value", "Confidence", "Last update"])
        self.sig_table.setAlternatingRowColors(True)
        self.sig_table.horizontalHeader().setStretchLastSection(True)
        self.sig_table.setFont(QFont("Consolas", 10))
        right_l.addWidget(self.sig_table)
        split.addWidget(right)
        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 3)
        root.addWidget(split, stretch=1)

        self._ui_timer = QTimer(self)
        self._ui_timer.setInterval(250)
        self._ui_timer.timeout.connect(self._refresh_tables)

    def _emit_status(self, text: str, kind: str = "idle") -> None:
        self.status.setText(text)
        self.status.setObjectName(
            "StatusLive" if kind == "live" else ("StatusError" if kind == "error" else "StatusIdle")
        )
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)
        self.status_changed.emit(text, kind)

    def _decoder(self):
        vid = self.vehicle.currentText().strip() or DEFAULT_VEHICLE
        return get_decoder(vid)

    def _reset_session(self) -> None:
        self._session = ListenSession(decoder=self._decoder())
        self.id_table.setRowCount(0)
        self.sig_table.setRowCount(0)

    def _set_running(self, running: bool) -> None:
        self.start_btn.setEnabled(not running)
        self.virtual_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        if running:
            self._ui_timer.start()
        else:
            self._ui_timer.stop()
            self._refresh_tables()

    def _start_live(self) -> None:
        if not python_can_available():
            QMessageBox.warning(
                self,
                "No python-can",
                "python-can is not installed.\n\n"
                'Install:  pip install -e ".[hw]"\n\n'
                "Or use Virtual / synthetic, or Play an offline capture file.",
            )
            return
        self._stop_all()
        try:
            self._reset_session()
        except KeyError as exc:
            QMessageBox.warning(self, "Decoder", str(exc))
            return
        bustype = self.iface.currentText()
        channel = self.channel.text().strip() or "can0"
        bitrate = int(self.bitrate.value())
        self._thread = QThread(self)
        self._worker = _BusWorker(bustype, channel, bitrate)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.frame.connect(self._on_frame)
        self._worker.error.connect(self._on_worker_error)
        self._worker.finished.connect(self._on_worker_finished)
        self._thread.start()
        self._set_running(True)
        self._emit_status(
            f"Listening {bustype}:{channel} @ {bitrate} — LISTEN ONLY — NO TRANSMIT",
            "live",
        )

    def _start_virtual(self) -> None:
        try:
            path = resolve_virtual_fixture()
        except FileNotFoundError as exc:
            QMessageBox.warning(self, "Virtual fixture", str(exc))
            return
        self.capture_path.setText(str(path))
        self._start_offline(synthetic=True)

    def _browse_capture(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open candump / ASC capture",
            "",
            "CAN logs (*.log *.asc *.csv *.json);;All files (*.*)",
        )
        if path:
            self.capture_path.setText(path)

    def _start_offline(self, *, synthetic: bool = False) -> None:
        path_s = self.capture_path.text().strip()
        if not path_s:
            QMessageBox.information(self, "Offline", "Choose a candump/ASC file first.")
            return
        path = Path(path_s)
        if not path.is_file():
            QMessageBox.warning(self, "Offline", f"Not found:\n{path}")
            return
        self._stop_all()
        try:
            self._reset_session()
            self._offline_frames = list(read_capture(path))
        except (KeyError, ValueError, OSError) as exc:
            QMessageBox.warning(self, "Offline", str(exc))
            return
        self._offline_index = 0
        label = "SYNTHETIC replay" if synthetic else "Offline play"
        self._emit_status(f"{label}: {path.name} — LISTEN ONLY — NO TRANSMIT", "live")
        self._set_running(True)
        # ~40 Hz UI feed (timestamps in file are relative; we pace by index)
        self._play_timer.start(25)

    def _play_next_offline(self) -> None:
        if self._session is None:
            return
        if self._offline_index >= len(self._offline_frames):
            self._play_timer.stop()
            self._set_running(False)
            self._emit_status(
                f"Offline play finished — {self._session.frame_count} frames — LISTEN ONLY",
                "idle",
            )
            return
        # Burst a few frames per tick for snappy replay
        for _ in range(4):
            if self._offline_index >= len(self._offline_frames):
                break
            self._session.ingest(self._offline_frames[self._offline_index])
            self._offline_index += 1

    @Slot(object)
    def _on_frame(self, frame: object) -> None:
        if self._session is None:
            return
        self._session.ingest(frame)  # type: ignore[arg-type]

    @Slot(str)
    def _on_worker_error(self, message: str) -> None:
        QMessageBox.warning(self, "Listen error", message)
        self._emit_status("Error — see dialog. Try Virtual / offline play.", "error")

    @Slot()
    def _on_worker_finished(self) -> None:
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait(2000)
        self._thread = None
        self._worker = None
        if self._play_timer.isActive():
            return
        self._set_running(False)
        n = self._session.frame_count if self._session else 0
        self._emit_status(f"Stopped — {n} frames — LISTEN ONLY — NO TRANSMIT", "idle")

    def _stop_all(self) -> None:
        self._play_timer.stop()
        if self._worker is not None:
            self._worker.request_stop()
        if self._thread is not None and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(2000)
        self._thread = None
        self._worker = None
        was_running = self.stop_btn.isEnabled()
        self._set_running(False)
        if was_running and self._session is not None:
            self._emit_status(
                f"Stopped — {self._session.frame_count} frames — LISTEN ONLY",
                "idle",
            )

    def _refresh_tables(self) -> None:
        if self._session is None:
            return
        rows = self._session.id_rate_rows()
        self.id_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            rate = f"{row.rate_hz:.1f}" if row.rate_hz is not None else "—"
            vals = [
                f"{row.arbitration_id:#05x}",
                str(row.count),
                rate,
                row.last_data_hex,
            ]
            for c, v in enumerate(vals):
                self.id_table.setItem(r, c, QTableWidgetItem(v))
        sigs = self._session.signal_rows()
        self.sig_table.setRowCount(len(sigs))
        for r, (name, val, conf, ts) in enumerate(sigs):
            for c, v in enumerate((name, val, conf, ts)):
                item = QTableWidgetItem(v)
                if c == 2:
                    tier = services.confidence_tier(conf)
                    item.setForeground(
                        QColor(CONFIDENCE_COLORS.get(tier, CONFIDENCE_COLORS["unknown"]))
                    )
                self.sig_table.setItem(r, c, item)
        if self.stop_btn.isEnabled():
            self._emit_status(
                f"Listening — {self._session.frame_count} frames — LISTEN ONLY",
                "live",
            )

    def shutdown(self) -> None:
        self._stop_all()
