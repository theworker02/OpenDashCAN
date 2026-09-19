"""Hardware package — interfaces only in Phase 1."""

from opendashcan.hardware.interfaces import (
    BusConfig,
    CanInterface,
    DualBusAdapter,
    DualBusConfig,
    LinkMode,
    NullDualBusAdapter,
)

__all__ = [
    "BusConfig",
    "CanInterface",
    "DualBusAdapter",
    "DualBusConfig",
    "LinkMode",
    "NullDualBusAdapter",
]
