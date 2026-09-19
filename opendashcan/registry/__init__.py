"""Protocol registry package — Phase-1 vehicle API + Phase-2 YAML loader."""

from __future__ import annotations

from opendashcan.registry.ids import (
    LEGACY_ALIASES,
    adapter_id,
    normalize_cluster_id,
    normalize_platform_id,
    normalize_variant_id,
)
from opendashcan.registry.loader import (
    CLUSTER_ALIASES,
    ProtocolRegistry,
    discover_package_dirs,
    get_registry,
    iter_signal_implementations,
    load_platform,
)
from opendashcan.registry.vehicles import VEHICLES, VehicleInfo, get_decoder, get_encoder

__all__ = [
    "VEHICLES",
    "VehicleInfo",
    "get_decoder",
    "get_encoder",
    "ProtocolRegistry",
    "get_registry",
    "discover_package_dirs",
    "load_platform",
    "normalize_platform_id",
    "normalize_cluster_id",
    "normalize_variant_id",
    "adapter_id",
    "LEGACY_ALIASES",
    "CLUSTER_ALIASES",
    "iter_signal_implementations",
]
