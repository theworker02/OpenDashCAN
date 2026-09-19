#!/usr/bin/env python3
"""Batch-import vendored commaai/opendbc Honda/Acura DBCs into structured indexes.

Writes under dbc/opendbc/index/ with full signal provenance.
Does NOT auto-merge into protocol YAML (optional --apply-platforms for Fit/Insight/Odyssey stubs).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from opendashcan.dbc import (  # noqa: E402
    import_dbc,
    taxonomy_implementations_from_imports,
    write_import_artifacts,
)

GENERATED = ROOT / "dbc" / "opendbc" / "generated"
INDEX = ROOT / "dbc" / "opendbc" / "index"

# DBC stem → OpenDashCAN vehicle / platform id + optional compare platform + bus
IMPORT_MAP: list[dict[str, str]] = [
    {
        "file": "honda_civic_touring_2016_can_generated.dbc",
        "vehicle": "honda.civic.gen10.us.touring_2016",
        "platform": "honda.civic.gen10.us",
        "bus": "vehicle_can",
    },
    {
        "file": "honda_civic_hatchback_ex_2017_can_generated.dbc",
        "vehicle": "honda.civic.gen10.us.hatch_ex_2017",
        "platform": "honda.civic.gen10.us",
        "bus": "vehicle_can",
    },
    {
        "file": "honda_civic_ex_2022_can_generated.dbc",
        "vehicle": "honda.civic.gen11.us.ex_2022",
        "platform": "honda.civic.gen11.us",
        "bus": "vehicle_can",
    },
    {
        "file": "honda_accord_2018_can_generated.dbc",
        "vehicle": "honda.accord.gen10.us.2018",
        "platform": "honda.accord.gen10.us",
        "bus": "vehicle_can",
    },
    {
        "file": "honda_crv_ex_2017_can_generated.dbc",
        "vehicle": "honda.crv.gen5.us.ex_2017",
        "platform": "honda.crv.gen5.us",
        "bus": "vehicle_can",
    },
    {
        "file": "honda_crv_ex_2017_body_generated.dbc",
        "vehicle": "honda.crv.gen5.us.ex_2017_body",
        "platform": "honda.crv.gen5.us",
        "bus": "body_can",
    },
    {
        "file": "honda_crv_touring_2016_can_generated.dbc",
        "vehicle": "honda.crv.gen5.us.touring_2016",
        "platform": "honda.crv.gen5.us",
        "bus": "vehicle_can",
    },
    {
        "file": "honda_fit_ex_2018_can_generated.dbc",
        "vehicle": "honda.fit.gen3.us.ex_2018",
        "platform": "honda.fit.gen3.us",
        "bus": "vehicle_can",
    },
    {
        "file": "honda_fit_hybrid_2018_can_generated.dbc",
        "vehicle": "honda.fit.gen3.us.hybrid_2018",
        "platform": "honda.fit.gen3.us",
        "bus": "vehicle_can",
    },
    {
        "file": "honda_insight_ex_2019_can_generated.dbc",
        "vehicle": "honda.insight.gen3.us.ex_2019",
        "platform": "honda.insight.gen3.us",
        "bus": "vehicle_can",
    },
    {
        "file": "honda_odyssey_exl_2018_generated.dbc",
        "vehicle": "honda.odyssey.gen5.us.exl_2018",
        "platform": "honda.odyssey.gen5.us",
        "bus": "vehicle_can",
    },
    {
        "file": "honda_clarity_hybrid_2018_can_generated.dbc",
        "vehicle": "honda.clarity.gen1.us.hybrid_2018",
        "bus": "vehicle_can",
    },
    {
        "file": "acura_ilx_2016_can_generated.dbc",
        "vehicle": "acura.ilx.gen1.us.2016",
        "bus": "vehicle_can",
    },
    {
        "file": "acura_rdx_2018_can_generated.dbc",
        "vehicle": "acura.rdx.gen2.us.2018",
        "bus": "vehicle_can",
    },
    {
        "file": "acura_rdx_2020_can_generated.dbc",
        "vehicle": "acura.rdx.gen3.us.2020",
        "bus": "vehicle_can",
    },
    {
        "file": "honda_crv_executive_2016_can_generated.dbc",
        "vehicle": "honda.crv.gen5.eu.executive_2016",
        "platform": "honda.crv.gen5.us",
        "bus": "vehicle_can",
    },
]


def main() -> int:
    if not GENERATED.is_dir():
        print(f"missing {GENERATED}", file=sys.stderr)
        return 1

    INDEX.mkdir(parents=True, exist_ok=True)
    catalog: list[dict] = []
    for entry in IMPORT_MAP:
        path = GENERATED / entry["file"]
        if not path.is_file():
            print(f"SKIP missing {entry['file']}")
            continue
        compare = entry.get("platform")
        # Only compare if platform exists in registry
        if compare:
            try:
                from opendashcan.registry import get_registry

                get_registry().get(compare)
            except KeyError:
                compare = None
        result = import_dbc(
            path,
            compare_platform=compare,
            vehicle=entry["vehicle"],
            source="opendbc",
            bus=entry.get("bus", "vehicle_can"),
        )
        arts = write_import_artifacts(result, INDEX)
        catalog.append(
            {
                "file": entry["file"],
                "vehicle_id": entry["vehicle"],
                "bus": entry.get("bus", "vehicle_can"),
                "messages": len(result.messages),
                "signals": sum(len(m.signals) for m in result.messages),
                "taxonomy_mapped": len(result.taxonomy_mapped),
                "absent": result.absent_signals,
                "json": str(arts["json"].relative_to(ROOT)).replace("\\", "/"),
                "yaml": str(arts["yaml"].relative_to(ROOT)).replace("\\", "/"),
            }
        )
        print(
            f"imported {entry['file']}: {len(result.messages)} msgs, "
            f"{sum(len(m.signals) for m in result.messages)} signals -> {arts['json'].name}"
        )

    cross = taxonomy_implementations_from_imports(INDEX)
    cross_path = INDEX / "cross_vehicle_signal_index.json"
    cross_path.write_text(json.dumps(cross, indent=2) + "\n", encoding="utf-8")
    catalog_path = INDEX / "catalog.json"
    catalog_path.write_text(
        json.dumps(
            {
                "warning": "Vehicle-protocol documentation only; not cluster RX confirmed.",
                "imports": catalog,
                "cross_vehicle_index": str(cross_path.relative_to(ROOT)).replace("\\", "/"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {catalog_path}")
    print(f"wrote {cross_path} ({len(cross)} taxonomy signals)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
