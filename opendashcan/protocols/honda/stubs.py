"""Stub / thin target encoders for multi-cluster adaptations.

Until encodings are DOCUMENTED and gated, encode() returns []
(EncodeMode.NO_OUTPUT). Civic10 remains the only encoder that can emit
SYNTHETIC / RESEARCH_DOCUMENTED frames when explicitly enabled.
"""

from __future__ import annotations

from opendashcan.core.encoder import ClusterEncoder, EncodeMode, OutputKind
from opendashcan.core.frame import CANFrame
from opendashcan.core.state import VehicleState


class StubClusterEncoder(ClusterEncoder):
    """Documentation-only stub — never invents frames."""

    def __init__(
        self,
        cluster_id: str,
        display_name: str,
        *,
        supported: dict[str, str] | None = None,
        encode_mode: EncodeMode = EncodeMode.NO_OUTPUT,
    ) -> None:
        self.cluster_id = cluster_id
        self.display_name = display_name
        self.encode_mode = encode_mode
        self._supported = supported or {}
        self._last_kind = OutputKind.NO_OUTPUT

    def encode(self, state: VehicleState, timestamp: float | None = None) -> list[CANFrame]:
        self._last_kind = OutputKind.NO_OUTPUT
        return []

    def supported_signals(self) -> dict[str, str]:
        return dict(self._supported)

    def last_output_kind(self) -> OutputKind:
        return self._last_kind


def civic11_encoder() -> StubClusterEncoder:
    return StubClusterEncoder(
        "honda.civic.gen11.cluster.digital",
        "Honda Civic 11th Gen digital cluster — stub (NO_OUTPUT)",
        supported={
            "powertrain.engine_rpm": "DOCUMENTED",
            "vehicle.speed": "DOCUMENTED",
        },
    )


def accord10_encoder() -> StubClusterEncoder:
    return StubClusterEncoder(
        "honda.accord.gen10.cluster.digital",
        "Honda Accord 10th Gen digital cluster — stub (NO_OUTPUT)",
        supported={
            "powertrain.engine_rpm": "DOCUMENTED",
            "vehicle.speed": "DOCUMENTED",
        },
    )


def crv5_encoder() -> StubClusterEncoder:
    return StubClusterEncoder(
        "honda.crv.gen5.cluster.digital",
        "Honda CR-V 5th Gen digital cluster — stub (NO_OUTPUT)",
        supported={
            "powertrain.engine_rpm": "DOCUMENTED",
            "vehicle.speed": "DOCUMENTED",
        },
    )
