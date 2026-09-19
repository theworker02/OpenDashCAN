"""CAN capture readers (candump / ASC / CSV / JSON). Offline only."""

from __future__ import annotations

import csv
import json
import re
from collections.abc import Iterator
from pathlib import Path

from opendashcan.core.frame import BusRole, CANFrame, FrameDirection

# (timestamp) interface ID#DATA  OR  interface ID#DATA
_CANDUMP_RE = re.compile(
    r"^\s*(?:\((?P<ts>[\d.]+)\)\s+)?(?P<iface>\S+)\s+(?P<id>[0-9A-Fa-f]+)#(?P<data>[0-9A-Fa-f]*)\s*$"
)

# candump -L / SocketCAN log: (ts) iface ID##R or ID#DATA (extended uses 8 hex digits)
_CANDUMP_L_RE = re.compile(
    r"^\s*\((?P<ts>[\d.]+)\)\s+(?P<iface>\S+)\s+"
    r"(?P<id>[0-9A-Fa-f]{3,8})#(?P<data>[0-9A-Fa-f]*)\s*$"
)

# Vector ASC: "0.000000 1 158 Rx d 8 00 00 00 00 00 00 00 00"
_ASC_RE = re.compile(
    r"^\s*(?P<ts>[\d.]+)\s+(?P<chan>\d+)\s+(?P<id>[0-9A-Fa-f]+)\s+"
    r"(?P<dir>Rx|Tx)\s+d\s+(?P<dlc>\d+)\s*(?P<data>(?:[0-9A-Fa-f]{2}\s*)*)",
    re.IGNORECASE,
)


def read_candump(path: Path | str) -> Iterator[CANFrame]:
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            raw = line.strip()
            if not raw or raw.startswith("#"):
                continue
            m = _CANDUMP_RE.match(raw) or _CANDUMP_L_RE.match(raw)
            if not m:
                raise ValueError(f"{path}:{line_no}: unrecognized candump line: {raw!r}")
            ts = float(m.group("ts") or 0.0)
            arb = int(m.group("id"), 16)
            data_hex = m.group("data") or ""
            if len(data_hex) % 2:
                raise ValueError(f"{path}:{line_no}: odd-length data hex")
            data = bytes.fromhex(data_hex)
            yield CANFrame(
                arbitration_id=arb,
                data=data,
                timestamp=ts,
                channel=m.group("iface"),
                bus=BusRole.SOURCE,
                direction=FrameDirection.RX,
                is_extended=arb > 0x7FF,
                meta={"format": "candump", "source_file": str(path)},
            )


def read_asc(path: Path | str) -> Iterator[CANFrame]:
    """Parse Vector ASC / candump-compatible ASC exports (simple classic CAN lines)."""
    path = Path(path)
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line_no, line in enumerate(fh, start=1):
            raw = line.strip()
            if not raw or raw.startswith("//") or raw.startswith(";"):
                continue
            lower = raw.lower()
            if lower.startswith("date ") or lower.startswith("base ") or lower.startswith("internal"):
                continue
            if lower.startswith("begintriggerblock") or lower.startswith("endtriggerblock"):
                continue
            m = _ASC_RE.match(raw)
            if not m:
                # Ignore unrecognized ASC metadata lines rather than failing hard
                if re.match(r"^[\d.]+", raw):
                    raise ValueError(f"{path}:{line_no}: unrecognized ASC line: {raw!r}")
                continue
            ts = float(m.group("ts"))
            arb = int(m.group("id"), 16)
            data_hex = (m.group("data") or "").replace(" ", "")
            if len(data_hex) % 2:
                raise ValueError(f"{path}:{line_no}: odd-length ASC data")
            data = bytes.fromhex(data_hex)
            dlc = int(m.group("dlc"))
            if len(data) < dlc:
                data = data + bytes(dlc - len(data))
            elif len(data) > dlc:
                data = data[:dlc]
            direction = (
                FrameDirection.TX if m.group("dir").lower() == "tx" else FrameDirection.RX
            )
            yield CANFrame(
                arbitration_id=arb,
                data=data,
                timestamp=ts,
                channel=m.group("chan"),
                bus=BusRole.SOURCE,
                direction=direction,
                is_extended=arb > 0x7FF,
                meta={"format": "asc", "source_file": str(path)},
            )


def read_csv(path: Path | str) -> Iterator[CANFrame]:
    path = Path(path)
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            arb = int(row["arbitration_id"], 0)
            data = bytes.fromhex(row["data"].replace(" ", ""))
            ts = float(row.get("timestamp") or 0.0)
            yield CANFrame(
                arbitration_id=arb,
                data=data,
                timestamp=ts,
                bus=row.get("bus") or BusRole.SOURCE,
                direction=FrameDirection.RX,
                is_extended=arb > 0x7FF,
                meta={"format": "csv", "source_file": str(path)},
            )


def read_json(path: Path | str) -> Iterator[CANFrame]:
    path = Path(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    frames = payload["frames"] if isinstance(payload, dict) else payload
    for item in frames:
        arb = (
            int(item["arbitration_id"], 0)
            if isinstance(item["arbitration_id"], str)
            else int(item["arbitration_id"])
        )
        data = bytes.fromhex(item["data"].replace(" ", ""))
        yield CANFrame(
            arbitration_id=arb,
            data=data,
            timestamp=float(item.get("timestamp") or 0.0),
            bus=item.get("bus") or BusRole.SOURCE,
            direction=FrameDirection.RX,
            is_extended=bool(item.get("is_extended", arb > 0x7FF)),
            meta={"format": "json", "source_file": str(path), **item.get("meta", {})},
        )


def read_capture(path: Path | str) -> Iterator[CANFrame]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".asc":
        yield from read_asc(path)
    elif suffix in {".log", ".candump", ".txt"}:
        yield from read_candump(path)
    elif suffix == ".csv":
        yield from read_csv(path)
    elif suffix == ".json":
        yield from read_json(path)
    else:
        try:
            yield from read_candump(path)
        except ValueError:
            try:
                yield from read_asc(path)
            except ValueError:
                yield from read_json(path)
