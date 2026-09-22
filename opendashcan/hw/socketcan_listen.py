"""Listen-only SocketCAN helper — thin wrapper over ``open_listen_bus``.

Requires python-can + a SocketCAN interface (Linux). Prefer
``opendashcan.hw.listen.open_listen_bus`` for multi-backend desktop use.
"""

from __future__ import annotations

from collections.abc import Iterator

from opendashcan.core.frame import CANFrame
from opendashcan.hw.listen import (
    DEFAULT_BITRATE,
    HardwareUnavailableError,
    iter_bus_frames,
    open_listen_bus,
)


def listen_socketcan(
    channel: str = "can0",
    *,
    bitrate: int | None = DEFAULT_BITRATE,
    max_frames: int | None = None,
) -> Iterator[CANFrame]:
    """Yield RX frames from a SocketCAN interface (listen-only intent).

    Does not call ``bus.send``. Callers must not pass this bus to TX code.
    """
    try:
        bus = open_listen_bus(bustype="socketcan", channel=channel, bitrate=bitrate)
    except HardwareUnavailableError:
        raise
    yield from iter_bus_frames(bus, max_frames=max_frames)
