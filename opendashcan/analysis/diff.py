"""Frame list diff helpers."""

from __future__ import annotations

from opendashcan.analysis.correlation import diff_ids
from opendashcan.core.frame import CANFrame


def payload_changes(a: list[CANFrame], b: list[CANFrame]) -> list[dict[str, str]]:
    """Compare first occurrence payloads per ID between two captures."""
    first_a = {fr.arbitration_id: fr for fr in a}
    first_b = {fr.arbitration_id: fr for fr in b}
    changes: list[dict[str, str]] = []
    for arb in sorted(set(first_a) & set(first_b)):
        da, db = first_a[arb].data, first_b[arb].data
        if da != db:
            changes.append(
                {
                    "id": hex(arb),
                    "a": da.hex().upper(),
                    "b": db.hex().upper(),
                }
            )
    return changes


__all__ = ["diff_ids", "payload_changes"]
