#!/usr/bin/env python3
"""Validate signal evidence YAML against policy + schema.

Rejects VERIFIED entries that lack sources.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "signal_evidence.schema.json"
DEFAULT_GLOBS = [
    "opendashcan/protocols/**/evidence.yaml",
]


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def find_files(path: Path | None) -> list[Path]:
    if path is not None:
        if path.is_file():
            return [path]
        return sorted(path.rglob("evidence.yaml"))
    files: list[Path] = []
    for pattern in DEFAULT_GLOBS:
        files.extend(ROOT.glob(pattern))
    return sorted(set(files))


def validate_file(path: Path, schema: dict) -> list[str]:
    errors: list[str] = []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        errors.append(f"{path}: schema: {err.message}")

    signals = data.get("signals") or []
    if isinstance(signals, dict):
        signals = [{"name": k, **(v if isinstance(v, dict) else {})} for k, v in signals.items()]
    for sig in signals:
        if not isinstance(sig, dict):
            errors.append(f"{path}: signal entry must be a mapping")
            continue
        name = sig.get("name", "<unnamed>")
        conf = sig.get("confidence")
        sources = sig.get("sources") or []
        if conf == "VERIFIED" and not sources:
            errors.append(f"{path}: signal {name!r}: VERIFIED requires sources")
        if conf == "VERIFIED":
            for src in sources:
                if isinstance(src, str):
                    if not src.strip():
                        errors.append(f"{path}: signal {name!r}: VERIFIED source string empty")
                    continue
                if isinstance(src, dict):
                    citation = src.get("citation") or src.get("url") or src.get("title")
                    if not citation:
                        errors.append(
                            f"{path}: signal {name!r}: VERIFIED source missing citation/url"
                        )
                else:
                    errors.append(
                        f"{path}: signal {name!r}: VERIFIED source must be string or mapping"
                    )
    return errors


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    path = Path(argv[0]) if argv else None
    schema = load_schema()
    files = find_files(path)
    if not files:
        print("no evidence.yaml files found", file=sys.stderr)
        return 1
    all_errors: list[str] = []
    for f in files:
        all_errors.extend(validate_file(f, schema))
    if all_errors:
        print("Evidence validation FAILED:")
        for e in all_errors:
            print(f"  - {e}")
        return 1
    print(f"Evidence validation OK ({len(files)} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
