"""Adaptation planner — documentation-only readiness matrix."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendashcan.adaptation.environment import ClusterEnvironment
from opendashcan.adaptation.readiness import Readiness, classify_signal_readiness
from opendashcan.core.confidence import Confidence
from opendashcan.registry import get_registry
from opendashcan.registry.models import PlatformPackage


@dataclass
class SignalPlanRow:
    signal: str
    source_confidence: str
    target_confidence: str
    priority: str
    translation: str
    readiness: Readiness
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal": self.signal,
            "source_confidence": self.source_confidence,
            "target_confidence": self.target_confidence,
            "priority": self.priority,
            "translation": self.translation,
            "readiness": self.readiness.value,
            "notes": self.notes,
        }


@dataclass
class AdaptationPlan:
    source_id: str
    cluster_id: str
    source_platform: PlatformPackage
    target_platform: PlatformPackage
    environment: ClusterEnvironment
    rows: list[SignalPlanRow] = field(default_factory=list)
    mode: str = "DOCUMENTATION_ONLY"
    physical_compatibility: str = "NOT_VALIDATED"
    electrical_compatibility: str = "NOT_VALIDATED"
    protocol_compatibility: str = "INCOMPLETE"

    def readiness_summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in self.rows:
            key = row.readiness.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def format_text(self) -> str:
        src = self.source_platform.vehicle
        tgt = self.target_platform.cluster
        lines = [
            "MODE: DOCUMENTATION_ONLY (no hardware required)",
            "",
            "SOURCE VEHICLE",
            f"  {self.source_id}",
            (
                f"  {src.manufacturer} {src.model} gen {src.generation} "
                f"({src.years_start}-{src.years_end})"
            ),
            "",
            "SOURCE NETWORKS",
        ]
        for bus in self.source_platform.buses:
            rate = bus.bitrate if bus.bitrate is not None else "UNKNOWN"
            name = bus.manufacturer_name or bus.bus_id
            lines.append(f"  {name} bitrate={rate} confidence={bus.confidence.value}")
        lines += ["", "TARGET CLUSTER"]
        if tgt:
            lines.append(
                f"  {tgt.cluster_id} display={tgt.display_type} status={tgt.compatibility_status}"
            )
        else:
            lines.append(f"  {self.cluster_id} (no cluster.yaml)")
        lines += [
            "",
            f"{'SIGNAL':<32} {'SOURCE':<14} {'TARGET':<14} {'PRIORITY':<10} {'READINESS'}",
            "-" * 100,
        ]
        for row in self.rows:
            lines.append(
                f"{row.signal:<32} {row.source_confidence:<14} {row.target_confidence:<14} "
                f"{row.priority:<10} {row.readiness.value}"
            )
        lines += [
            "",
            "COMPATIBILITY",
            f"  physical:  {self.physical_compatibility}",
            f"  electrical:{self.electrical_compatibility}",
            f"  protocol:  {self.protocol_compatibility}",
            "",
            "READINESS SUMMARY",
        ]
        for k, v in sorted(self.readiness_summary().items()):
            lines.append(f"  {k}: {v}")
        unknowns = self.environment.unknowns
        if unknowns:
            lines += ["", "UNKNOWNS / GAPS"]
            for u in unknowns[:40]:
                lines.append(f"  - {u}")
        lines += [
            "",
            "Never claim hardware compatibility from this plan alone.",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "source_id": self.source_id,
            "cluster_id": self.cluster_id,
            "physical_compatibility": self.physical_compatibility,
            "electrical_compatibility": self.electrical_compatibility,
            "protocol_compatibility": self.protocol_compatibility,
            "rows": [r.to_dict() for r in self.rows],
            "readiness_summary": self.readiness_summary(),
            "environment": self.environment.gap_report(),
        }


def _conf_str(pkg: PlatformPackage, signal: str) -> str:
    enc = pkg.signal_map().get(signal)
    if enc is None:
        return Confidence.UNKNOWN.value
    return enc.confidence.value


def plan(vehicle: str, cluster: str) -> AdaptationPlan:
    """Build an adaptation plan for source vehicle → target cluster."""
    reg = get_registry()
    source = reg.get(vehicle)
    target = reg.get_cluster(cluster)
    env = ClusterEnvironment.from_package(target)

    # Union of source signals, target signals, and target requirements
    signal_names: set[str] = set(source.signal_map()) | set(target.signal_map())
    req_by_signal: dict[str, str] = {}
    for req in target.requirements:
        if req.signal:
            signal_names.add(req.signal)
            req_by_signal[req.signal] = req.priority

    rows: list[SignalPlanRow] = []
    for sig in sorted(signal_names):
        src_c = _conf_str(source, sig)
        tgt_c = _conf_str(target, sig)
        priority = req_by_signal.get(sig, "UNKNOWN")
        readiness = classify_signal_readiness(
            source_confidence=src_c, target_confidence=tgt_c, priority=priority
        )
        if readiness == Readiness.READY_FROM_DOCUMENTATION:
            translation = "possible"
        elif readiness == Readiness.PARTIAL:
            translation = "incomplete"
        elif readiness == Readiness.BLOCKED_SOURCE:
            translation = "BLOCKED_SOURCE"
        else:
            translation = "blocked"
        notes = ""
        src_enc = source.signal_map().get(sig)
        tgt_enc = target.signal_map().get(sig)
        if src_enc and src_enc.notes:
            notes = src_enc.notes
        elif tgt_enc and tgt_enc.notes:
            notes = tgt_enc.notes
        rows.append(
            SignalPlanRow(
                signal=sig,
                source_confidence=src_c,
                target_confidence=tgt_c,
                priority=priority,
                translation=translation,
                readiness=readiness,
                notes=notes or "",
            )
        )

    # Protocol compatibility heuristic
    ready = sum(1 for r in rows if r.readiness == Readiness.READY_FROM_DOCUMENTATION)
    blocked = sum(
        1
        for r in rows
        if r.readiness
        in (
            Readiness.BLOCKED_SOURCE,
            Readiness.REQUIRES_CAN_CAPTURE,
            Readiness.REQUIRES_BENCH_TEST,
        )
    )
    # Source-unknown with documented target still counts as PARTIAL protocol progress
    blocked_source_only = all(
        r.readiness
        in (
            Readiness.BLOCKED_SOURCE,
            Readiness.READY_FROM_DOCUMENTATION,
            Readiness.PARTIAL,
            Readiness.REQUIRES_BENCH_TEST,
        )
        for r in rows
    ) and any(r.readiness == Readiness.BLOCKED_SOURCE for r in rows)
    if ready and not blocked:
        proto = "DOCUMENTATION_READY"
    elif ready or blocked_source_only:
        proto = "PARTIAL"
    else:
        proto = "INCOMPLETE"

    cluster_id = target.cluster.cluster_id if target.cluster else cluster
    return AdaptationPlan(
        source_id=vehicle,
        cluster_id=cluster_id,
        source_platform=source,
        target_platform=target,
        environment=env,
        rows=rows,
        protocol_compatibility=proto,
    )
