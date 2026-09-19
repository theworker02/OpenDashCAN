#!/usr/bin/env python3
"""Generate docs/generated/*.md and dist/registry.json from the protocol registry."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from opendashcan.adaptation.matrix import write_coverage_docs  # noqa: E402
from opendashcan.registry import get_registry  # noqa: E402
from opendashcan.registry.validate import validate_registry  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    print(f"wrote {path}")


def generate_vehicles_md(reg) -> str:  # type: ignore[no-untyped-def]
    lines = [
        "# Vehicles",
        "",
        "_Auto-generated from protocol YAML._",
        "",
        "| Platform | Manufacturer | Model | Gen | Years | Roles | Validation |",
        "|----------|--------------|-------|-----|-------|-------|------------|",
    ]
    for pkg in reg.list_platforms():
        v = pkg.vehicle
        lines.append(
            f"| `{pkg.platform_id}` | {v.manufacturer} | {v.model} | {v.generation} | "
            f"{v.years_start}-{v.years_end} | {','.join(v.roles)} | {v.physical_validation} |"
        )
    lines.append("")
    return "\n".join(lines)


def generate_buses_md(reg) -> str:  # type: ignore[no-untyped-def]
    lines = [
        "# Buses",
        "",
        "| Platform | Bus ID | OEM name | Bitrate | Confidence |",
        "|----------|--------|----------|---------|------------|",
    ]
    for pkg in reg.list_platforms():
        for b in pkg.buses:
            rate = b.bitrate if b.bitrate is not None else "UNKNOWN"
            name = b.manufacturer_name or "—"
            lines.append(
                f"| `{pkg.platform_id}` | `{b.bus_id}` | {name} | {rate} | {b.confidence.value} |"
            )
    lines.append("")
    return "\n".join(lines)


def generate_modules_md(reg) -> str:  # type: ignore[no-untyped-def]
    lines = [
        "# Modules",
        "",
        "| Platform | Module | Bus | Role | Confidence |",
        "|----------|--------|-----|------|------------|",
    ]
    for pkg in reg.list_platforms():
        for m in pkg.modules:
            lines.append(
                f"| `{pkg.platform_id}` | `{m.module_id}` | {m.bus or 'UNKNOWN'} | "
                f"{m.role or '—'} | {m.confidence.value} |"
            )
    lines.append("")
    return "\n".join(lines)


def generate_messages_md(reg) -> str:  # type: ignore[no-untyped-def]
    lines = [
        "# Messages",
        "",
        "| Platform | ID | Name | Bus | Confidence |",
        "|----------|----|------|-----|------------|",
    ]
    for pkg in reg.list_platforms():
        for m in pkg.messages:
            lines.append(
                f"| `{pkg.platform_id}` | `{m.arbitration_id or 'UNKNOWN'}` | "
                f"{m.name or '—'} | {m.bus or '—'} | {m.confidence.value} |"
            )
    lines.append("")
    return "\n".join(lines)


def generate_signals_md(reg) -> str:  # type: ignore[no-untyped-def]
    lines = [
        "# Signals",
        "",
        "| Platform | Signal | CAN ID | Confidence | Physical |",
        "|----------|--------|--------|------------|----------|",
    ]
    for pkg in reg.list_platforms():
        for s in pkg.signals:
            lines.append(
                f"| `{pkg.platform_id}` | `{s.signal}` | `{s.arbitration_id or 'UNKNOWN'}` | "
                f"{s.confidence.value} | {s.physical_validation} |"
            )
    lines.append("")
    return "\n".join(lines)


def generate_clusters_md(reg) -> str:  # type: ignore[no-untyped-def]
    lines = [
        "# Clusters",
        "",
        "| Cluster | Platform | Display | Compatibility |",
        "|---------|----------|---------|---------------|",
    ]
    for cid, pkg in reg.list_clusters():
        c = pkg.cluster
        assert c is not None
        lines.append(
            f"| `{cid}` | `{pkg.platform_id}` | {c.display_type or '—'} | "
            f"{c.compatibility_status} |"
        )
    lines.append("")
    return "\n".join(lines)


def generate_conflicts_md(reg) -> str:  # type: ignore[no-untyped-def]
    lines = [
        "# Conflicts",
        "",
        "_Conflicts are preserved, never silently resolved._",
        "",
    ]
    any_conflict = False
    for pkg in reg.list_platforms():
        if not pkg.conflicts:
            continue
        any_conflict = True
        lines.append(f"## `{pkg.platform_id}`")
        lines.append("")
        for c in pkg.conflicts:
            lines.append(f"- {c}")
        lines.append("")
    if not any_conflict:
        lines += ["No registered conflicts.", ""]
    return "\n".join(lines)


def main() -> int:
    reg = get_registry(reload=True)
    dist = ROOT / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    registry_path = dist / "registry.json"
    registry_path.write_text(json.dumps(reg.to_dict(), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {registry_path}")

    written = write_coverage_docs(ROOT / "docs" / "generated")
    for _name, path in written.items():
        print(f"wrote {path}")

    gen = ROOT / "docs" / "generated"
    _write(gen / "vehicles.md", generate_vehicles_md(reg))
    _write(gen / "buses.md", generate_buses_md(reg))
    _write(gen / "modules.md", generate_modules_md(reg))
    _write(gen / "messages.md", generate_messages_md(reg))
    _write(gen / "signals.md", generate_signals_md(reg))
    _write(gen / "clusters.md", generate_clusters_md(reg))
    _write(gen / "conflicts.md", generate_conflicts_md(reg))
    # coverage.md alias of honda + adaptations summary
    coverage = (gen / "honda_coverage.md").read_text(encoding="utf-8")
    adaptations = (gen / "adaptations.md").read_text(encoding="utf-8")
    _write(
        gen / "coverage.md",
        "# Coverage\n\n" + coverage + "\n" + adaptations,
    )

    # Platforms index
    platforms_md = gen / "platforms.md"
    lines = [
        "# Registered Honda platforms",
        "",
        "_Auto-generated from protocol YAML. UNKNOWN is valid._",
        "",
        "| Platform | Years | Roles | Buses | Messages | Signals | Cluster |",
        "|----------|-------|-------|-------|----------|---------|---------|",
    ]
    for pkg in reg.list_platforms():
        years = f"{pkg.vehicle.years_start}-{pkg.vehicle.years_end}"
        cluster = pkg.cluster.cluster_id if pkg.cluster else "—"
        lines.append(
            f"| `{pkg.platform_id}` | {years} | {','.join(pkg.vehicle.roles)} | "
            f"{len(pkg.buses)} | {len(pkg.messages)} | {len(pkg.signals)} | `{cluster}` |"
        )
    lines.append("")
    _write(platforms_md, "\n".join(lines))

    report = validate_registry(reg)
    if report.errors:
        print("VALIDATION ERRORS:", file=sys.stderr)
        for e in report.errors:
            print(f"  ERROR: {e}", file=sys.stderr)
        return 1
    for w in report.warnings[:30]:
        print(f"  WARN: {w}")
    print(f"platforms={len(reg.list_platforms())} clusters={len(reg.list_clusters())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
