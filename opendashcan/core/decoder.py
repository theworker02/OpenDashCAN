"""Abstract vehicle decoder interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from opendashcan.core.frame import CANFrame
from opendashcan.core.state import VehicleState


class VehicleDecoder(ABC):
    """Decode source-vehicle CAN frames into normalized VehicleState.

    Implementations must not invent signal values. If evidence is insufficient,
    leave SignalValue.value as None with Confidence.UNKNOWN.
    """

    vehicle_id: str
    display_name: str

    @abstractmethod
    def decode_frame(self, frame: CANFrame, state: VehicleState) -> VehicleState:
        """Apply one frame to state and return the updated state."""

    def decode_frames(
        self, frames: Iterable[CANFrame], state: VehicleState | None = None
    ) -> VehicleState:
        current = state if state is not None else VehicleState()
        for frame in frames:
            current = self.decode_frame(frame, current)
        return current

    @abstractmethod
    def supported_signals(self) -> dict[str, str]:
        """Map signal name -> confidence label for documented capabilities."""
