"""Validation helpers for frames, state, and evidence policy hooks."""

from __future__ import annotations

from typing import Any

from opendashcan.core.frame import CANFrame
from opendashcan.core.state import Confidence, SignalValue, VehicleState


def validate_frame(frame: CANFrame) -> list[str]:
    """Return human-readable validation errors for a CANFrame (empty if ok)."""
    errors: list[str] = []
    if frame.dlc is not None and frame.dlc < len(frame.data):
        errors.append("DLC smaller than payload length")
    if frame.is_fd and frame.bitrate_switch and not frame.is_fd:
        errors.append("bitrate_switch requires CAN FD")
    max_len = 64 if frame.is_fd else 8
    if len(frame.data) > max_len:
        errors.append(f"payload length exceeds {max_len}")
    return errors


def validate_signal_value(name: str, sig: SignalValue[Any]) -> list[str]:
    errors: list[str] = []
    if sig.confidence == Confidence.VERIFIED and not sig.evidence_refs and sig.value is not None:
        errors.append(f"{name}: VERIFIED value should cite evidence_refs")
    if sig.value is not None and sig.confidence == Confidence.UNKNOWN:
        errors.append(
            f"{name}: non-None value with Confidence.UNKNOWN — mark INFERRED or leave value None"
        )
    return errors


def validate_state(state: VehicleState) -> list[str]:
    """Validate a VehicleState instance for evidence-policy consistency."""
    errors: list[str] = []
    for name in VehicleState.__dataclass_fields__:
        sig: SignalValue[Any] = getattr(state, name)
        errors.extend(validate_signal_value(name, sig))
    return errors


def validate_state_dict(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = set(VehicleState.__dataclass_fields__)
    for key in data:
        if key not in required:
            errors.append(f"unknown state field: {key}")
    return errors


def confidence_allows_live_tx(confidence: Confidence) -> bool:
    """Phase 1 never enables live TX regardless of confidence."""
    _ = confidence
    return False
