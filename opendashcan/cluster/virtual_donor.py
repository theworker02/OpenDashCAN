"""Virtual donor vehicle — software-only ECU frame emission via ClusterEnvironment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendashcan.adaptation.environment import ClusterEnvironment
from opendashcan.adaptation.gating import EncodeMode
from opendashcan.cluster.environment_loader import load_cluster_env
from opendashcan.core.frame import CANFrame
from opendashcan.core.state import VehicleState
from opendashcan.registry import get_encoder, get_registry


@dataclass
class VirtualDonorVehicle:
    """Emit documented donor frames from VehicleState — no hardware TX.

    Production EncodeMode remains NO_OUTPUT unless explicitly overridden for
    SYNTHETIC / RESEARCH_DOCUMENTED software validation.
    """

    cluster_key: str
    encode_mode: EncodeMode = EncodeMode.NO_OUTPUT
    environment: ClusterEnvironment | None = None
    omissions: list[str] = field(default_factory=list)
    counter: int = 0

    def __post_init__(self) -> None:
        env_pkg = load_cluster_env(self.cluster_key)
        reg = get_registry()
        platform_id = env_pkg.platform_id
        if platform_id:
            try:
                pkg = reg.get(platform_id)
                self.environment = ClusterEnvironment.from_package(pkg)
            except KeyError:
                self.environment = None
        self._encoder = None
        # Map cluster key → encoder vehicle id
        encoder_map = {
            "civic10": "honda.civic.gen10.cluster.digital",
            "civic11": "honda.civic.gen11.cluster.digital",
            "accord10": "honda.accord.gen10.cluster.digital",
            "crv5": "honda.crv.gen5.cluster.digital",
        }
        eid = encoder_map.get(env_pkg.key)
        if eid:
            try:
                self._encoder = get_encoder(eid)
                # Apply mode if encoder supports it
                if hasattr(self._encoder, "encode_mode"):
                    self._encoder.encode_mode = self.encode_mode
            except KeyError:
                self.omissions.append(f"no encoder for {eid}")

    def observe(self, state: VehicleState) -> None:
        if self.environment:
            self.environment.observe_state(state)

    def emit(self, state: VehicleState, *, timestamp: float = 0.0) -> list[CANFrame]:
        self.observe(state)
        if self.encode_mode == EncodeMode.NO_OUTPUT:
            self.omissions.append("EncodeMode.NO_OUTPUT — no frames emitted (production default)")
            return []
        if self._encoder is None:
            self.omissions.append("encoder unavailable")
            return []
        if hasattr(self._encoder, "encode_mode"):
            self._encoder.encode_mode = self.encode_mode
        frames = self._encoder.encode(state, timestamp=timestamp)
        self.counter += 1
        return list(frames)

    def summary(self) -> dict[str, Any]:
        return {
            "cluster_key": self.cluster_key,
            "encode_mode": self.encode_mode.value
            if hasattr(self.encode_mode, "value")
            else str(self.encode_mode),
            "environment": self.environment.gap_report() if self.environment else None,
            "omissions": list(self.omissions),
            "label": "SOFTWARE VALIDATION ONLY — virtual donor, no hardware",
        }
