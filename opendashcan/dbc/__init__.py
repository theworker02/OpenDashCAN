"""DBC import with full signal provenance — never silently overwrites registry data.

Imported DBC facts are labeled VEHICLE_PROTOCOL_DOCUMENTED (or
CLUSTER_RELEVANT_SIGNAL_DOCUMENTED when taxonomy-mapped). They are NEVER
auto-promoted to CLUSTER_RX_CONFIRMED / PHYSICALLY_VERIFIED / BENCH_VERIFIED.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from opendashcan.core.donor_knowledge import (
    DonorKnowledge,
    default_knowledge_for_dbc_signal,
)
from opendashcan.registry import get_registry

BO_RE = re.compile(r"^BO_\s+(\d+)\s+(\w+)\s*:\s*(\d+)\s+(\w+)")
# SG_ NAME : start|len@endian+/- (scale,offset) [min|max] "unit" receiver
SG_RE = re.compile(
    r"^SG_\s+(\w+)\s*:\s*(\d+)\|(\d+)@([01])([+-])\s*"
    r"\(([^,]+),([^)]+)\)\s*"
    r"\[([^\|]*)\|([^\]]*)\]\s*"
    r'"([^"]*)"\s*(.*)$'
)
VAL_RE = re.compile(r"^VAL_\s+(\d+)\s+(\w+)\s+(.+);?\s*$")
CM_BO_RE = re.compile(r'^CM_\s+BO_\s+(\d+)\s+"([^"]*)"\s*;?\s*$')
CM_SG_RE = re.compile(r'^CM_\s+SG_\s+(\d+)\s+(\w+)\s+"([^"]*)"\s*;?\s*$')

# DBC signal name → taxonomy path (only clear 1:1 mappings).
DBC_SIGNAL_TO_TAXONOMY: dict[str, str] = {
    "ENGINE_RPM": "powertrain.engine_rpm",
    "XMISSION_SPEED": "vehicle.speed",
    "CAR_SPEED": "vehicle.speed",
    "ODOMETER": "vehicle.odometer",
    "GEAR_SHIFTER": "transmission.gear",
    "EPB_ACTIVE": "brakes.parking_brake",
    "ESP_DISABLED": "stability.vsa_warning",
    "LEFT_BLINKER": "lighting.left_indicator",
    "RIGHT_BLINKER": "lighting.right_indicator",
    "HIGH_BEAMS": "lighting.high_beam",
    "LOW_BEAMS": "lighting.low_beam",
    "HEADLIGHTS_ON": "lighting.headlights_on",
    "SEATBELT_DRIVER_LATCHED": "safety.seatbelt_driver",
    "SEATBELT_PASS_LATCHED": "safety.seatbelt_passenger",
    "DOOR_OPEN_FL": "body.driver_door",
    "DOOR_OPEN_FR": "body.passenger_door",
    "DOOR_OPEN_RL": "body.rear_left_door",
    "DOOR_OPEN_RR": "body.rear_right_door",
    "TRUNK_OPEN": "body.trunk",
    "PEDAL_GAS": "powertrain.throttle_position",
    "BRAKE_PRESSED": "brakes.service_brake",
    "STEER_ANGLE": "chassis.steering_angle",
    "ACC_STATUS": "adas.acc_state",
}

# Signals we explicitly searched for and did not find in Honda public DBCs.
ABSENT_FROM_PUBLIC_DBC: frozenset[str] = frozenset(
    {
        "fuel.level",
        "powertrain.coolant_temperature",
        "safety.srs_warning",
        "safety.check_engine",
        "brakes.abs_warning",
    }
)

DEFAULT_OPENDBC_SHA = "4ab347baefb7473771ada0723c969c50d0c28d01"
DEFAULT_OPENDBC_REPO = "https://github.com/commaai/opendbc"
DEFAULT_LICENSE = "MIT"


@dataclass
class DbcSignal:
    name: str
    start_bit: int
    length: int
    is_little_endian: bool
    is_signed: bool
    scale: float
    offset: float
    min_value: float | None
    max_value: float | None
    unit: str
    receivers: list[str] = field(default_factory=list)
    comment: str | None = None
    enums: dict[int, str] = field(default_factory=dict)

    @property
    def byte_order(self) -> str:
        return "intel" if self.is_little_endian else "motorola"

    def to_dict(self) -> dict[str, Any]:
        taxonomy = DBC_SIGNAL_TO_TAXONOMY.get(self.name)
        knowledge = default_knowledge_for_dbc_signal(taxonomy)
        return {
            "name": self.name,
            "taxonomy": taxonomy,
            "start_bit": self.start_bit,
            "length": self.length,
            "byte_order": self.byte_order,
            "is_little_endian": self.is_little_endian,
            "signed": self.is_signed,
            "scale": self.scale,
            "offset": self.offset,
            "min": self.min_value,
            "max": self.max_value,
            "unit": self.unit or None,
            "receivers": self.receivers,
            "comment": self.comment,
            "enums": {str(k): v for k, v in sorted(self.enums.items())} if self.enums else {},
            "knowledge_level": knowledge.value,
            "role": "vehicle_protocol",
            "confidence": "DOCUMENTED",
        }


@dataclass
class DbcMessage:
    arbitration_id: int
    name: str
    dlc: int
    sender: str = "XXX"
    signals: list[DbcSignal] = field(default_factory=list)
    comment: str | None = None

    @property
    def id_hex(self) -> str:
        if self.arbitration_id > 0x7FF:
            return f"0x{self.arbitration_id:08X}"
        return hex(self.arbitration_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_dec": self.arbitration_id,
            "id_hex": self.id_hex,
            "name": self.name,
            "dlc": self.dlc,
            "sender": self.sender,
            "comment": self.comment,
            "knowledge_level": DonorKnowledge.VEHICLE_PROTOCOL_DOCUMENTED.value,
            "role": "vehicle_protocol",
            "confidence": "DOCUMENTED",
            "signals": [s.to_dict() for s in self.signals],
        }


@dataclass
class DbcConflict:
    arbitration_id: str
    dbc_name: str
    registry_name: str | None
    platform_id: str
    detail: str


@dataclass
class DbcImportResult:
    source_file: str
    messages: list[DbcMessage] = field(default_factory=list)
    conflicts: list[DbcConflict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    vehicle_id: str | None = None
    taxonomy_mapped: list[dict[str, Any]] = field(default_factory=list)
    dbc_signals_unmapped: list[dict[str, Any]] = field(default_factory=list)
    absent_signals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file,
            "vehicle_id": self.vehicle_id,
            "provenance": self.provenance,
            "warning": (
                "Imported DBC data is VEHICLE_PROTOCOL_DOCUMENTED only. "
                "It does NOT prove donor-cluster RX. "
                "Never auto-promote to CLUSTER_RX_CONFIRMED / PHYSICALLY_VERIFIED. "
                "Verify MIT license before redistributing DBC contents."
            ),
            "message_count": len(self.messages),
            "signal_count": sum(len(m.signals) for m in self.messages),
            "messages": [m.to_dict() for m in self.messages],
            "taxonomy_mapped": self.taxonomy_mapped,
            "dbc_signals": self.dbc_signals_unmapped,
            "absent_from_public_dbc": self.absent_signals,
            "conflicts": [
                {
                    "arbitration_id": c.arbitration_id,
                    "dbc_name": c.dbc_name,
                    "registry_name": c.registry_name,
                    "platform_id": c.platform_id,
                    "detail": c.detail,
                    "status": "REQUIRES_REVIEW",
                }
                for c in self.conflicts
            ],
            "notes": self.notes,
        }


def _parse_float(s: str) -> float:
    return float(s.strip())


def parse_dbc(text: str) -> list[DbcMessage]:
    """Parse BO_/SG_/VAL_/CM_ from a DBC text body."""
    messages: list[DbcMessage] = []
    by_id: dict[int, DbcMessage] = {}
    current: DbcMessage | None = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("BS_") or line.startswith("BU_"):
            continue

        m_bo = BO_RE.match(line)
        if m_bo:
            msg = DbcMessage(
                arbitration_id=int(m_bo.group(1)),
                name=m_bo.group(2),
                dlc=int(m_bo.group(3)),
                sender=m_bo.group(4),
            )
            messages.append(msg)
            by_id[msg.arbitration_id] = msg
            current = msg
            continue

        m_sg = SG_RE.match(line)
        if m_sg and current is not None:
            receivers = [r for r in m_sg.group(11).strip().split() if r]
            try:
                amin: float | None = _parse_float(m_sg.group(8))
            except ValueError:
                amin = None
            try:
                amax: float | None = _parse_float(m_sg.group(9))
            except ValueError:
                amax = None
            current.signals.append(
                DbcSignal(
                    name=m_sg.group(1),
                    start_bit=int(m_sg.group(2)),
                    length=int(m_sg.group(3)),
                    is_little_endian=m_sg.group(4) == "1",
                    is_signed=m_sg.group(5) == "-",
                    scale=_parse_float(m_sg.group(6)),
                    offset=_parse_float(m_sg.group(7)),
                    min_value=amin,
                    max_value=amax,
                    unit=m_sg.group(10),
                    receivers=receivers,
                )
            )
            continue

        m_val = VAL_RE.match(line)
        if m_val:
            mid = int(m_val.group(1))
            sig_name = m_val.group(2)
            rest = m_val.group(3).rstrip(";").strip()
            msg = by_id.get(mid)
            if msg is None:
                continue
            sig = next((s for s in msg.signals if s.name == sig_name), None)
            if sig is None:
                continue
            # pairs: value "label"
            for pair in re.finditer(r'(\d+)\s+"([^"]*)"', rest):
                sig.enums[int(pair.group(1))] = pair.group(2)
            continue

        m_cm_bo = CM_BO_RE.match(line)
        if m_cm_bo:
            msg = by_id.get(int(m_cm_bo.group(1)))
            if msg is not None:
                msg.comment = m_cm_bo.group(2)
            continue

        m_cm_sg = CM_SG_RE.match(line)
        if m_cm_sg:
            msg = by_id.get(int(m_cm_sg.group(1)))
            if msg is None:
                continue
            sig = next((s for s in msg.signals if s.name == m_cm_sg.group(2)), None)
            if sig is not None:
                sig.comment = m_cm_sg.group(3)
            continue

    return messages


def parse_dbc_messages(text: str) -> list[DbcMessage]:
    """Backward-compatible name used by tests — returns full message objects."""
    return parse_dbc(text)


def _load_provenance(dbc_path: Path) -> dict[str, Any]:
    """Load PROVENANCE.yaml next to vendored opendbc tree if present."""
    candidates = [
        dbc_path.parent.parent / "PROVENANCE.yaml",
        dbc_path.parent / "PROVENANCE.yaml",
        Path("dbc/opendbc/PROVENANCE.yaml"),
    ]
    for c in candidates:
        if c.is_file():
            data = yaml.safe_load(c.read_text(encoding="utf-8")) or {}
            return {
                "repo": data.get("repo", DEFAULT_OPENDBC_REPO),
                "commit_sha": data.get("commit_sha", DEFAULT_OPENDBC_SHA),
                "license": data.get("license", DEFAULT_LICENSE),
                "source_dbc": dbc_path.name,
                "provenance_file": str(c).replace("\\", "/"),
            }
    return {
        "repo": DEFAULT_OPENDBC_REPO,
        "commit_sha": DEFAULT_OPENDBC_SHA,
        "license": DEFAULT_LICENSE,
        "source_dbc": dbc_path.name,
    }


def _build_taxonomy_index(messages: list[DbcMessage]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mapped: list[dict[str, Any]] = []
    unmapped: list[dict[str, Any]] = []
    seen_tax: set[str] = set()
    for msg in messages:
        for sig in msg.signals:
            tax = DBC_SIGNAL_TO_TAXONOMY.get(sig.name)
            entry = {
                "dbc_signal": sig.name,
                "taxonomy": tax,
                "message": msg.name,
                "arbitration_id": msg.id_hex,
                "start_bit": sig.start_bit,
                "length": sig.length,
                "byte_order": sig.byte_order,
                "signed": sig.is_signed,
                "scale": sig.scale,
                "offset": sig.offset,
                "unit": sig.unit or None,
                "knowledge_level": default_knowledge_for_dbc_signal(tax).value,
                "role": "vehicle_protocol",
            }
            if tax:
                # Prefer ENGINE_DATA RPM over POWERTRAIN_DATA duplicate for index
                if tax in seen_tax and sig.name == "ENGINE_RPM" and msg.name != "ENGINE_DATA":
                    unmapped.append({**entry, "taxonomy": None, "note": "duplicate_rpm_on_powertrain"})
                    continue
                if tax not in seen_tax or (sig.name == "ENGINE_RPM" and msg.name == "ENGINE_DATA"):
                    if tax in seen_tax:
                        mapped = [m for m in mapped if m["taxonomy"] != tax]
                    mapped.append(entry)
                    seen_tax.add(tax)
                else:
                    unmapped.append({**entry, "note": "alternate_message_same_taxonomy"})
            else:
                unmapped.append(entry)
    return mapped, unmapped


def _absent_signals(messages: list[DbcMessage]) -> list[str]:
    names = {s.name.upper() for m in messages for s in m.signals}
    absent: list[str] = []
    for tax in sorted(ABSENT_FROM_PUBLIC_DBC):
        # Heuristic name search — fuel/coolant/srs/mil/abs warning
        needles = {
            "fuel.level": ("FUEL_LEVEL", "FUEL_GAUGE", "FUEL_REMAINING"),
            "powertrain.coolant_temperature": ("COOLANT", "ECT", "ENGINE_TEMP"),
            "safety.srs_warning": ("SRS", "AIRBAG"),
            "safety.check_engine": ("MIL", "CHECK_ENGINE", "CEL"),
            "brakes.abs_warning": ("ABS_WARNING", "ABS_FAULT", "ABS_LAMP"),
        }[tax]
        if not any(n in names for n in needles):
            absent.append(tax)
    return absent


def import_dbc(
    path: Path,
    *,
    compare_platform: str | None = None,
    vehicle: str | None = None,
    source: str = "opendbc",
    bus: str = "vehicle_can",
) -> DbcImportResult:
    text = path.read_text(encoding="utf-8", errors="replace")
    messages = parse_dbc(text)
    provenance = _load_provenance(path)
    provenance["source"] = source
    provenance["bus"] = bus
    if vehicle:
        provenance["vehicle_id"] = vehicle

    mapped, unmapped = _build_taxonomy_index(messages)
    result = DbcImportResult(
        source_file=str(path).replace("\\", "/"),
        messages=messages,
        provenance=provenance,
        vehicle_id=vehicle,
        taxonomy_mapped=mapped,
        dbc_signals_unmapped=unmapped,
        absent_signals=_absent_signals(messages),
    )
    result.notes.append(
        "All imported layouts are vehicle-bus DOCUMENTED. "
        "Cluster RX / timing / startup remain UNKNOWN unless separate evidence exists."
    )
    if result.absent_signals:
        result.notes.append(
            "Not in this public DBC (do not label vaguely UNKNOWN): "
            + ", ".join(result.absent_signals)
        )

    if compare_platform is None:
        return result

    pkg = get_registry().get(compare_platform)
    by_id: dict[str, list[str]] = {}
    for msg in pkg.messages:
        if msg.arbitration_id:
            key = msg.arbitration_id.lower()
            by_id.setdefault(key, []).append(msg.name or "UNNAMED")

    for m in messages:
        key = m.id_hex.lower()
        if key in by_id:
            reg_names = by_id[key]
            if m.name not in reg_names:
                result.conflicts.append(
                    DbcConflict(
                        arbitration_id=m.id_hex,
                        dbc_name=m.name,
                        registry_name=",".join(reg_names),
                        platform_id=pkg.platform_id,
                        detail="DBC message name differs from registry for same CAN ID",
                    )
                )
    missing = [m for m in messages if m.id_hex.lower() not in by_id]
    if missing:
        result.notes.append(
            f"{len(missing)} DBC message ID(s) not in registry for {pkg.platform_id} "
            "(not auto-merged)."
        )
    return result


def write_conflict_report(result: DbcImportResult, path: Path) -> None:
    lines = [
        "# DBC_CONFLICT_REPORT",
        "",
        f"Source: `{result.source_file}`",
        "",
        "STATUS: REQUIRES REVIEW",
        "",
        "Imported DBC data does **not** overwrite the canonical OpenDashCAN registry.",
        "",
    ]
    if not result.conflicts:
        lines += ["No name conflicts detected against the compared platform.", ""]
    else:
        lines += [
            "| CAN ID | DBC name | Registry name | Platform | Detail |",
            "|--------|----------|---------------|----------|--------|",
        ]
        for c in result.conflicts:
            lines.append(
                f"| `{c.arbitration_id}` | {c.dbc_name} | {c.registry_name} | "
                f"`{c.platform_id}` | {c.detail} |"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_import_artifacts(result: DbcImportResult, output_dir: Path) -> dict[str, Path]:
    """Write JSON index + compact YAML summary under output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(result.source_file).stem
    json_path = output_dir / f"{stem}.json"
    yaml_path = output_dir / f"{stem}.yaml"
    json_path.write_text(json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8")

    summary = {
        "source_file": result.source_file,
        "vehicle_id": result.vehicle_id,
        "provenance": result.provenance,
        "message_count": len(result.messages),
        "signal_count": sum(len(m.signals) for m in result.messages),
        "knowledge_level_default": DonorKnowledge.VEHICLE_PROTOCOL_DOCUMENTED.value,
        "taxonomy_mapped": result.taxonomy_mapped,
        "absent_from_public_dbc": result.absent_signals,
        "notes": result.notes,
        "warning": (
            "Vehicle-bus documentation only — not CLUSTER_RX_CONFIRMED."
        ),
    }
    yaml_path.write_text(
        yaml.safe_dump(summary, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return {"json": json_path, "yaml": yaml_path}


def export_platform_catalog(platform_id: str) -> dict[str, Any]:
    """Export registry message catalog as JSON (not a full DBC — avoids inventing layouts)."""
    pkg = get_registry().get(platform_id)
    return {
        "platform_id": pkg.platform_id,
        "format": "opendashcan_message_catalog_v1",
        "warning": "Not a full DBC. Encodings remain UNKNOWN unless documented.",
        "messages": [
            {
                "arbitration_id": m.arbitration_id,
                "name": m.name,
                "dlc": m.dlc,
                "bus": m.bus,
                "confidence": m.confidence.value,
                "period_ms": m.period_ms,
            }
            for m in pkg.messages
        ],
        "signals": [
            {
                "signal": s.signal,
                "arbitration_id": s.arbitration_id,
                "confidence": s.confidence.value,
                "physical_validation": s.physical_validation,
                "knowledge_level": getattr(s, "knowledge_level", None),
            }
            for s in pkg.signals
        ],
    }


def taxonomy_implementations_from_imports(
    index_dir: Path,
) -> dict[str, list[dict[str, Any]]]:
    """Scan imported JSON indexes for taxonomy signal implementations."""
    out: dict[str, list[dict[str, Any]]] = {}
    if not index_dir.is_dir():
        return out
    for path in sorted(index_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        vehicle = data.get("vehicle_id") or path.stem
        for item in data.get("taxonomy_mapped") or []:
            tax = item.get("taxonomy")
            if not tax:
                continue
            out.setdefault(tax, []).append(
                {
                    "vehicle_id": vehicle,
                    "source_dbc": data.get("provenance", {}).get("source_dbc"),
                    "commit_sha": data.get("provenance", {}).get("commit_sha"),
                    **{k: v for k, v in item.items() if k != "taxonomy"},
                }
            )
    return out
