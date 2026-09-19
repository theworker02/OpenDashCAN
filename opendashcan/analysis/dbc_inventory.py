"""Programmatic DBC inventory from vendored Honda/Acura DBCs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from opendashcan.cluster.classify import classify_from_dbc_message
from opendashcan.dbc import import_dbc

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATED_DBC = REPO_ROOT / "dbc" / "opendbc" / "generated"
OUT_DIR = REPO_ROOT / "research" / "generated"


def _import_map_safe() -> list[dict[str, str]]:
    try:
        import sys

        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from import_opendbc_honda import IMPORT_MAP  # type: ignore  # noqa: PLC0415

        return list(IMPORT_MAP)
    except Exception:
        pass
    try:
        import runpy

        ns = runpy.run_path(str(REPO_ROOT / "tools" / "import_opendbc_honda.py"))
        return list(ns["IMPORT_MAP"])
    except Exception:
        rows: list[dict[str, str]] = []
        for p in sorted(GENERATED_DBC.glob("*_generated.dbc")):
            rows.append({"file": p.name, "vehicle": p.stem, "bus": "vehicle_can"})
        return rows


def build_dbc_inventory(*, out_dir: Path | None = None) -> dict[str, Any]:
    """Decompose all mapped DBCs → inventory JSON + CSV tables."""
    dest = out_dir or OUT_DIR
    dest.mkdir(parents=True, exist_ok=True)

    inventory: dict[str, Any] = {
        "warning": (
            "Auto-generated from public opendbc Honda/Acura DBCs. "
            "VEHICLE_PROTOCOL_DOCUMENTED only — not CLUSTER_RX_CONFIRMED."
        ),
        "dbc_count": 0,
        "message_count": 0,
        "signal_count": 0,
        "vehicles": [],
    }
    msg_rows: list[dict[str, Any]] = []
    sig_rows: list[dict[str, Any]] = []

    for entry in _import_map_safe():
        path = GENERATED_DBC / entry["file"]
        if not path.is_file():
            continue
        result = import_dbc(
            path,
            vehicle=entry.get("vehicle"),
            source="opendbc",
            bus=entry.get("bus", "vehicle_can"),
        )
        platform_hint = entry.get("platform") or entry.get("vehicle")
        vehicle_summary = {
            "file": entry["file"],
            "vehicle_id": result.vehicle_id,
            "bus": entry.get("bus", "vehicle_can"),
            "messages": len(result.messages),
            "signals": sum(len(m.signals) for m in result.messages),
            "taxonomy_mapped": len(result.taxonomy_mapped),
            "absent_from_public_dbc": result.absent_signals,
            "cluster_candidate_counts": {},
        }
        class_counts: dict[str, int] = {}
        for msg in result.messages:
            mdict = msg.to_dict()
            cand = classify_from_dbc_message(mdict, platform_hint=platform_hint)
            class_counts[cand] = class_counts.get(cand, 0) + 1
            msg_rows.append(
                {
                    "vehicle_id": result.vehicle_id,
                    "source_dbc": entry["file"],
                    "bus": entry.get("bus", "vehicle_can"),
                    "id_hex": msg.id_hex,
                    "id_dec": msg.arbitration_id,
                    "name": msg.name,
                    "dlc": msg.dlc,
                    "sender": msg.sender,
                    "signal_count": len(msg.signals),
                    "cluster_candidate_class": cand,
                    "knowledge_level": "VEHICLE_PROTOCOL_DOCUMENTED",
                }
            )
            for sig in msg.signals:
                sdict = sig.to_dict()
                sig_rows.append(
                    {
                        "vehicle_id": result.vehicle_id,
                        "source_dbc": entry["file"],
                        "bus": entry.get("bus", "vehicle_can"),
                        "message": msg.name,
                        "id_hex": msg.id_hex,
                        "signal": sig.name,
                        "taxonomy": sdict.get("taxonomy"),
                        "start_bit": sig.start_bit,
                        "length": sig.length,
                        "byte_order": sig.byte_order,
                        "signed": sig.is_signed,
                        "scale": sig.scale,
                        "offset": sig.offset,
                        "unit": sig.unit or "",
                        "knowledge_level": sdict.get("knowledge_level"),
                        "cluster_candidate_class": cand,
                    }
                )
        vehicle_summary["cluster_candidate_counts"] = class_counts
        inventory["vehicles"].append(vehicle_summary)
        inventory["dbc_count"] += 1
        inventory["message_count"] += len(result.messages)
        inventory["signal_count"] += sum(len(m.signals) for m in result.messages)

    inv_path = dest / "dbc_inventory.json"
    inv_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")

    msg_csv = dest / "dbc_messages.csv"
    with msg_csv.open("w", newline="", encoding="utf-8") as f:
        if msg_rows:
            w = csv.DictWriter(f, fieldnames=list(msg_rows[0].keys()))
            w.writeheader()
            w.writerows(msg_rows)
        else:
            f.write("vehicle_id,name\n")

    sig_csv = dest / "dbc_signals.csv"
    with sig_csv.open("w", newline="", encoding="utf-8") as f:
        if sig_rows:
            w = csv.DictWriter(f, fieldnames=list(sig_rows[0].keys()))
            w.writeheader()
            w.writerows(sig_rows)
        else:
            f.write("vehicle_id,signal\n")

    return {
        "inventory": inventory,
        "paths": {"json": inv_path, "messages_csv": msg_csv, "signals_csv": sig_csv},
        "message_rows": msg_rows,
        "signal_rows": sig_rows,
    }
