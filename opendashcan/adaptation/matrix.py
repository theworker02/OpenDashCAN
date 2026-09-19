"""Coverage matrix generators for Honda platforms and clusters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from opendashcan.adaptation.planner import plan
from opendashcan.registry import get_registry

# Signals shown in coverage matrices
MATRIX_SIGNALS = (
    "powertrain.engine_rpm",
    "vehicle.speed",
    "fuel.level",
    "powertrain.coolant_temperature",
    "transmission.gear",
    "lighting.left_indicator",
    "brakes.abs_warning",
    "safety.srs_warning",
)

SHORT = {
    "powertrain.engine_rpm": "RPM",
    "vehicle.speed": "SPEED",
    "fuel.level": "FUEL",
    "powertrain.coolant_temperature": "TEMP",
    "transmission.gear": "GEAR",
    "lighting.left_indicator": "TURN",
    "brakes.abs_warning": "ABS",
    "safety.srs_warning": "SRS",
}


def _cell(conf: str) -> str:
    c = conf.upper()
    if c in ("PHYSICALLY_VERIFIED", "VERIFIED", "CAPTURE_VERIFIED"):
        return c
    if c in ("DOCUMENTED", "SUPPORTED_BY_MULTIPLE_SOURCES"):
        return "DOCUMENTED"
    if c == "COMMUNITY_REPORTED":
        return "PARTIAL"
    if c in ("INFERRED", "HYPOTHESIS"):
        return "PARTIAL"
    if c == "UNKNOWN":
        return "UNKNOWN"
    return c


def generate_honda_coverage_md() -> str:
    reg = get_registry()
    lines = [
        "# Honda coverage matrix",
        "",
        "_Auto-generated. Confidence labels only — not hardware claims._",
        "",
        "| Platform | " + " | ".join(SHORT[s] for s in MATRIX_SIGNALS) + " |",
        "|----------|" + "|".join(["------"] * len(MATRIX_SIGNALS)) + "|",
    ]
    for pkg in reg.list_platforms():
        sm = pkg.signal_map()
        cells = []
        for sig in MATRIX_SIGNALS:
            enc = sm.get(sig)
            cells.append(_cell(enc.confidence.value if enc else "UNKNOWN"))
        lines.append(f"| `{pkg.platform_id}` | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def generate_cluster_coverage_md() -> str:
    reg = get_registry()
    lines = [
        "# Cluster coverage matrix",
        "",
        "_What OpenDashCAN documents about each target cluster. "
        "Cluster RX for donor swap is NOT PHYSICALLY_VERIFIED unless stated._",
        "",
        "| Cluster | " + " | ".join(SHORT[s] for s in MATRIX_SIGNALS) + " | Status |",
        "|---------|" + "|".join(["------"] * len(MATRIX_SIGNALS)) + "|--------|",
    ]
    for cid, pkg in reg.list_clusters():
        sm = pkg.signal_map()
        cells = [_cell(sm[s].confidence.value) if s in sm else "UNKNOWN" for s in MATRIX_SIGNALS]
        status = pkg.cluster.compatibility_status if pkg.cluster else "UNKNOWN"
        lines.append(f"| `{cid}` | " + " | ".join(cells) + f" | {status} |")
    lines.append("")
    return "\n".join(lines)


def generate_adaptations_md() -> str:
    reg = get_registry()
    pairs = [
        ("honda.civic.gen8.us.r18.auto", "honda.civic.gen10.cluster.digital"),
        ("honda.civic.gen8.us.r18.auto", "honda.civic.gen11.cluster.digital"),
        ("honda.civic.gen8.us.r18.auto", "honda.accord.gen10.cluster.digital"),
        ("honda.civic.gen8.us.r18.auto", "honda.crv.gen5.cluster.digital"),
    ]
    lines = [
        "# Adaptation readiness",
        "",
        "_Requirement states — not percentages. Mode: DOCUMENTATION_ONLY._",
        "",
    ]
    for src, tgt in pairs:
        try:
            p = plan(src, tgt)
        except KeyError as exc:
            lines += [f"## `{src}` → `{tgt}`", "", f"Unavailable: {exc}", ""]
            continue
        lines += [
            f"## `{src}` → `{p.cluster_id}`",
            "",
            f"Protocol compatibility: **{p.protocol_compatibility}**",
            "",
            "| Signal | Source | Target | Priority | Readiness |",
            "|--------|--------|--------|----------|-----------|",
        ]
        for row in p.rows:
            lines.append(
                f"| `{row.signal}` | {row.source_confidence} | {row.target_confidence} | "
                f"{row.priority} | {row.readiness.value} |"
            )
        lines.append("")
        summary = p.readiness_summary()
        lines.append("Summary: " + ", ".join(f"{k}={v}" for k, v in sorted(summary.items())))
        lines.append("")
    _ = reg  # registry warm
    return "\n".join(lines)


def write_coverage_docs(docs_dir: Path | None = None) -> dict[str, Path]:
    root = Path(__file__).resolve().parents[2]
    out_dir = docs_dir or (root / "docs" / "generated")
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    mapping = {
        "honda_coverage.md": generate_honda_coverage_md(),
        "cluster_coverage.md": generate_cluster_coverage_md(),
        "adaptations.md": generate_adaptations_md(),
    }
    for name, text in mapping.items():
        path = out_dir / name
        path.write_text(text, encoding="utf-8")
        written[name] = path
    return written


def coverage_snapshot() -> dict[str, Any]:
    return {
        "honda_platforms": [p.platform_id for p in get_registry().list_platforms()],
        "clusters": [c for c, _ in get_registry().list_clusters()],
    }
