#!/usr/bin/env python3
"""CLI wrapper — prefer `opendashcan dbc import`."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from opendashcan.dbc import import_dbc, write_conflict_report, write_import_artifacts


def main() -> int:
    p = argparse.ArgumentParser(description="Import DBC with full signal provenance (no auto-merge)")
    p.add_argument("dbc", type=Path)
    p.add_argument("-o", "--output", type=Path, help="Single JSON output")
    p.add_argument("--output-dir", type=Path, help="Write JSON+YAML index pair")
    p.add_argument("--platform", help="Compare against registry platform")
    p.add_argument("--vehicle", help="Vehicle label for provenance")
    p.add_argument("--source", default="opendbc")
    p.add_argument("--bus", default="vehicle_can")
    args = p.parse_args()
    result = import_dbc(
        args.dbc,
        compare_platform=args.platform,
        vehicle=args.vehicle,
        source=args.source,
        bus=args.bus,
    )
    if args.output_dir:
        arts = write_import_artifacts(result, args.output_dir)
        print(f"wrote {len(result.messages)} messages to {arts['json']}")
    else:
        out = args.output or Path("dist") / "dbc_import.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8")
        print(f"wrote {len(result.messages)} messages to {out}")
    if result.conflicts:
        report = Path("DBC_CONFLICT_REPORT.md")
        write_conflict_report(result, report)
        print(f"wrote {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
