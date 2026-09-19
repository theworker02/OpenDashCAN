"""Cluster-candidate classification — never invent CLUSTER_CONFIRMED_RX."""

from __future__ import annotations

from enum import Enum
from typing import Any

from opendashcan.core.donor_knowledge import CLUSTER_RELEVANT_TAXONOMY


class ClusterCandidateClass(str, Enum):
    """How a vehicle-bus message relates to a donor cluster.

    CLUSTER_CONFIRMED_RX requires capture/bench evidence — never auto-promoted
    from DBC or forum posts alone.
    """

    CLUSTER_CONFIRMED_RX = "CLUSTER_CONFIRMED_RX"
    CLUSTER_LIKELY_RX = "CLUSTER_LIKELY_RX"
    DISPLAY_RELEVANT = "DISPLAY_RELEVANT"
    POWERTRAIN_ONLY = "POWERTRAIN_ONLY"
    ADAS_ONLY = "ADAS_ONLY"
    BODY_RELEVANT = "BODY_RELEVANT"
    DIAGNOSTIC = "DIAGNOSTIC"
    UNKNOWN = "UNKNOWN"


# CivicX COMMUNITY_RESEARCH + opendbc vehicle protocol — LIKELY, not CONFIRMED.
CIVIC10_LIKELY_RX_IDS: frozenset[int] = frozenset({0x158, 0x17C})

# Names that are clearly ADAS / openpilot command traffic in opendbc Honda DBCs.
ADAS_NAME_HINTS: frozenset[str] = frozenset(
    {
        "ACC_CONTROL",
        "ACC_HUD",
        "ACC_COMMAND",
        "LKAS_HUD",
        "STEERING_CONTROL",
        "GAS_COMMAND",
        "BRAKE_COMMAND",
        "CAM_LANE",
        "RADAR",
        "CAMERA",
    }
)

POWERTRAIN_NAME_HINTS: frozenset[str] = frozenset(
    {
        "ENGINE",
        "POWERTRAIN",
        "GAS_PEDAL",
        "THROTTLE",
        "CRUISE",
        "GEARBOX",
        "CVT",
        "CAR_SPEED",
        "WHEEL_SPEED",
        "EPB",
        "VSA",
        "STANDSTILL",
    }
)

BODY_NAME_HINTS: frozenset[str] = frozenset(
    {
        "DOOR",
        "SEATBELT",
        "STALK",
        "SCM",
        "LIGHT",
        "WIPER",
        "TRUNK",
        "BODY",
        "BSM",
    }
)

DIAG_NAME_HINTS: frozenset[str] = frozenset(
    {
        "DIAG",
        "UDS",
        "TESTER",
        "OBD",
    }
)


def _name_matches(name: str, hints: frozenset[str]) -> bool:
    upper = name.upper()
    return any(h in upper for h in hints)


def classify_message(
    *,
    arbitration_id: int | None,
    name: str | None,
    signal_taxonomies: list[str] | None = None,
    confirmed_rx_ids: frozenset[int] | None = None,
    likely_rx_ids: frozenset[int] | None = None,
    platform_hint: str | None = None,
) -> ClusterCandidateClass:
    """Classify one message. Never promotes LIKELY → CONFIRMED without evidence set."""
    confirmed = confirmed_rx_ids or frozenset()
    likely = likely_rx_ids or frozenset()
    if platform_hint and "civic.gen10" in platform_hint and not likely:
        likely = CIVIC10_LIKELY_RX_IDS

    aid = arbitration_id
    if aid is not None and aid in confirmed:
        return ClusterCandidateClass.CLUSTER_CONFIRMED_RX
    if aid is not None and aid in likely:
        return ClusterCandidateClass.CLUSTER_LIKELY_RX

    taxes = signal_taxonomies or []
    if any(t in CLUSTER_RELEVANT_TAXONOMY for t in taxes):
        return ClusterCandidateClass.DISPLAY_RELEVANT

    n = name or ""
    if _name_matches(n, DIAG_NAME_HINTS):
        return ClusterCandidateClass.DIAGNOSTIC
    if _name_matches(n, ADAS_NAME_HINTS):
        return ClusterCandidateClass.ADAS_ONLY
    if _name_matches(n, BODY_NAME_HINTS):
        return ClusterCandidateClass.BODY_RELEVANT
    if _name_matches(n, POWERTRAIN_NAME_HINTS):
        return ClusterCandidateClass.POWERTRAIN_ONLY
    return ClusterCandidateClass.UNKNOWN


def classify_from_dbc_message(msg: dict[str, Any], *, platform_hint: str | None = None) -> str:
    taxes = [
        s.get("taxonomy")
        for s in (msg.get("signals") or [])
        if s.get("taxonomy")
    ]
    aid = msg.get("id_dec")
    if aid is None and msg.get("id_hex"):
        try:
            aid = int(str(msg["id_hex"]), 16)
        except ValueError:
            aid = None
    return classify_message(
        arbitration_id=aid,
        name=msg.get("name"),
        signal_taxonomies=[t for t in taxes if t],
        platform_hint=platform_hint,
    ).value
