"""Compile an adaptation specification into dist/adapters/<id>/."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from opendashcan.adaptation.planner import plan
from opendashcan.adaptation.readiness import Readiness
from opendashcan.adaptation.virtual_cluster import VirtualCluster, run_software_validation
from opendashcan.registry.ids import adapter_id as make_adapter_id

REPO_ROOT = Path(__file__).resolve().parents[2]
DIST_ADAPTERS = REPO_ROOT / "dist" / "adapters"


class AdapterStatus(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"


def _classify(adaptation: Any) -> AdapterStatus:
    summary = adaptation.readiness_summary()
    ready = summary.get(Readiness.READY_FROM_DOCUMENTATION.value, 0)
    blocked = sum(
        summary.get(k, 0)
        for k in (
            Readiness.BLOCKED_SOURCE.value,
            Readiness.REQUIRES_CAN_CAPTURE.value,
            Readiness.REQUIRES_BENCH_TEST.value,
            Readiness.REQUIRES_VEHICLE_TEST.value,
        )
    )
    partial = summary.get(Readiness.PARTIAL.value, 0)
    if ready and not blocked and not partial:
        return AdapterStatus.COMPLETE
    # Target-side documentation with unknown source encodings → PARTIAL (not COMPLETE)
    documented_target = any(
        r.target_confidence
        in (
            "DOCUMENTED",
            "SUPPORTED_BY_MULTIPLE_SOURCES",
            "CAPTURE_VERIFIED",
            "PHYSICALLY_VERIFIED",
            "VERIFIED",
        )
        for r in adaptation.rows
    )
    if ready or partial or documented_target or adaptation.protocol_compatibility == "PARTIAL":
        return AdapterStatus.PARTIAL
    if blocked and not ready:
        return AdapterStatus.BLOCKED
    return AdapterStatus.PARTIAL


def build_adapter(
    source: str,
    target: str,
    *,
    output_root: Path | None = None,
    documentation_only: bool = True,
) -> Path:
    """Gather plan + evidence into a portable adapter directory.

    Does not flash hardware. DOCUMENTATION_ONLY / SOFTWARE VALIDATION ONLY.
    Status is COMPLETE | PARTIAL | BLOCKED based on readiness — never invents
    encodings to force COMPLETE.
    """
    adaptation = plan(source, target)
    aid = make_adapter_id(source, target)
    status = _classify(adaptation)
    out = (output_root or DIST_ADAPTERS) / aid
    out.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "adapter_id": aid,
        "source": source,
        "target": target,
        "cluster_id": adaptation.cluster_id,
        "mode": "DOCUMENTATION_ONLY" if documentation_only else adaptation.mode,
        "status": status.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "protocol_compatibility": adaptation.protocol_compatibility,
        "physical_compatibility": adaptation.physical_compatibility,
        "electrical_compatibility": adaptation.electrical_compatibility,
        "label": "SOFTWARE VALIDATION ONLY — no hardware claim",
        "documentation_only": documentation_only,
    }
    (out / "adapter_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    signal_map = {
        "signals": [r.to_dict() for r in adaptation.rows],
        "readiness_summary": adaptation.readiness_summary(),
        "status": status.value,
    }
    (out / "signal_map.json").write_text(json.dumps(signal_map, indent=2) + "\n", encoding="utf-8")

    required_messages = [
        m
        for m in adaptation.environment.expected_messages
        if m.get("confidence") not in (None, "UNKNOWN")
    ]
    (out / "required_messages.json").write_text(
        json.dumps({"messages": required_messages}, indent=2) + "\n", encoding="utf-8"
    )

    unknowns = {
        "environment_unknowns": adaptation.environment.unknowns,
        "blocked_signals": [r.to_dict() for r in adaptation.rows if r.translation == "blocked"],
        "status": status.value,
    }
    (out / "unknowns.json").write_text(json.dumps(unknowns, indent=2) + "\n", encoding="utf-8")

    evidence: dict[str, Any] = {
        "source_evidence_ids": sorted(adaptation.source_platform.evidence_index.keys()),
        "target_evidence_ids": sorted(adaptation.target_platform.evidence_index.keys()),
        "source_records": adaptation.source_platform.evidence_index,
        "target_records": adaptation.target_platform.evidence_index,
    }
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    report: dict[str, Any] = {
        "label": "SOFTWARE VALIDATION ONLY",
        "documentation_only": documentation_only,
        "encoder_available": False,
        "frames_emitted": 0,
        "output_kind": "NO_OUTPUT",
        "virtual_cluster": None,
        "notes": [],
        "status": status.value,
    }
    try:
        from opendashcan.registry import get_encoder

        # Explicit SYNTHETIC path for software_test_report only (not production TX).
        encoder = get_encoder(target, emit_synthetic_research=True)
        report["encoder_available"] = True
        from opendashcan.core.state import Confidence, SignalValue, Validity, VehicleState

        state = VehicleState()
        state.engine_rpm = SignalValue(
            1500.0, confidence=Confidence.INFERRED, validity=Validity.VALID
        )
        state.vehicle_speed = SignalValue(
            40.0, confidence=Confidence.INFERRED, validity=Validity.VALID
        )
        frames = encoder.encode(state, timestamp=0.0)
        report["frames_emitted"] = len(frames)
        kind_obj = encoder.last_output_kind() if hasattr(encoder, "last_output_kind") else None
        if kind_obj is not None and hasattr(kind_obj, "value"):
            report["output_kind"] = str(kind_obj.value)
        elif kind_obj is not None:
            report["output_kind"] = str(kind_obj)
        vc = VirtualCluster(cluster_id=adaptation.cluster_id)
        summary = run_software_validation(vc, frames)
        report["virtual_cluster"] = summary
        report["notes"].append(
            "software_test_report may use SYNTHETIC frames for virtual-cluster "
            "checks only. SOFTWARE VALIDATION ONLY — no hardware claim."
        )
    except KeyError:
        report["notes"].append(f"No encoder registered for {target!r}; skipped encode path.")
    except TypeError:
        report["notes"].append("Encoder call failed; skipped software encode path.")

    (out / "software_test_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (out / "adaptation_plan.json").write_text(
        json.dumps(adaptation.to_dict(), indent=2) + "\n", encoding="utf-8"
    )
    (out / "status.json").write_text(
        json.dumps({"status": status.value, "adapter_id": aid}, indent=2) + "\n",
        encoding="utf-8",
    )

    # Phase 4: per-function SOURCE/TARGET/TRANSLATION/TIMING/INTEGRITY/CLUSTER RX/VALIDATION
    try:
        from opendashcan.cluster.gaps import build_gap_report
        from opendashcan.cluster.environment_loader import CLUSTER_ALIASES

        gap_key = CLUSTER_ALIASES.get(target) or CLUSTER_ALIASES.get(adaptation.cluster_id)
        if gap_key:
            gap = build_gap_report(
                gap_key,
                source_confidence_map={
                    r.signal: r.source_confidence for r in adaptation.rows
                },
            )
            functions = []
            for row in gap["rows"]:
                axes = row["axes"]
                plan_row = next((r for r in adaptation.rows if r.signal == row["signal"]), None)
                functions.append(
                    {
                        "signal": row["signal"],
                        "SOURCE": axes["A"],
                        "TARGET": axes["B"],
                        "TRANSLATION": (
                            plan_row.translation if plan_row else "UNKNOWN"
                        ),
                        "PRODUCER": axes["C"],
                        "BUS": axes["D"],
                        "CLUSTER_RX": axes["E"],
                        "TIMING": axes["F"],
                        "INTEGRITY": axes["G"],
                        "VALIDATION": axes["H"],
                        "overall": row["overall"],
                        "priority": row["priority"],
                    }
                )
            (out / "function_axes.json").write_text(
                json.dumps(
                    {
                        "cluster": gap_key,
                        "warning": "Source UNKNOWN does not erase target documentation",
                        "functions": functions,
                        "completeness": gap["completeness"],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
    except Exception as exc:  # noqa: BLE001
        (out / "function_axes.json").write_text(
            json.dumps({"error": str(exc), "status": "SKIPPED"}, indent=2) + "\n",
            encoding="utf-8",
        )

    return out
