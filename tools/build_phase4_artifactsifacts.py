#!/usr/bin/env python3
"""Build Phase 4 research/dist artifacts incrementally."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from opendashcan.analysis.conflicts_engine import collect_conflicts, write_conflicts_json
    from opendashcan.analysis.dbc_inventory import build_dbc_inventory
    from opendashcan.analysis.lineage import build_lineage, write_lineage_artifacts
    from opendashcan.analysis.network_graph import write_network_graph
    from opendashcan.analysis.similarity import build_cross_platform_candidates
    from opendashcan.cluster.environment_loader import list_cluster_envs
    from opendashcan.cluster.gaps import build_gap_report
    from opendashcan.cluster.timing import write_timing_database
    from opendashcan.honda.integrity.patterns import write_integrity_patterns

    print("1/8 DBC inventory…")
    inv = build_dbc_inventory()
    print(f"   dbcs={inv['inventory']['dbc_count']} msgs={inv['inventory']['message_count']}")

    print("2/8 Message lineage…")
    lineage = build_lineage()
    paths = write_lineage_artifacts(lineage)
    print(f"   wrote {paths['json']} {paths['md']}")

    print("3/8 Network graph…")
    gpath = write_network_graph()
    print(f"   wrote {gpath}")

    print("4/8 Timing + integrity…")
    print(f"   wrote {write_timing_database()}")
    print(f"   wrote {write_integrity_patterns()}")

    print("5/8 Cross-platform candidates…")
    cands = build_cross_platform_candidates()
    cand_json = ROOT / "dist" / "cross_platform_candidates.json"
    cand_json.write_text(json.dumps(cands, indent=2) + "\n", encoding="utf-8")
    _write_candidates_md(cands, ROOT / "research" / "CROSS_PLATFORM_CANDIDATES.md")
    print(f"   leads={cands['lead_count']}")

    print("6/8 Cluster requirements + gaps…")
    all_reqs: dict = {"clusters": {}, "warning": "Per-cluster isolated requirements"}
    gap_lines = [
        "# Cluster Gap Report",
        "",
        "_Phase 4 — real per-axis counts, not one fake compatibility %._",
        "",
    ]

    for key in list_cluster_envs():
        report = build_gap_report(key)
        all_reqs["clusters"][key] = {
            "cluster_id": report["cluster_id"],
            "platform_id": report["platform_id"],
            "completeness": report["completeness"],
            "requirements": report["rows"],
        }
        c = report["completeness"]
        gap_lines += [
            f"## `{key}`",
            "",
            f"- signals_evaluated: {c['signals_evaluated']}",
            f"- donor_encoding_documented: {c['donor_encoding_documented']} "
            f"(fraction {c['fractions']['donor_encoding_documented']})",
            f"- donor_encoding_absent_public_dbc: {c['donor_encoding_absent_public_dbc']}",
            f"- cluster_rx_confirmed: {c['cluster_rx_confirmed']} "
            f"(fraction {c['fractions']['cluster_rx_confirmed']})",
            f"- cluster_rx_likely/community: {c['cluster_rx_likely_or_community']}",
            f"- timing_established: {c['timing_established']}",
            f"- integrity_algorithm_documented: {c['integrity_algorithm_documented']}",
            f"- demonstrated_any: {c['demonstrated_any']}",
            "",
        ]
    req_path = ROOT / "dist" / "cluster_requirements.json"
    req_path.write_text(json.dumps(all_reqs, indent=2) + "\n", encoding="utf-8")
    (ROOT / "research" / "CLUSTER_GAP_REPORT.md").write_text(
        "\n".join(gap_lines) + "\n", encoding="utf-8"
    )
    print(f"   wrote {req_path}")

    print("7/8 Conflicts…")
    write_conflicts_json()
    conf = collect_conflicts()
    print(f"   registry={conf['counts']['registry']} lineage={conf['counts']['lineage_encoding']}")

    print("8/8 Provenance archive stub…")
    _write_provenance_archive()
    print("done")
    return 0


def _write_candidates_md(cands: dict, path: Path) -> None:
    lines = [
        "# Cross-Platform Candidates",
        "",
        cands["warning"],
        "",
        f"Lead count: **{cands['lead_count']}**",
        "",
        "| Target | Signal | Candidate | ID | Score | Label |",
        "|--------|--------|-----------|----|-------|-------|",
    ]
    for lead in cands["leads"][:80]:
        lines.append(
            f"| `{lead['target_vehicle']}` | `{lead['signal']}` | "
            f"`{lead['candidate_vehicle']}` | `{lead.get('arbitration_id')}` | "
            f"{lead['score']} | {lead['label']} |"
        )
    if len(cands["leads"]) > 80:
        lines.append(f"| … | ({len(cands['leads']) - 80} more) | | | | |")
    lines += [
        "",
        "## Policy",
        "",
        "- Never copy Accord fuel into Civic.",
        "- `CROSS_PLATFORM_CANDIDATE` ≠ platform definition.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_provenance_archive() -> None:
    archive = ROOT / "research" / "provenance" / "PUBLIC_SOURCE_EXPANSION.md"
    archive.parent.mkdir(parents=True, exist_ok=True)
    text = """# Public source expansion (Phase 4)

Record positive **and negative** results for remaining cluster gaps.

## Searched / revisited

| Source | Result | Cluster relevance |
|--------|--------|-------------------|
| commaai/opendbc Honda DBCs (vendored) | Positive — vehicle protocol | PROTOCOL_DOCUMENTED |
| CivicX 2020 Si cluster swap | COMMUNITY_RESEARCH on 0x158/0x17C | NOT CLUSTER_RX_CONFIRMED |
| CivicX “Decoding the CAN BUS” | Points to opendbc | Use DBC labels, not forum |
| Honda-Civic-B-CAN (GitHub) | Body bus tap claims | UNKNOWN for cluster gauges |
| HondaCAN (Accord, GitHub) | Vehicle profiles | UNKNOWN cluster RX |
| Public OEM fuel/coolant CAN PDFs | **Negative** — no public bit layout | Remain ABSENT / UNKNOWN |
| Academic papers on Honda cluster RX | **Negative** — no citable encoding | UNKNOWN |
| Public cluster part ↔ CAN map | **Negative / incomplete** | CIVIC10_CLUSTER_DEEP_DIVE.md |

## Gaps still open

- Fuel / coolant / SRS / MIL / ABS lamp encodings
- Cluster RX confirmation for any ID
- Timing tables at cluster connector
- Startup / ignition sequencing
- Civic8 byte layouts (source)

## Labeling reminder

forum ≠ CAPTURE_VERIFIED; DBC ≠ BENCH_VERIFIED / CLUSTER_RX_CONFIRMED.
"""
    archive.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
