"""Hardware abstractions for future dual-bus adapters.

Phase 1: interfaces only. No physical TX is enabled by default.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum

from opendashcan.core.frame import BusRole, CANFrame


class LinkMode(str, Enum):
    OFFLINE = "offline"
    LISTEN_ONLY = "listen_only"
    BIDIRECTIONAL = "bidirectional"  # requires explicit enable + allowlist


@dataclass
class BusConfig:
    role: BusRole
    channel: str
    bitrate: int | None = None
    fd: bool = False
    listen_only: bool = True


@dataclass
class DualBusConfig:
    source: BusConfig
    target: BusConfig
    mode: LinkMode = LinkMode.OFFLINE
    tx_enabled: bool = False
    tx_allowlist: set[int] = field(default_factory=set)


class CanInterface(ABC):
    """Single CAN channel interface."""

    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def recv(self, timeout: float | None = None) -> CANFrame | None: ...

    @abstractmethod
    def send(self, frame: CANFrame) -> None:
        """Must refuse unless TX explicitly enabled by backend policy."""


class DualBusAdapter(ABC):
    """Future ESP32/STM32/socketcan dual-bus bridge."""

    def __init__(self, config: DualBusConfig) -> None:
        self.config = config

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def read_source(self, timeout: float | None = None) -> CANFrame | None: ...

    def write_target(self, frame: CANFrame) -> None:
        """Refuse TX unless bidirectional + tx_enabled + env flag + allowlist.

        Future-only. Default install never reaches ``_write_target_impl``.
        """
        from opendashcan.hw.tx_guard import assert_tx_permitted

        if not self.config.tx_enabled or self.config.mode != LinkMode.BIDIRECTIONAL:
            raise RuntimeError(
                "Target TX disabled (LISTEN_ONLY / OFFLINE default). Enable only with "
                "hardware isolation, OPENDASHCAN_ALLOW_TX=1, allowlists, and verified evidence."
            )
        assert_tx_permitted(
            frame.arbitration_id,
            allowlist=self.config.tx_allowlist,
            mode_label=self.config.mode.value,
        )
        self._write_target_impl(frame)

    @abstractmethod
    def _write_target_impl(self, frame: CANFrame) -> None: ...

    def write_target_many(self, frames: Iterable[CANFrame]) -> None:
        for fr in frames:
            self.write_target(fr)


class NullDualBusAdapter(DualBusAdapter):
    """Software placeholder used in tests — never transmits."""

    def connect(self) -> None:
        return None

    def disconnect(self) -> None:
        return None

    def read_source(self, timeout: float | None = None) -> CANFrame | None:
        _ = timeout
        return None

    def _write_target_impl(self, frame: CANFrame) -> None:
        _ = frame
        raise RuntimeError("NullDualBusAdapter cannot transmit")
