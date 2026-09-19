"""Synthetic vehicle-state scenario generator.

Does NOT claim cluster compatibility. Produces normalized VehicleState
timelines and optional research frames for architecture testing.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from opendashcan.core.frame import BusRole, CANFrame, FrameDirection
from opendashcan.core.state import Confidence, SignalValue, Validity, VehicleState


@dataclass(frozen=True)
class ScenarioStep:
    t: float
    label: str
    rpm: float
    speed_kph: float
    ignition: str = "ON"


SCENARIOS: dict[str, list[ScenarioStep]] = {
    "idle": [
        ScenarioStep(0.0, "key_on", 0.0, 0.0, "ON"),
        ScenarioStep(1.0, "crank", 200.0, 0.0, "START"),
        ScenarioStep(2.0, "idle", 800.0, 0.0, "ON"),
        ScenarioStep(5.0, "idle_stable", 750.0, 0.0, "ON"),
    ],
    "accelerate": [
        ScenarioStep(0.0, "idle", 800.0, 0.0, "ON"),
        ScenarioStep(1.0, "roll", 1200.0, 10.0, "ON"),
        ScenarioStep(2.0, "pull", 2500.0, 40.0, "ON"),
        ScenarioStep(3.0, "cruise_build", 3000.0, 80.0, "ON"),
        ScenarioStep(5.0, "cruise", 2200.0, 100.0, "ON"),
    ],
}


def _sig(value: Any, t: float, unit: str | None = None) -> SignalValue[Any]:
    return SignalValue(
        value=value,
        timestamp=t,
        source="synthetic_simulator",
        confidence=Confidence.INFERRED,
        validity=Validity.VALID,
        unit=unit,
        notes="SYNTHETIC — not from a real vehicle capture",
        evidence_refs=("synthetic_fixture",),
    )


def state_at(step: ScenarioStep) -> VehicleState:
    return VehicleState(
        engine_rpm=_sig(step.rpm, step.t, "rpm"),
        vehicle_speed=_sig(step.speed_kph, step.t, "kph"),
        ignition_state=_sig(step.ignition, step.t),
    )


def iter_scenario(name: str) -> Iterator[tuple[ScenarioStep, VehicleState]]:
    if name not in SCENARIOS:
        raise KeyError(f"unknown scenario {name!r}; choose from {sorted(SCENARIOS)}")
    for step in SCENARIOS[name]:
        yield step, state_at(step)


def synthetic_source_frames(name: str, *, watch_id: int = 0x194) -> list[CANFrame]:
    """Emit labeled SYNTHETIC frames on a watch ID (no real encoding claimed)."""
    frames: list[CANFrame] = []
    for step, _state in iter_scenario(name):
        # Payload is opaque research padding — NOT a Civic8 encoding.
        rpm_i = int(step.rpm) & 0xFFFF
        data = bytes([(rpm_i >> 8) & 0xFF, rpm_i & 0xFF, 0, 0, 0, 0, 0, 0])
        frames.append(
            CANFrame(
                arbitration_id=watch_id,
                data=data,
                timestamp=step.t,
                bus=BusRole.SOURCE,
                direction=FrameDirection.RX,
                meta={
                    "SYNTHETIC": "true",
                    "scenario": name,
                    "step": step.label,
                    "warning": "NOT a verified Civic 8 encoding",
                },
            )
        )
    return frames
