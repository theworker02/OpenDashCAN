"""Honda integrity pattern grouping — documented examples only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from opendashcan.honda.integrity.checksums import EVIDENCE, NIBBLE_CHECKSUM_PLATFORMS, NIBBLE_V1
from opendashcan.protocols.honda.checksum import honda_compute_checksum, honda_set_checksum

REPO_ROOT = Path(__file__).resolve().parents[3]


def integrity_pattern_groups() -> dict[str, Any]:
    """Group known checksum/counter patterns without inventing universal algorithms."""
    # Documented test: compute checksum for a zeroed buffer on 0x158 — verifies algorithm identity
    sample_addr = 0x158
    sample_data = bytes(8)
    with_counter_ck = honda_set_checksum(sample_addr, bytearray(sample_data))
    nibble = honda_compute_checksum(sample_addr, with_counter_ck)

    return {
        "warning": (
            "No universal invented checksum. Patterns below are vehicle-bus "
            "documentation from opendbc — cluster acceptance UNKNOWN."
        ),
        "groups": [
            {
                "pattern_id": "honda_nibble_v1",
                "platforms": sorted(NIBBLE_CHECKSUM_PLATFORMS),
                "confidence": NIBBLE_V1.confidence,
                "evidence": dict(EVIDENCE),
                "cluster_acceptance": "UNKNOWN",
                "counter_companion": "honda_2bit_v1",
                "test_vector": {
                    "arbitration_id": hex(sample_addr),
                    "input": sample_data.hex(),
                    "output_with_checksum": with_counter_ck.hex(),
                    "checksum_nibble": nibble,
                    "provenance": "opendbc honda_compute_checksum identity check",
                    "cluster_verified": False,
                    "note": "Synthetic algorithm self-check — not a captured cluster frame",
                },
            },
            {
                "pattern_id": "honda_2bit_v1",
                "description": "2-bit rolling counter in high nibble of final byte (opendbc convention)",
                "confidence": "DOCUMENTED",
                "cluster_acceptance": "UNKNOWN",
                "test_vectors": [],
            },
        ],
    }


def write_integrity_patterns(path: Path | None = None) -> Path:
    out = path or (REPO_ROOT / "dist" / "honda_integrity_patterns.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(integrity_pattern_groups(), indent=2) + "\n", encoding="utf-8")
    return out
