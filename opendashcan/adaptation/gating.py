"""Confidence gating for encoder emission.

Production mode blocks UNKNOWN / HYPOTHESIS / INFERRED emission.
Research mode may emit documented/research frames when tagged.
Synthetic only when explicitly SYNTHETIC.

``EncodeMode`` and ``gate_encode`` live in ``opendashcan.core.encoder``
(re-exported here) to avoid circular imports with ``core``.
"""

from __future__ import annotations

from enum import Enum

from opendashcan.core.confidence import Confidence
from opendashcan.core.encoder import EncodeMode, gate_encode
from opendashcan.core.state import SignalValue, VehicleState

__all__ = [
    "BLOCKED_FOR_PRODUCTION",
    "EmissionDecision",
    "EncodeMode",
    "RESEARCH_ALLOWED",
    "gate_encode",
    "signal_emittable",
    "state_has_emittable",
]

BLOCKED_FOR_PRODUCTION = frozenset(
    {
        Confidence.UNKNOWN,
        Confidence.HYPOTHESIS,
        Confidence.INFERRED,
    }
)

RESEARCH_ALLOWED = frozenset(
    {
        Confidence.DOCUMENTED,
        Confidence.SUPPORTED_BY_MULTIPLE_SOURCES,
        Confidence.COMMUNITY_REPORTED,
        Confidence.CAPTURE_VERIFIED,
        Confidence.PHYSICALLY_VERIFIED,
        Confidence.VERIFIED,
    }
)


class EmissionDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK_NO_OUTPUT = "BLOCK_NO_OUTPUT"
    BLOCK_LOW_CONFIDENCE = "BLOCK_LOW_CONFIDENCE"
    BLOCK_UNKNOWN_VALUE = "BLOCK_UNKNOWN_VALUE"


def signal_emittable(sig: SignalValue[object], mode: EncodeMode) -> EmissionDecision:
    conf_name = sig.confidence.value if hasattr(sig.confidence, "value") else str(sig.confidence)

    if mode == EncodeMode.NO_OUTPUT:
        return EmissionDecision.BLOCK_NO_OUTPUT
    if sig.value is None:
        return EmissionDecision.BLOCK_UNKNOWN_VALUE
    if mode == EncodeMode.PRODUCTION:
        if conf_name in ("UNKNOWN", "HYPOTHESIS", "INFERRED"):
            return EmissionDecision.BLOCK_LOW_CONFIDENCE
        return EmissionDecision.ALLOW
    if mode == EncodeMode.RESEARCH_DOCUMENTED:
        if conf_name in ("UNKNOWN", "HYPOTHESIS"):
            return EmissionDecision.BLOCK_LOW_CONFIDENCE
        return EmissionDecision.ALLOW
    if mode == EncodeMode.SYNTHETIC:
        return EmissionDecision.ALLOW
    return EmissionDecision.BLOCK_NO_OUTPUT


def state_has_emittable(
    state: VehicleState,
    signals: tuple[str, ...],
    mode: EncodeMode,
) -> bool:
    for name in signals:
        if hasattr(state, name) and not name.startswith("_"):
            sig = getattr(state, name)
        else:
            sig = state.get(name)
        if isinstance(sig, SignalValue) and signal_emittable(sig, mode) == EmissionDecision.ALLOW:
            return True
    return False
