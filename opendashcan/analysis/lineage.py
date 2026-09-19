"""Cross-Honda message lineage — matching names ≠ identical encoding."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX_DIR = REPO_ROOT / "dbc" / "opendbc" / "index"


def _load_indexed_messages() -> list[dict[str, Any]]:
    """Prefer already-imported JSON indexes to avoid re-parsing when present."""
    rows: list[dict[str, Any]] = []
    if INDEX_DIR.is_dir():
        for path in sorted(INDEX_DIR.glob("*_generated.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            vehicle = data.get("vehicle_id") or path.stem
            bus = (data.get("provenance") or {}).get("bus", "vehicle_can")
            for msg in data.get("messages") or []:
                rows.append(
                    {
                        "vehicle_id": vehicle,
                        "source_dbc": (data.get("provenance") or {}).get("source_dbc"),
                        "bus": bus,
                        "id_dec": msg.get("id_dec"),
                        "id_hex": msg.get("id_hex"),
                        "name": msg.get("name"),
                        "dlc": msg.get("dlc"),
                        "sender": msg.get("sender"),
                        "signals": [
                            {
                                "name": s.get("name"),
                                "taxonomy": s.get("taxonomy"),
                                "start_bit": s.get("start_bit"),
                                "length": s.get("length"),
                                "byte_order": s.get("byte_order"),
                                "signed": s.get("signed"),
                                "scale": s.get("scale"),
                                "offset": s.get("offset"),
                                "unit": s.get("unit"),
                            }
                            for s in (msg.get("signals") or [])
                        ],
                    }
                )
    return rows


def _sig_fingerprint(sig: dict[str, Any]) -> tuple[Any, ...]:
    return (
        sig.get("name"),
        sig.get("start_bit"),
        sig.get("length"),
        sig.get("byte_order"),
        sig.get("signed"),
        sig.get("scale"),
        sig.get("offset"),
    )


def _message_fingerprint(msg: dict[str, Any]) -> tuple[Any, ...]:
    sigs = tuple(sorted(_sig_fingerprint(s) for s in msg.get("signals") or []))
    return (msg.get("id_dec"), msg.get("dlc"), msg.get("name"), sigs)


def compare_encodings(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Compare two message instances; names matching is not identity."""
    diffs: list[str] = []
    same_id = a.get("id_dec") == b.get("id_dec")
    same_dlc = a.get("dlc") == b.get("dlc")
    same_name = a.get("name") == b.get("name")
    if not same_id:
        diffs.append(f"id {a.get('id_hex')} vs {b.get('id_hex')}")
    if not same_dlc:
        diffs.append(f"dlc {a.get('dlc')} vs {b.get('dlc')}")
    if not same_name:
        diffs.append(f"name {a.get('name')} vs {b.get('name')}")

    by_name_a = {s["name"]: s for s in a.get("signals") or [] if s.get("name")}
    by_name_b = {s["name"]: s for s in b.get("signals") or [] if s.get("name")}
    only_a = sorted(set(by_name_a) - set(by_name_b))
    only_b = sorted(set(by_name_b) - set(by_name_a))
    encoding_mismatches: list[dict[str, Any]] = []
    for name in sorted(set(by_name_a) & set(by_name_b)):
        fa, fb = _sig_fingerprint(by_name_a[name]), _sig_fingerprint(by_name_b[name])
        if fa != fb:
            encoding_mismatches.append(
                {
                    "signal": name,
                    "a": by_name_a[name],
                    "b": by_name_b[name],
                }
            )
    identical = (
        same_id
        and same_dlc
        and same_name
        and not only_a
        and not only_b
        and not encoding_mismatches
    )
    return {
        "identical_encoding": identical,
        "same_id": same_id,
        "same_dlc": same_dlc,
        "same_name": same_name,
        "signals_only_in_a": only_a,
        "signals_only_in_b": only_b,
        "encoding_mismatches": encoding_mismatches,
        "diffs": diffs,
        "note": "Matching message/signal names do NOT imply identical encoding.",
    }


def build_lineage(*, messages: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    msgs = messages if messages is not None else _load_indexed_messages()
    by_id: dict[int, list[dict[str, Any]]] = defaultdict(list)
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for m in msgs:
        if m.get("id_dec") is not None:
            by_id[int(m["id_dec"])].append(m)
        if m.get("name"):
            by_name[str(m["name"])].append(m)

    id_groups: list[dict[str, Any]] = []
    for aid, group in sorted(by_id.items()):
        vehicles = sorted({g["vehicle_id"] for g in group if g.get("vehicle_id")})
        fps = {_message_fingerprint(g) for g in group}
        # Pairwise: pick first as reference, compare others
        ref = group[0]
        variants: list[dict[str, Any]] = []
        for other in group[1:]:
            cmp = compare_encodings(ref, other)
            if not cmp["identical_encoding"]:
                variants.append(
                    {
                        "vehicle_id": other.get("vehicle_id"),
                        "vs_reference": ref.get("vehicle_id"),
                        **cmp,
                    }
                )
        # Checksum / counter signal presence
        has_checksum = any(
            any("CHECKSUM" in str(s.get("name", "")).upper() for s in (g.get("signals") or []))
            for g in group
        )
        has_counter = any(
            any("COUNTER" in str(s.get("name", "")).upper() for s in (g.get("signals") or []))
            for g in group
        )
        id_groups.append(
            {
                "arbitration_id": hex(aid) if aid <= 0x7FF else f"0x{aid:08X}",
                "id_dec": aid,
                "names": sorted({g.get("name") for g in group if g.get("name")}),
                "vehicles": vehicles,
                "vehicle_count": len(vehicles),
                "encoding_variant_count": len(fps),
                "identical_across_all": len(fps) == 1,
                "has_checksum_signal": has_checksum,
                "has_counter_signal": has_counter,
                "encoding_differences": variants[:20],  # cap for size
            }
        )

    # Name collisions across different IDs
    name_collisions = []
    for name, group in sorted(by_name.items()):
        ids = sorted({g.get("id_dec") for g in group if g.get("id_dec") is not None})
        if len(ids) > 1:
            name_collisions.append(
                {
                    "name": name,
                    "ids": [hex(i) if i <= 0x7FF else f"0x{i:08X}" for i in ids],
                    "vehicles": sorted({g["vehicle_id"] for g in group}),
                    "warning": "Same message name on different CAN IDs across platforms",
                }
            )

    return {
        "warning": (
            "Lineage is vehicle-protocol comparison from public DBC. "
            "CROSS_PLATFORM_CANDIDATE ≠ Civic definition. "
            "Matching names ≠ identical encoding."
        ),
        "message_instances": len(msgs),
        "unique_ids": len(by_id),
        "id_groups": id_groups,
        "name_collisions": name_collisions,
        "stable_ids_identical_encoding": [
            g["arbitration_id"]
            for g in id_groups
            if g["identical_across_all"] and g["vehicle_count"] >= 2
        ],
        "divergent_ids": [
            g["arbitration_id"] for g in id_groups if not g["identical_across_all"]
        ],
    }


def write_lineage_artifacts(
    lineage: dict[str, Any] | None = None,
    *,
    dist: Path | None = None,
    research: Path | None = None,
) -> dict[str, Path]:
    data = lineage or build_lineage()
    dist_dir = dist or (REPO_ROOT / "dist")
    research_dir = research or (REPO_ROOT / "research")
    dist_dir.mkdir(parents=True, exist_ok=True)
    research_dir.mkdir(parents=True, exist_ok=True)

    json_path = dist_dir / "honda_message_lineage.json"
    json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Honda Message Lineage",
        "",
        "_Auto-generated from public opendbc Honda/Acura DBC indexes._",
        "",
        data["warning"],
        "",
        f"- Message instances: **{data['message_instances']}**",
        f"- Unique CAN IDs: **{data['unique_ids']}**",
        f"- IDs with identical encoding across ≥2 vehicles: "
        f"**{len(data['stable_ids_identical_encoding'])}**",
        f"- IDs with encoding divergence: **{len(data['divergent_ids'])}**",
        f"- Same-name / different-ID collisions: **{len(data['name_collisions'])}**",
        "",
        "## Stable IDs (identical encoding)",
        "",
    ]
    for aid in data["stable_ids_identical_encoding"][:40]:
        lines.append(f"- `{aid}`")
    if len(data["stable_ids_identical_encoding"]) > 40:
        lines.append(f"- … ({len(data['stable_ids_identical_encoding']) - 40} more)")
    lines += ["", "## Divergent IDs (do not assume copy-paste)", ""]
    for g in data["id_groups"]:
        if g["identical_across_all"]:
            continue
        lines.append(
            f"- `{g['arbitration_id']}` names={g['names']} "
            f"vehicles={g['vehicle_count']} variants={g['encoding_variant_count']}"
        )
        for d in g["encoding_differences"][:3]:
            lines.append(
                f"  - vs `{d.get('vehicle_id')}`: mismatches={len(d.get('encoding_mismatches') or [])} "
                f"only_a={d.get('signals_only_in_a')} only_b={d.get('signals_only_in_b')}"
            )
    lines += ["", "## Name collisions (different IDs)", ""]
    for c in data["name_collisions"][:30]:
        lines.append(f"- `{c['name']}` → {', '.join(c['ids'])}")
    lines += [
        "",
        "## Policy",
        "",
        "- Never copy Accord fuel (or any absent signal) into Civic.",
        "- `CROSS_PLATFORM_CANDIDATE` is a lead, not a Civic definition.",
        "- DBC presence ≠ `CLUSTER_RX_CONFIRMED`.",
        "",
    ]
    md_path = research_dir / "HONDA_MESSAGE_LINEAGE.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": json_path, "md": md_path}
