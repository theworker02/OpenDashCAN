"""Eight-axis cluster requirement resolution and gap reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from opendashcan.cluster.environment_loader import ClusterEnvPackage, load_cluster_env
from opendashcan.core.donor_knowledge import CLUSTER_RELEVANT_TAXONOMY, DonorKnowledge
from opendashcan.dbc import taxonomy_implementations_from_imports

AXES = ("A", "B", "C", "D", "E", "F", "G", "H")

AXIS_LABELS = {
    "A": "source_signal_encoding",
    "B": "donor_representation",
    "C": "producer_ecu",
    "D": "bus",
    "E": "cluster_rx",
    "F": "timing",
    "G": "integrity",
    "H": "demonstrated",
}


@dataclass
class AxisStatus:
    axis: str
    label: str
    status: str  # DOCUMENTED | COMMUNITY_RESEARCH | UNKNOWN | ABSENT | N/A
    detail: str = ""
    evidence_to_close: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "axis": self.axis,
            "label": self.label,
            "status": self.status,
            "detail": self.detail,
            "evidence_to_close": self.evidence_to_close,
        }


@dataclass
class SignalGapRow:
    signal: str
    priority: str
    axes: dict[str, AxisStatus] = field(default_factory=dict)
    overall: str = "UNKNOWN"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal": self.signal,
            "priority": self.priority,
            "overall": self.overall,
            "notes": self.notes,
            "axes": {k: v.to_dict() for k, v in self.axes.items()},
        }


def _axis(letter: str, status: str, detail: str = "", close: str = "") -> AxisStatus:
    return AxisStatus(
        axis=letter,
        label=AXIS_LABELS[letter],
        status=status,
        detail=detail,
        evidence_to_close=close,
    )


def _donor_impl(signal: str, platform_hint: str | None) -> dict[str, Any] | None:
    index = Path("dbc/opendbc/index")
    cross = taxonomy_implementations_from_imports(index)
    rows = cross.get(signal) or []
    if not rows:
        return None
    if platform_hint:
        for r in rows:
            vid = str(r.get("vehicle_id") or "")
            if platform_hint.split(".")[2] in vid or platform_hint in vid:
                return r
            # civic.gen10 match touring/hatch vehicle ids
            parts = platform_hint.split(".")
            if len(parts) >= 3 and parts[1] in vid and parts[2] in vid:
                return r
    return rows[0]


def resolve_signal_axes(
    signal: str,
    req: dict[str, Any],
    env: ClusterEnvPackage,
    *,
    source_confidence: str | None = None,
) -> SignalGapRow:
    """Resolve A–H for one display function from env YAML + donor DBC index."""
    platform = env.platform_id
    donor = _donor_impl(signal, platform)
    rx_class = str(req.get("cluster_rx_class") or req.get("rx_class") or "UNKNOWN")
    priority = str(req.get("priority") or "UNKNOWN")
    notes = str(req.get("notes") or "")

    # A — source encoding (caller may pass Civic8 UNKNOWN)
    src = (source_confidence or req.get("source_confidence") or "UNKNOWN").upper()
    if src in ("DOCUMENTED", "SUPPORTED_BY_MULTIPLE_SOURCES", "CAPTURE_VERIFIED"):
        a = _axis("A", "DOCUMENTED", f"source confidence={src}")
    elif src == "UNKNOWN":
        a = _axis(
            "A",
            "UNKNOWN",
            "Source vehicle encoding UNKNOWN",
            "Capture source vehicle F-CAN with ground-truth RPM/speed to map bytes",
        )
    else:
        a = _axis("A", src, f"source confidence={src}")

    # B — donor representation (vehicle-bus DBC)
    if donor:
        b = _axis(
            "B",
            "DOCUMENTED",
            (
                f"{donor.get('message')} {donor.get('arbitration_id')} "
                f"start={donor.get('start_bit')}|{donor.get('length')} "
                f"scale={donor.get('scale')} ({DonorKnowledge.VEHICLE_PROTOCOL_DOCUMENTED.value})"
            ),
        )
    elif signal in (
        "fuel.level",
        "powertrain.coolant_temperature",
        "safety.srs_warning",
        "safety.check_engine",
        "brakes.abs_warning",
    ):
        b = _axis(
            "B",
            "ABSENT",
            "Explicitly absent from public Honda opendbc DBC",
            "Find non-public DBC, service tool log, or bench reverse-engineering",
        )
    else:
        b = _axis(
            "B",
            "UNKNOWN",
            "No taxonomy mapping in imported DBC indexes",
            "Map DBC signal name → taxonomy or document absence",
        )

    # C — producer ECU
    if req.get("producer") and req.get("producer") != "UNKNOWN":
        c = _axis("C", "DOCUMENTED", str(req["producer"]))
    elif donor:
        c = _axis(
            "C",
            "INFERRED",
            "DBC sender field present on message — treat as vehicle-protocol only",
            "Confirm TX ECU via capture / service literature",
        )
    else:
        c = _axis("C", "UNKNOWN", "Producer ECU UNKNOWN", "Identify transmitting module")

    # D — bus
    bus = req.get("bus") or env.environment.get("primary_bus") or "UNKNOWN"
    if bus and bus != "UNKNOWN":
        d = _axis(
            "D", "DOCUMENTED" if req.get("bus_confidence") != "UNKNOWN" else "INFERRED", str(bus)
        )
    else:
        d = _axis("D", "UNKNOWN", "Bus UNKNOWN", "Confirm cluster tap bus (F-CAN vs B-CAN)")

    # E — cluster RX (never promote DBC → CONFIRMED)
    if rx_class == "CLUSTER_CONFIRMED_RX":
        e = _axis("E", "DOCUMENTED", "CLUSTER_CONFIRMED_RX (bench/capture)")
    elif rx_class == "CLUSTER_LIKELY_RX":
        e = _axis(
            "E",
            "COMMUNITY_RESEARCH",
            "CLUSTER_LIKELY_RX — not CONFIRMED",
            "Bench: omit frame and observe gauge; or capture at cluster connector",
        )
    elif rx_class in ("DISPLAY_RELEVANT", "CLUSTER_RELEVANT"):
        e = _axis(
            "E",
            "INFERRED",
            "display-relevant ≠ CLUSTER_RX",
            "Prove cluster consumes this ID (RX pin or fault-on-omit)",
        )
    else:
        e = _axis(
            "E",
            "UNKNOWN",
            f"cluster_rx_class={rx_class}",
            "Establish cluster RX with capture or controlled bench",
        )

    # F — timing
    period = req.get("period_ms")
    if period is None or period == "UNKNOWN":
        f = _axis(
            "F",
            "UNKNOWN",
            "period_ms UNKNOWN (vehicle DBC period ≠ cluster requirement)",
            "Measure period at cluster bus or document from OEM timing table",
        )
    else:
        f = _axis(
            "F",
            str(req.get("timing_provenance") or "DOCUMENTED"),
            f"period_ms={period} provenance={req.get('timing_provenance', 'UNKNOWN')}",
        )

    # G — integrity
    csum = (
        req.get("checksum") or req.get("integrity", {}).get("checksum")
        if isinstance(req.get("integrity"), dict)
        else req.get("checksum")
    )
    if isinstance(req.get("integrity"), dict):
        csum = req["integrity"].get("checksum_type") or req["integrity"].get("checksum")
        ctr = req["integrity"].get("counter_type") or req["integrity"].get("counter")
    else:
        ctr = req.get("counter")
    if csum and csum != "UNKNOWN":
        g = _axis(
            "G",
            "DOCUMENTED",
            f"checksum={csum} counter={ctr or 'UNKNOWN'} — vehicle-bus algorithm; "
            "cluster acceptance NOT BENCH_VERIFIED",
            "Verify cluster rejects bad checksum / accepts good (bench)",
        )
    else:
        g = _axis("G", "UNKNOWN", "Integrity UNKNOWN", "Document checksum/counter or prove none")

    # H — demonstrated
    demo = req.get("demonstrated") or "NONE"
    if demo in ("BENCH_VERIFIED", "CAPTURE_VERIFIED", "PHYSICALLY_VERIFIED"):
        h = _axis("H", "DOCUMENTED", demo)
    elif demo in ("COMMUNITY_RESEARCH", "COMMUNITY_REPORTED"):
        h = _axis(
            "H",
            "COMMUNITY_RESEARCH",
            demo,
            "Reproduce under controlled OpenDashCAN bench with logged frames",
        )
    else:
        h = _axis(
            "H", "UNKNOWN", "Not demonstrated in-repo", "Bench or vehicle test with artifacts"
        )

    axes = {"A": a, "B": b, "C": c, "D": d, "E": e, "F": f, "G": g, "H": h}

    # Overall: worst of E/B/H for cluster adaptation;
    # source A UNKNOWN → BLOCKED_SOURCE, not overall fail on target
    statuses = [axes[x].status for x in ("B", "E", "F", "G", "H")]
    if "ABSENT" in statuses:
        overall = "ABSENT_FROM_PUBLIC_DBC"
    elif all(s == "DOCUMENTED" for s in statuses):
        overall = "DONOR_SIDE_DOCUMENTED"
    elif "COMMUNITY_RESEARCH" in statuses or "INFERRED" in statuses:
        overall = "PARTIAL"
    else:
        overall = "UNKNOWN"

    if a.status == "UNKNOWN" and b.status == "DOCUMENTED":
        notes = (notes + " | ").lstrip(
            " |"
        ) + "TRANSLATION=BLOCKED_SOURCE (target donor encoding documented)"

    return SignalGapRow(
        signal=signal,
        priority=priority,
        axes=axes,
        overall=overall,
        notes=notes,
    )


def build_gap_report(
    cluster_name: str, *, source_confidence_map: dict[str, str] | None = None
) -> dict[str, Any]:
    env = load_cluster_env(cluster_name)
    src_map = source_confidence_map or {}
    rows: list[SignalGapRow] = []
    for req in env.requirement_rows():
        sig = req.get("signal")
        if not sig or sig == "UNKNOWN":
            continue
        rows.append(
            resolve_signal_axes(
                sig,
                req,
                env,
                source_confidence=src_map.get(sig),
            )
        )

    # Completeness axes counts (real numbers, not one fake %)
    axis_counts: dict[str, dict[str, int]] = {ax: {} for ax in AXES}
    overall_counts: dict[str, int] = {}
    for row in rows:
        overall_counts[row.overall] = overall_counts.get(row.overall, 0) + 1
        for ax, st in row.axes.items():
            axis_counts[ax][st.status] = axis_counts[ax].get(st.status, 0) + 1

    taxonomy_covered = sum(1 for r in rows if r.axes["B"].status == "DOCUMENTED")
    taxonomy_absent = sum(1 for r in rows if r.axes["B"].status == "ABSENT")
    rx_confirmed = sum(1 for r in rows if r.axes["E"].status == "DOCUMENTED")
    rx_likely = sum(
        1
        for r in rows
        if "LIKELY" in r.axes["E"].detail or r.axes["E"].status == "COMMUNITY_RESEARCH"
    )
    timing_known = sum(1 for r in rows if r.axes["F"].status not in ("UNKNOWN",))
    integrity_known = sum(1 for r in rows if r.axes["G"].status not in ("UNKNOWN",))
    demonstrated = sum(
        1 for r in rows if r.axes["H"].status in ("DOCUMENTED", "COMMUNITY_RESEARCH")
    )

    n = len(rows) or 1
    return {
        "cluster": env.key,
        "cluster_id": env.cluster_id,
        "platform_id": env.platform_id,
        "label": "DOCUMENTATION_ONLY — gaps are not hardware failures",
        "signal_count": len(rows),
        "rows": [r.to_dict() for r in rows],
        "completeness": {
            "signals_evaluated": len(rows),
            "donor_encoding_documented": taxonomy_covered,
            "donor_encoding_absent_public_dbc": taxonomy_absent,
            "donor_encoding_unknown": sum(1 for r in rows if r.axes["B"].status == "UNKNOWN"),
            "cluster_rx_confirmed": rx_confirmed,
            "cluster_rx_likely_or_community": rx_likely,
            "cluster_rx_unknown": sum(1 for r in rows if r.axes["E"].status == "UNKNOWN"),
            "timing_established": timing_known,
            "timing_unknown": len(rows) - timing_known,
            "integrity_algorithm_documented": integrity_known,
            "integrity_unknown": len(rows) - integrity_known,
            "demonstrated_any": demonstrated,
            "demonstrated_bench": sum(1 for r in rows if "BENCH" in r.axes["H"].detail.upper()),
            "fractions": {
                "donor_encoding_documented": round(taxonomy_covered / n, 3),
                "cluster_rx_confirmed": round(rx_confirmed / n, 3),
                "timing_established": round(timing_known / n, 3),
                "integrity_documented": round(integrity_known / n, 3),
                "demonstrated_any": round(demonstrated / n, 3),
            },
            "note": (
                "Fractions are per evaluated requirement signal. "
                "There is no single overall compatibility percentage."
            ),
        },
        "axis_status_counts": axis_counts,
        "overall_counts": overall_counts,
        "cluster_relevant_taxonomy_size": len(CLUSTER_RELEVANT_TAXONOMY),
    }


def format_gaps_text(report: dict[str, Any]) -> str:
    def _ascii(s: str) -> str:
        return (
            s.replace("\u2192", "->")
            .replace("\u2014", "-")
            .replace("\u2013", "-")
            .replace("\u2260", "!=")
            .replace("\u2026", "...")
        )

    lines = [
        f"CLUSTER GAPS: {report['cluster']} ({report.get('cluster_id')})",
        f"platform: {report.get('platform_id')}",
        _ascii(report.get("label", "")),
        "",
        "COMPLETENESS (per-axis counts - not one fake %)",
    ]
    c = report["completeness"]
    lines += [
        f"  signals_evaluated:              {c['signals_evaluated']}",
        f"  donor_encoding_documented:      {c['donor_encoding_documented']}",
        f"  donor_encoding_absent:          {c['donor_encoding_absent_public_dbc']}",
        f"  cluster_rx_confirmed:           {c['cluster_rx_confirmed']}",
        f"  cluster_rx_likely/community:    {c['cluster_rx_likely_or_community']}",
        f"  timing_established:             {c['timing_established']}",
        f"  integrity_algorithm_documented: {c['integrity_algorithm_documented']}",
        f"  demonstrated_any:               {c['demonstrated_any']}",
        "",
        f"{'SIGNAL':<36} {'PRI':<10} {'OVERALL':<24} B/E/F/G/H",
        "-" * 100,
    ]
    for row in report["rows"]:
        axes = row["axes"]
        befgh = "/".join(axes[x]["status"][:3] for x in ("B", "E", "F", "G", "H"))
        lines.append(f"{row['signal']:<36} {row['priority']:<10} {row['overall']:<24} {befgh}")
        if row.get("notes"):
            lines.append(f"  notes: {_ascii(row['notes'][:120])}")
        for letter in ("B", "E", "F", "G", "H"):
            ax = axes[letter]
            if ax["status"] in ("UNKNOWN", "ABSENT", "COMMUNITY_RESEARCH", "INFERRED") and ax.get(
                "evidence_to_close"
            ):
                lines.append(f"  [{letter}] {ax['status']}: {_ascii(ax['evidence_to_close'])}")
    lines.append("")
    return "\n".join(lines)
