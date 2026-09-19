"""Vehicle-agnostic translator: Source CAN → Decoder → State → Encoder → Target CAN."""

from __future__ import annotations

from dataclasses import dataclass, field

from opendashcan.core.decoder import VehicleDecoder
from opendashcan.core.encoder import ClusterEncoder
from opendashcan.core.frame import CANFrame
from opendashcan.core.startup import ClusterStartupSequencer, StartupPhase
from opendashcan.core.state import VehicleState


@dataclass
class TranslationResult:
    state: VehicleState
    output_frames: list[CANFrame] = field(default_factory=list)
    startup_phase: StartupPhase = StartupPhase.OFF


class Translator:
    """Connect a decoder and encoder without knowing vehicle-specific CAN IDs."""

    def __init__(
        self,
        decoder: VehicleDecoder,
        encoder: ClusterEncoder,
        *,
        sequencer: ClusterStartupSequencer | None = None,
        emit_while_inactive: bool = False,
    ) -> None:
        self.decoder = decoder
        self.encoder = encoder
        self.sequencer = sequencer or ClusterStartupSequencer()
        self.emit_while_inactive = emit_while_inactive
        self.state = VehicleState()

    def process_frame(self, frame: CANFrame) -> TranslationResult:
        self.state = self.decoder.decode_frame(frame, self.state)
        phase = self.sequencer.observe_state(self.state)
        output: list[CANFrame] = []
        if (
            phase == StartupPhase.ACTIVE or self.emit_while_inactive
        ) and phase != StartupPhase.FAULT:
            output = self.encoder.encode(self.state, timestamp=frame.timestamp)
        return TranslationResult(state=self.state, output_frames=output, startup_phase=phase)

    def process_frames(self, frames: list[CANFrame]) -> TranslationResult:
        last = TranslationResult(state=self.state)
        for frame in frames:
            last = self.process_frame(frame)
        return last

    def decode_only(self, frames: list[CANFrame]) -> VehicleState:
        """Run decoder path only (no encode)."""
        return self.decoder.decode_frames(frames, self.state)

    def encode_only(self, state: VehicleState, timestamp: float | None = None) -> list[CANFrame]:
        """Run encoder path only (offline / research)."""
        return self.encoder.encode(state, timestamp=timestamp)
