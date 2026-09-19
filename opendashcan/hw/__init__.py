"""Optional hardware interfaces (listen-only)."""

from opendashcan.hw.listen import (
    DEFAULT_BITRATE,
    DEFAULT_VEHICLE,
    DEFAULT_VIRTUAL_FIXTURE,
    SUPPORTED_BUSTYPES,
    HardwareUnavailableError,
    ListenOnlyBus,
    iter_bus_frames,
    iter_capture_frames,
    open_listen_bus,
    python_can_available,
    resolve_virtual_fixture,
)
from opendashcan.hw.session import IdRateRow, ListenSession
from opendashcan.hw.socketcan_listen import listen_socketcan
from opendashcan.hw.tx_guard import (
    TX_ENV_FLAG,
    assert_tx_permitted,
    refuse_send_message,
    tx_env_enabled,
)

__all__ = [
    "DEFAULT_BITRATE",
    "DEFAULT_VEHICLE",
    "DEFAULT_VIRTUAL_FIXTURE",
    "SUPPORTED_BUSTYPES",
    "TX_ENV_FLAG",
    "HardwareUnavailableError",
    "IdRateRow",
    "ListenOnlyBus",
    "ListenSession",
    "assert_tx_permitted",
    "iter_bus_frames",
    "iter_capture_frames",
    "listen_socketcan",
    "open_listen_bus",
    "python_can_available",
    "refuse_send_message",
    "resolve_virtual_fixture",
    "tx_env_enabled",
]
