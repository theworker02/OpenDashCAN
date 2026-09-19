"""Civic 8 source decoder — intentional no-op placeholder.

This decoder does NOT invent decodings. Community-reported IDs may be tracked
for analysis hooks, but ``decode_frame`` does not write fabricated values into
VehicleState.
"""

from __future__ import annotations

from opendashcan.core.decoder import VehicleDecoder
from opendashcan.core.frame import CANFrame
from opendashcan.core.state import VehicleState
from opendashcan.protocols.honda.civic8.signals import documented_signal_confidence

# COMMUNITY_REPORTED watch IDs from Autosport Labs — encodings UNKNOWN.
_WATCH_IDS = frozenset({0x194, 0x494, 0x694})


class Civic8VehicleDecoder(VehicleDecoder):
    vehicle_id = "honda_civic_8th_gen"
    display_name = "Honda Civic 8th Gen (2006–2011)"

    def __init__(self) -> None:
        self.seen_watch_ids: set[int] = set()

    def decode_frame(self, frame: CANFrame, state: VehicleState) -> VehicleState:
        if frame.arbitration_id in _WATCH_IDS:
            self.seen_watch_ids.add(frame.arbitration_id)
        return state

    def supported_signals(self) -> dict[str, str]:
        return documented_signal_confidence()


# Back-compat alias used in some tests / docs
Civic8Decoder = Civic8VehicleDecoder
