"""Timing database with separate provenance — UNKNOWN if not established."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from opendashcan.cluster.environment_loader import list_cluster_envs, load_cluster_env

REPO_ROOT = Path(__file__).resolve().parents[2]


def build_timing_database() -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for key in list_cluster_envs():
        env = load_cluster_env(key)
        for req in env.requirement_rows():
            period = req.get("period_ms", "UNKNOWN")
            entries.append(
                {
                    "cluster": key,
                    "signal": req.get("signal"),
                    "arbitration_id": req.get("arbitration_id"),
                    "period_ms": period if period is not None else "UNKNOWN",
                    "provenance": req.get("timing_provenance", "UNKNOWN"),
                    "note": (
                        "Vehicle DBC cycle time is not automatically cluster requirement"
                        if period == "UNKNOWN" or period is None
                        else None
                    ),
                }
            )
        for msg in env.rx_rows():
            entries.append(
                {
                    "cluster": key,
                    "signal": None,
                    "message": msg.get("name"),
                    "arbitration_id": msg.get("arbitration_id"),
                    "period_ms": msg.get("period_ms", "UNKNOWN"),
                    "provenance": msg.get("timing_provenance", "UNKNOWN"),
                }
            )
    return {
        "warning": "period_ms UNKNOWN unless independently established. DBC ≠ cluster timing.",
        "entries": entries,
        "unknown_count": sum(1 for e in entries if e.get("period_ms") in (None, "UNKNOWN")),
        "known_count": sum(1 for e in entries if e.get("period_ms") not in (None, "UNKNOWN")),
    }


def write_timing_database(path: Path | None = None) -> Path:
    out = path or (REPO_ROOT / "dist" / "timing_database.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_timing_database(), indent=2) + "\n", encoding="utf-8")
    return out
