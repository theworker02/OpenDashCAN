"""Cluster startup sequencer skeleton (OFF → POWERED → INITIALIZING → ACTIVE / FAULT)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from opendashcan.core.state import Confidence, Validity, VehicleState


class StartupPhase(str, Enum):
    OFF = "OFF"
    POWERED = "POWERED"
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    FAULT = "FAULT"


@dataclass
class ClusterStartupSequencer:
    """Conservative software-only cluster lifecycle skeleton.

    Real cluster bring-up sequences are vehicle-specific and largely UNKNOWN
    without bench captures. This machine only models coarse phases so future
    hardware backends can plug in timed init frame schedules.
    """

    phase: StartupPhase = StartupPhase.OFF
    require_ignition: bool = True
    min_known_signals: int = 1
    history: list[StartupPhase] = field(default_factory=list)

    def reset(self) -> None:
        self.phase = StartupPhase.OFF
        self.history.clear()

    def _transition(self, new_phase: StartupPhase) -> StartupPhase:
        if new_phase != self.phase:
            self.history.append(self.phase)
            self.phase = new_phase
        return self.phase

    def observe_state(self, state: VehicleState) -> StartupPhase:
        ignition = state.ignition_state
        ignition_on = False
        if ignition.value is not None:
            ignition_on = str(ignition.value).upper() in {"ON", "RUN", "START", "ACC"}

        if self.phase == StartupPhase.FAULT:
            return self.phase

        if self.require_ignition and not ignition_on and self.phase != StartupPhase.OFF:
            return self._transition(StartupPhase.POWERED)

        if self.phase == StartupPhase.OFF:
            if ignition_on or not self.require_ignition:
                return self._transition(StartupPhase.POWERED)
            return self.phase

        if self.phase == StartupPhase.POWERED:
            return self._transition(StartupPhase.INITIALIZING)

        if self.phase == StartupPhase.INITIALIZING:
            known = [
                name
                for name in state.known_signals()
                if getattr(state, name).validity in {Validity.VALID, Validity.UNKNOWN}
                and getattr(state, name).confidence != Confidence.UNKNOWN
            ]
            if len(known) >= self.min_known_signals:
                return self._transition(StartupPhase.ACTIVE)
            return self.phase

        return self.phase

    def fault(self, reason: str | None = None) -> StartupPhase:
        _ = reason
        return self._transition(StartupPhase.FAULT)
