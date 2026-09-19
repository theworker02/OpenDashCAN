"""Adaptation readiness classifications (not percentages)."""

from __future__ import annotations

from enum import Enum


class Readiness(str, Enum):
    READY_FROM_DOCUMENTATION = "READY_FROM_DOCUMENTATION"
    PARTIAL = "PARTIAL"
    # Source encodings unknown / weak while target donor encoding is documented:
    # translation is blocked on the source side only (does not erase target docs).
    BLOCKED_SOURCE = "BLOCKED_SOURCE"
    REQUIRES_CAN_CAPTURE = "REQUIRES_CAN_CAPTURE"
    REQUIRES_BENCH_TEST = "REQUIRES_BENCH_TEST"
    REQUIRES_VEHICLE_TEST = "REQUIRES_VEHICLE_TEST"


DOCUMENTED_LIKE = frozenset(
    {
        "DOCUMENTED",
        "SUPPORTED_BY_MULTIPLE_SOURCES",
        "CAPTURE_VERIFIED",
        "PHYSICALLY_VERIFIED",
        "VERIFIED",
    }
)


def classify_signal_readiness(
    *,
    source_confidence: str,
    target_confidence: str,
    priority: str,
) -> Readiness:
    """Classify one signal adaptation readiness from source/target confidence."""
    src = (source_confidence or "UNKNOWN").upper()
    tgt = (target_confidence or "UNKNOWN").upper()
    pri = (priority or "UNKNOWN").upper()

    if pri == "UNKNOWN" and src == "UNKNOWN" and tgt == "UNKNOWN":
        return Readiness.REQUIRES_CAN_CAPTURE

    if src == "UNKNOWN" or src in ("HYPOTHESIS", "INFERRED"):
        if tgt in DOCUMENTED_LIKE:
            # Target donor encoding is documented; source gap must not erase that.
            # Translation is blocked on the source side only (BLOCKED_SOURCE).
            return Readiness.BLOCKED_SOURCE
        return Readiness.REQUIRES_CAN_CAPTURE

    if tgt == "UNKNOWN":
        if pri in ("REQUIRED", "OPTIONAL"):
            return Readiness.REQUIRES_BENCH_TEST
        return Readiness.REQUIRES_CAN_CAPTURE

    if src in DOCUMENTED_LIKE and tgt in DOCUMENTED_LIKE:
        return Readiness.READY_FROM_DOCUMENTATION

    if src == "COMMUNITY_REPORTED" or tgt == "COMMUNITY_REPORTED" or tgt == "PARTIAL":
        return Readiness.PARTIAL

    if "PARTIAL" in (src, tgt) or src == "INFERRED" or tgt == "INFERRED":
        return Readiness.PARTIAL

    return Readiness.PARTIAL
