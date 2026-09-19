"""Vehicle / cluster registry for Milestone 0.1 Honda Civic 8 / 10 placeholders."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from opendashcan.core.decoder import VehicleDecoder
from opendashcan.core.encoder import ClusterEncoder


@dataclass(frozen=True, slots=True)
class VehicleEntry:
    vehicle_id: str
    display_name: str
    role: str  # "source" | "target" | "both"
    kind: str  # "decoder" | "encoder"
    factory: Callable[[], VehicleDecoder | ClusterEncoder]
    notes: str = ""


_REGISTRY: dict[str, VehicleEntry] = {}


def register(entry: VehicleEntry) -> None:
    if entry.vehicle_id in _REGISTRY:
        raise ValueError(f"duplicate vehicle_id: {entry.vehicle_id}")
    _REGISTRY[entry.vehicle_id] = entry


def get(vehicle_id: str) -> VehicleEntry:
    try:
        return _REGISTRY[vehicle_id]
    except KeyError as exc:
        raise KeyError(f"unknown vehicle_id: {vehicle_id}") from exc


def list_vehicles() -> list[VehicleEntry]:
    return sorted(_REGISTRY.values(), key=lambda e: e.vehicle_id)


def create_decoder(vehicle_id: str) -> VehicleDecoder:
    entry = get(vehicle_id)
    obj = entry.factory()
    if not isinstance(obj, VehicleDecoder):
        raise TypeError(f"{vehicle_id} is not a decoder")
    return obj


def create_encoder(vehicle_id: str) -> ClusterEncoder:
    entry = get(vehicle_id)
    obj = entry.factory()
    if not isinstance(obj, ClusterEncoder):
        raise TypeError(f"{vehicle_id} is not an encoder")
    return obj


def _ensure_defaults() -> None:
    """Lazy-register built-in Honda Civic placeholders."""
    if _REGISTRY:
        return
    from opendashcan.protocols.honda.civic8.decoder import Civic8VehicleDecoder
    from opendashcan.protocols.honda.civic10.encoder import Civic10Encoder

    register(
        VehicleEntry(
            vehicle_id="honda-civic8",
            display_name="Honda Civic 8th Gen (2006–2011) — source vehicle",
            role="source",
            kind="decoder",
            factory=Civic8VehicleDecoder,
            notes=(
                "Mostly UNKNOWN decoding. Architecture from service manuals; "
                "speculative Autosport Labs IDs are COMMUNITY_REPORTED only."
            ),
        )
    )
    register(
        VehicleEntry(
            vehicle_id="honda-civic10",
            display_name="Honda Civic 10th Gen (2016–2021) — donor cluster target",
            role="target",
            kind="encoder",
            factory=Civic10Encoder,
            notes=(
                "Emits SYNTHETIC research frames from opendbc vehicle-bus layouts. "
                "Cluster consumption not bench-verified; no compatibility claimed."
            ),
        )
    )


# Populate on import so CLI/tests see vehicles immediately
_ensure_defaults()
