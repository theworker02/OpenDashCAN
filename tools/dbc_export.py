#!/usr/bin/env python3
"""Export a minimal DBC stub from a message catalog JSON (research aid)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Export minimal DBC from catalog JSON")
    p.add_argument("catalog", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    args = p.parse_args()
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    lines = [
        'VERSION ""',
        "",
        "NS_ :",
        "",
        "BS_:",
        "",
        "BU_: XXX",
        "",
    ]
    for msg in data.get("messages", []):
        lines.append(f"BO_ {msg['id_dec']} {msg['name']}: {msg['dlc']} XXX")
        lines.append("")
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote stub DBC {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
