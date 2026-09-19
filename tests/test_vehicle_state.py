"""VehicleState / SignalValue unit tests."""

from __future__ import annotations

from opendashcan.core.state import (
    Confidence,
    DoorStates,
    SignalValue,
    Validity,
    VehicleState,
)


def test_default_state_is_unknown() -> None:
    state = VehicleState()
    assert state.engine_rpm.value is None
    assert state.engine_rpm.confidence == Confidence.UNKNOWN
    assert state.known_signals() == []


def test_signal_with_update() -> None:
    sig: SignalValue[float] = SignalValue(value=None, confidence=Confidence.UNKNOWN)
    updated = sig.with_update(
        900.0,
        timestamp=1.0,
        source="SYNTHETIC",
        confidence=Confidence.INFERRED,
        validity=Validity.VALID,
        unit="rpm",
        notes="SYNTHETIC only",
    )
    assert updated.value == 900.0
    assert updated.confidence == Confidence.INFERRED
    assert sig.value is None


def test_door_states_none_means_unknown() -> None:
    doors = DoorStates()
    assert doors.driver is None
    assert doors.passenger is None


def test_as_dict_serializes_confidence() -> None:
    state = VehicleState()
    state.engine_rpm = SignalValue(
        value=1000.0,
        confidence=Confidence.INFERRED,
        validity=Validity.VALID,
        source="SYNTHETIC",
        unit="rpm",
    )
    d = state.as_dict()
    assert d["engine_rpm"]["value"] == 1000.0
    assert d["engine_rpm"]["confidence"] == "INFERRED"
    assert "coolant_temperature" in d
