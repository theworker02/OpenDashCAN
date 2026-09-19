"""Conflict engine — preserve contradictions; never silent-resolve."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from opendashcan.analysis.lineage import build_lineage
from opendashcan.registry import get_registry

REPO_ROOT = Path(__file__).resolve().parents[2]


def collect_conflicts() -> dict[str, Any]:
    reg = get_registry()
    registry_conflicts: list[dict[str, Any]] = []
    for pkg in reg.list_platforms():
        for c in pkg.conflicts or []:
            registry_conflicts.append(
                {
                    "platform_id": pkg.platform_id,
                    "conflict": c if isinstance(c, str) else str(c),
                    "status": "REQUIRES_REVIEW",
                }
            )
        # Also load conflicts.yaml raw if present via package path
        if pkg.vehicle.path:
            cpath = pkg.vehicle.path / "conflicts.yaml"
            if cpath.is_file():
                import yaml

                data = yaml.safe_load(cpath.read_text(encoding="utf-8")) or {}
                for item in data.get("conflicts") or []:
                    registry_conflicts.append(
                        {
                            "platform_id": pkg.platform_id,
                            "conflict": item,
                            "status": "REQUIRES_REVIEW",
                            "source": str(cpath).replace("\\", "/"),
                        }
                    )

    lineage = build_lineage()
    encoding_conflicts = []
    for g in lineage["id_groups"]:
        if g["identical_across_all"]:
            continue
        if g["vehicle_count"] < 2:
            continue
        encoding_conflicts.append(
            {
                "arbitration_id": g["arbitration_id"],
                "names": g["names"],
                "vehicles": g["vehicles"],
                "variant_count": g["encoding_variant_count"],
                "status": "REQUIRES_REVIEW",
                "detail": "Same CAN ID, divergent encodings across Honda DBCs",
            }
        )
    for c in lineage["name_collisions"]:
        encoding_conflicts.append(
            {
                "name": c["name"],
                "ids": c["ids"],
                "vehicles": c["vehicles"],
                "status": "REQUIRES_REVIEW",
                "detail": c["warning"],
            }
        )

    return {
        "warning": "Conflicts are preserved. Do not silent-resolve.",
        "registry_conflicts": registry_conflicts,
        "lineage_encoding_conflicts": encoding_conflicts,
        "counts": {
            "registry": len(registry_conflicts),
            "lineage_encoding": len(encoding_conflicts),
        },
    }


def format_conflicts_text(data: dict[str, Any] | None = None) -> str:
    data = data or collect_conflicts()
    lines = [
        "CONFLICTS (REQUIRES_REVIEW)",
        data["warning"],
        "",
        f"registry: {data['counts']['registry']}",
        f"lineage_encoding: {data['counts']['lineage_encoding']}",
        "",
        "## Registry",
    ]
    for c in data["registry_conflicts"][:50]:
        lines.append(f"- [{c['platform_id']}] {c['conflict']}")
    lines += ["", "## Lineage encoding"]
    for c in data["lineage_encoding_conflicts"][:50]:
        aid = c.get("arbitration_id") or c.get("name")
        lines.append(
            f"- {aid}: {c.get('detail')} vehicles={c.get('vehicles')}"
        )
    lines.append("")
    return "\n".join(lines)


def write_conflicts_json(path: Path | None = None) -> Path:
    out = path or (REPO_ROOT / "dist" / "conflicts.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(collect_conflicts(), indent=2, default=str) + "\n", encoding="utf-8")
    return out
