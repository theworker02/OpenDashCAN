"""Write captures to candump / CSV / JSON (offline)."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from pathlib import Path

from opendashcan.core.frame import CANFrame


def write_candump(path: Path | str, frames: Iterable[CANFrame], *, iface: str = "can0") -> None:
    path = Path(path)
    lines: list[str] = []
    for fr in frames:
        channel = fr.channel or iface
        lines.append(
            f"({fr.timestamp:.6f}) {channel} {fr.arbitration_id:03X}#{fr.data.hex().upper()}"
        )
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def write_csv(path: Path | str, frames: Iterable[CANFrame]) -> None:
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["timestamp", "arbitration_id", "data", "bus", "dlc"]
        )
        writer.writeheader()
        for fr in frames:
            writer.writerow(
                {
                    "timestamp": f"{fr.timestamp:.6f}",
                    "arbitration_id": hex(fr.arbitration_id),
                    "data": fr.data.hex().upper(),
                    "bus": str(fr.bus),
                    "dlc": fr.dlc,
                }
            )


def write_json(path: Path | str, frames: Iterable[CANFrame], *, label: str | None = None) -> None:
    path = Path(path)
    payload = {
        "label": label,
        "warning": "SYNTHETIC_OR_REPLAY_ONLY — not live vehicle truth unless labeled otherwise",
        "frames": [
            {
                "timestamp": fr.timestamp,
                "arbitration_id": hex(fr.arbitration_id),
                "data": fr.data.hex().upper(),
                "dlc": fr.dlc,
                "bus": str(fr.bus),
                "is_extended": fr.is_extended,
                "is_fd": fr.is_fd,
                "meta": dict(fr.meta),
            }
            for fr in frames
        ],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
