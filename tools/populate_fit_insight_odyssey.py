#!/usr/bin/env python3
"""Populate Fit / Insight / Odyssey protocol YAML from imported opendbc indexes.

Only writes VEHICLE_PROTOCOL_DOCUMENTED encodings from taxonomy_mapped entries.
Never marks CLUSTER_RX_CONFIRMED. fuel.level / coolant stay "not in public DBC".
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "dbc" / "opendbc" / "index"
PROTO = ROOT / "opendashcan" / "protocols" / "honda"

# Prefer these DBC indexes as the primary layout source per platform.
PLATFORM_SOURCES: dict[str, tuple[str, str]] = {
    "fit/gen3/us": ("honda_fit_ex_2018_can_generated.json", "ev_opendbc_fit3"),
    "insight/gen3/us": ("honda_insight_ex_2019_can_generated.json", "ev_opendbc_insight3"),
    "odyssey/gen5/us": ("honda_odyssey_exl_2018_generated.json", "ev_opendbc_odyssey5"),
}

ABSENT_NOTES = {
    "fuel.level": "Not in public opendbc Honda DBC signal list (no FUEL_LEVEL / FUEL_GAUGE).",
    "powertrain.coolant_temperature": (
        "Not in public opendbc Honda DBC signal list (do not confuse CRUISE 0x324)."
    ),
    "safety.srs_warning": "Not in public opendbc Honda DBC as a clear SRS lamp signal.",
    "safety.check_engine": "Not in public opendbc Honda DBC as MIL / check-engine lamp.",
    "brakes.abs_warning": "Not in public opendbc Honda DBC as ABS warning lamp.",
}

SENDER_MAP = {
    "PCM": "pcm",
    "VSA": "vsa",
    "BDY": "body",
    "EPS": "eps",
    "SCM": "scm",
    "EPB": "epb",
    "XXX": "UNKNOWN",
    "EON": "UNKNOWN",
}


def _load_index(name: str) -> dict:
    path = INDEX / name
    return json.loads(path.read_text(encoding="utf-8"))


def _messages_yaml(data: dict, ev: str) -> str:
    lines = ["messages:"]
    # Keep cluster-relevant + common powertrain messages only (not entire DBC dump)
    keep_names = {
        "ENGINE_DATA",
        "POWERTRAIN_DATA",
        "CAR_SPEED",
        "GEARBOX",
        "GEARBOX_15T",
        "GEARBOX_CVT",
        "GEARBOX_AUTO",
        "VSA_STATUS",
        "WHEEL_SPEEDS",
        "EPB_STATUS",
        "SEATBELT_STATUS",
        "DOORS_STATUS",
        "STALK_STATUS",
        "STALK_STATUS_2",
        "SCM_FEEDBACK",
        "ODOMETER",
        "CRUISE",
        "STEERING_SENSORS",
    }
    for msg in data.get("messages") or []:
        if msg.get("name") not in keep_names:
            continue
        lines.append(f'  - arbitration_id: "{msg["id_hex"]}"')
        lines.append(f'    name: {msg["name"]}')
        lines.append("    bus: vehicle_can")
        lines.append(f"    dlc: {msg['dlc']}")
        sender = SENDER_MAP.get(str(msg.get("sender") or "XXX").upper(), "UNKNOWN")
        lines.append(f"    sender: {sender}")
        lines.append("    receivers: [cluster]")
        lines.append("    period_ms: UNKNOWN")
        lines.append("    confidence: DOCUMENTED")
        lines.append(f"    evidence: [{ev}]")
        lines.append("    knowledge_level: VEHICLE_PROTOCOL_DOCUMENTED")
        lines.append("    role: vehicle_protocol")
        src = data.get("provenance", {}).get("source_dbc", "opendbc")
        sha = data.get("provenance", {}).get("commit_sha", "")
        lines.append(
            f"    notes: >\n      opendbc {src} ({sha[:12]}…). "
            "Vehicle-bus DOCUMENTED. Cluster RX NOT PHYSICALLY_VERIFIED."
        )
        if msg["name"] in ("ENGINE_DATA", "POWERTRAIN_DATA", "CAR_SPEED", "GEARBOX", "SCM_FEEDBACK"):
            lines.append("    integrity:")
            lines.append("      checksum: { type: honda_nibble_v1 }")
            lines.append("      counter: { type: honda_2bit_v1 }")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _signals_yaml(data: dict, ev: str) -> str:
    lines = ["signals:"]
    mapped = data.get("taxonomy_mapped") or []
    by_tax = {m["taxonomy"]: m for m in mapped if m.get("taxonomy")}

    for tax, m in sorted(by_tax.items()):
        kl = m.get("knowledge_level", "VEHICLE_PROTOCOL_DOCUMENTED")
        lines.append(f"  - signal: {tax}")
        lines.append("    message:")
        lines.append(f'      arbitration_id: "{m["arbitration_id"]}"')
        lines.append("      bus: vehicle_can")
        lines.append(f'      name: {m["message"]}')
        lines.append("    encoding:")
        lines.append(f'      start_bit: {m["start_bit"]}')
        lines.append(f'      length: {m["length"]}')
        lines.append(f'      byte_order: {m["byte_order"]}')
        lines.append(f'      signed: {"true" if m.get("signed") else "false"}')
        lines.append(f'      scale: {m["scale"]}')
        lines.append(f'      offset: {m["offset"]}')
        unit = m.get("unit")
        lines.append(f'      unit: {unit if unit else "null"}')
        lines.append("    confidence: DOCUMENTED")
        lines.append(f"    evidence: [{ev}]")
        lines.append(f"    knowledge_level: {kl}")
        lines.append("    role: vehicle_protocol")
        lines.append("    physical_validation: false")
        lines.append(
            "    notes: >\n      From opendbc import. "
            "VEHICLE_PROTOCOL_DOCUMENTED — cluster display path NOT PHYSICALLY_VERIFIED."
        )
        lines.append("")

    for tax, note in ABSENT_NOTES.items():
        if tax in by_tax:
            continue
        lines.append(f"  - signal: {tax}")
        lines.append("    message:")
        lines.append('      arbitration_id: UNKNOWN')
        lines.append("      bus: UNKNOWN")
        lines.append("    encoding: {}")
        lines.append("    confidence: UNKNOWN")
        lines.append("    evidence: []")
        lines.append("    knowledge_level: UNKNOWN")
        lines.append("    role: vehicle_protocol")
        lines.append("    physical_validation: false")
        lines.append(f"    notes: {note}")
        lines.append("")

    lines.append("  - signal: vehicle.ignition_state")
    lines.append("    message:")
    lines.append('      arbitration_id: UNKNOWN')
    lines.append("      bus: UNKNOWN")
    lines.append("    encoding: {}")
    lines.append("    confidence: UNKNOWN")
    lines.append("    evidence: []")
    lines.append("    knowledge_level: UNKNOWN")
    lines.append("    physical_validation: false")
    lines.append(
        "    notes: Startup / ignition sequencing for donor cluster UNKNOWN without bench."
    )
    lines.append("")
    return "\n".join(lines)


def _evidence_yaml(ev: str, data: dict, platform: str) -> str:
    prov = data.get("provenance") or {}
    return (
        "evidence:\n"
        f"  - evidence_id: {ev}\n"
        "    source_type: DBC\n"
        f"    source_url: \"{prov.get('repo', 'https://github.com/commaai/opendbc')}\"\n"
        f"    title: \"commaai/opendbc {prov.get('source_dbc', '')} (MIT)\"\n"
        f"    claim: opendbc vehicle-bus layouts for {platform}\n"
        "    confidence: DOCUMENTED\n"
        f"    license: {prov.get('license', 'MIT')}\n"
        f"    commit_sha: \"{prov.get('commit_sha', '')}\"\n"
        f"    source_dbc: {prov.get('source_dbc', '')}\n"
        "    bus: vehicle_can\n"
        "    notes: >\n"
        "      Imported as VEHICLE_PROTOCOL_DOCUMENTED only.\n"
        "      Does not confirm donor cluster RX.\n"
    )


def _ensure_insight_stub() -> Path:
    base = PROTO / "insight" / "gen3" / "us"
    base.mkdir(parents=True, exist_ok=True)
    vehicle = base / "vehicle.yaml"
    if not vehicle.exists():
        vehicle.write_text(
            """platform_id: honda.insight.gen3.us
manufacturer: honda
model: insight
generation: 3
platform: ZE
years:
  start: 2019
  end: 2022
markets: [US]
engines: []
transmissions: []
protocols: [CAN]
roles:
  - source
  - target
aliases:
  - honda_insight_3rd_gen
status:
  research: active
  physical_validation: incomplete
notes:
  - opendbc honda_insight_ex_2019_can_generated.dbc imported as VEHICLE_PROTOCOL_DOCUMENTED.
  - Cluster RX for donor swap NOT PHYSICALLY_VERIFIED.
""",
            encoding="utf-8",
        )
    buses = base / "buses.yaml"
    if not buses.exists():
        buses.write_text(
            """buses:
  - id: vehicle_can
    manufacturer_name: F-CAN
    protocol: CAN
    bitrate: 500000
    identifier_width: 11
    can_fd: false
    confidence: DOCUMENTED
    evidence: [ev_opendbc_insight3]
    notes: openpilot Honda Bosch platform; PT bus ~500 kbps typical.
""",
            encoding="utf-8",
        )
    modules = base / "modules.yaml"
    if not modules.exists():
        modules.write_text(
            """modules:
  - module_id: pcm
    display_name: Powertrain Control Module
    bus: vehicle_can
    role: powertrain
    confidence: DOCUMENTED
    evidence: [ev_opendbc_insight3]
  - module_id: cluster
    display_name: Gauge Control Module
    bus: vehicle_can
    role: cluster
    confidence: UNKNOWN
    evidence: []
    notes: Cluster RX requirements UNKNOWN without bench.
""",
            encoding="utf-8",
        )
    return base


def main() -> None:
    _ensure_insight_stub()
    for rel, (index_name, ev) in PLATFORM_SOURCES.items():
        data = _load_index(index_name)
        base = PROTO / rel
        base.mkdir(parents=True, exist_ok=True)
        (base / "messages.yaml").write_text(_messages_yaml(data, ev), encoding="utf-8")
        (base / "signals.yaml").write_text(_signals_yaml(data, ev), encoding="utf-8")
        evid_dir = base / "evidence"
        evid_dir.mkdir(exist_ok=True)
        (evid_dir / "catalog.yaml").write_text(
            _evidence_yaml(ev, data, rel), encoding="utf-8"
        )
        # Update vehicle notes
        vpath = base / "vehicle.yaml"
        if vpath.exists():
            v = yaml.safe_load(vpath.read_text(encoding="utf-8")) or {}
            notes = list(v.get("notes") or [])
            marker = "opendbc vehicle-bus layouts imported"
            if not any(marker in str(n) for n in notes):
                notes.append(
                    f"{marker} as VEHICLE_PROTOCOL_DOCUMENTED "
                    f"from {data.get('provenance', {}).get('source_dbc')}. "
                    "Cluster RX NOT PHYSICALLY_VERIFIED."
                )
            v["notes"] = notes
            status = dict(v.get("status") or {})
            status["research"] = "active"
            v["status"] = status
            if "insight" in rel:
                v.setdefault("roles", ["source", "target"])
            vpath.write_text(
                yaml.safe_dump(v, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
        print(f"populated {rel} from {index_name}")


if __name__ == "__main__":
    main()
