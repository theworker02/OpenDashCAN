"""CAN frame types prepared for classic CAN and future CAN FD."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class BusRole(str, Enum):
    """Logical bus role in a dual-bus translation setup."""

    SOURCE = "source"
    TARGET = "target"
    UNKNOWN = "unknown"


class FrameDirection(str, Enum):
    RX = "rx"
    TX = "tx"
    UNKNOWN = "unknown"


class CanFormat(str, Enum):
    CLASSIC = "classic"
    FD = "fd"


@dataclass(frozen=True, slots=True)
class CANFrame:
    """Immutable CAN frame representation.

    Phase 1 is software-only. Frames are used for replay/analysis — never for
    live transmission unless a future hardware backend explicitly enables TX.

    Field aliases:
    - ``arb_id`` / ``arbitration_id`` — 11- or 29-bit identifier
    - ``payload`` / ``data`` — raw bytes
    """

    arbitration_id: int
    data: bytes
    timestamp: float
    dlc: int | None = None
    bus: BusRole | str = BusRole.UNKNOWN
    is_extended: bool = False
    is_fd: bool = False
    bitrate_switch: bool = False
    error_state_indicator: bool = False
    direction: FrameDirection = FrameDirection.UNKNOWN
    channel: str | None = None
    meta: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.arbitration_id < 0:
            raise ValueError("arbitration_id must be non-negative")
        max_id = 0x1FFFFFFF if self.is_extended else 0x7FF
        if self.arbitration_id > max_id:
            raise ValueError(
                f"arbitration_id 0x{self.arbitration_id:X} exceeds "
                f"{'29' if self.is_extended else '11'}-bit limit"
            )
        payload = bytes(self.data)
        object.__setattr__(self, "data", payload)
        max_len = 64 if self.is_fd else 8
        if len(payload) > max_len:
            raise ValueError(f"payload length {len(payload)} exceeds max {max_len}")
        effective_dlc = self.dlc if self.dlc is not None else len(payload)
        if effective_dlc < 0 or effective_dlc > max_len:
            raise ValueError(f"invalid DLC {effective_dlc}")
        if self.dlc is None:
            object.__setattr__(self, "dlc", effective_dlc)

    @property
    def arb_id(self) -> int:
        """Alias for arbitration_id."""
        return self.arbitration_id

    @property
    def payload(self) -> bytes:
        """Alias for data."""
        return self.data

    @property
    def format(self) -> CanFormat:
        return CanFormat.FD if self.is_fd else CanFormat.CLASSIC

    @property
    def id_hex(self) -> str:
        width = 8 if self.is_extended else 3
        return f"0x{self.arbitration_id:0{width}X}"

    def data_hex(self, sep: Literal["", " "] = " ") -> str:
        if sep:
            return sep.join(f"{b:02X}" for b in self.data)
        return self.data.hex().upper()
