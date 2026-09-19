"""Load and parse cluster requirements YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from opendashcan.registry.models import ClusterRequirement

VALID_PRIORITIES = frozenset({"REQUIRED", "OPTIONAL", "COSMETIC", "UNKNOWN"})


def load_requirements(path: Path | dict[str, Any]) -> list[ClusterRequirement]:
    if isinstance(path, dict):
        data = path
    else:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(raw, dict):
            raise ValueError(f"requirements root must be mapping: {path}")
        data = raw
    return [ClusterRequirement.from_dict(r) for r in (data.get("requirements") or [])]


def summarize_priorities(reqs: list[ClusterRequirement]) -> dict[str, int]:
    counts = {p: 0 for p in sorted(VALID_PRIORITIES)}
    for r in reqs:
        key = r.priority if r.priority in VALID_PRIORITIES else "UNKNOWN"
        counts[key] = counts.get(key, 0) + 1
    return counts
