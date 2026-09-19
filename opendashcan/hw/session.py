"""Shared listen session: ingest RX frames → decode → ID rates + VehicleState."""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field

from opendashcan.core.decoder import VehicleDecoder
from opendashcan.core.frame import CANFrame
from opendashcan.core.state import VehicleState


@dataclass
class IdRateRow:
    arbitration_id: int
    count: int
    rate_hz: float | None
    last_timestamp: float
    last_data_hex: str


@dataclass
class ListenSession:
    """Accumulate frames for live CLI/GUI views (decode-only, no TX)."""

    decoder: VehicleDecoder
    state: VehicleState = field(default_factory=VehicleState)
    frame_count: int = 0
    started_monotonic: float = field(default_factory=time.monotonic)
    _id_count: dict[int, int] = field(default_factory=lambda: defaultdict(int))
    _id_last_ts: dict[int, float] = field(default_factory=dict)
    _id_last_data: dict[int, str] = field(default_factory=dict)
    _id_periods: dict[int, list[float]] = field(default_factory=lambda: defaultdict(list))

    def ingest(self, frame: CANFrame) -> VehicleState:
        self.frame_count += 1
        aid = frame.arbitration_id
        prev = self._id_last_ts.get(aid)
        if prev is not None and frame.timestamp > prev:
            periods = self._id_periods[aid]
            periods.append(frame.timestamp - prev)
            if len(periods) > 64:
                del periods[:-64]
        self._id_count[aid] += 1
        self._id_last_ts[aid] = float(frame.timestamp)
        self._id_last_data[aid] = frame.data.hex().upper()
        self.state = self.decoder.decode_frame(frame, self.state)
        return self.state

    def id_rate_rows(self) -> list[IdRateRow]:
        rows: list[IdRateRow] = []
        for aid, count in sorted(self._id_count.items(), key=lambda kv: (-kv[1], kv[0])):
            periods = self._id_periods.get(aid) or []
            rate: float | None = None
            if periods:
                mean_p = sum(periods) / len(periods)
                if mean_p > 0:
                    rate = 1.0 / mean_p
            rows.append(
                IdRateRow(
                    arbitration_id=aid,
                    count=count,
                    rate_hz=rate,
                    last_timestamp=self._id_last_ts.get(aid, 0.0),
                    last_data_hex=self._id_last_data.get(aid, ""),
                )
            )
        return rows

    def signal_rows(self) -> list[tuple[str, str, str, str]]:
        """Return (name, value, confidence, last_update) for known signals."""
        rows: list[tuple[str, str, str, str]] = []
        for name in self.state.known_signals():
            sig = self.state.get(name)
            val = sig.value
            if hasattr(val, "value"):  # Enum
                val_s = str(getattr(val, "value", val))
            else:
                val_s = repr(val)
            conf = sig.confidence.value if hasattr(sig.confidence, "value") else str(sig.confidence)
            ts = f"{sig.timestamp:.3f}" if sig.timestamp is not None else "-"
            rows.append((name, val_s, conf, ts))
        return rows

    def elapsed_s(self) -> float:
        return time.monotonic() - self.started_monotonic
