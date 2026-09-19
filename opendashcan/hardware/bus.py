"""Dual-bus bridge interface. TransmitMode.DISABLED is the hard default.

Phase 1 is software-only. Implementations must not enable hardware TX unless
a future milestone explicitly opts in after VERIFIED evidence and safety review.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from enum import Enum

from opendashcan.core.frame import CANFrame


class TransmitMode(str, Enum):
    DISABLED = "disabled"  # default — never TX
    LISTEN_ONLY = "listen_only"  # RX only (controller listen-only if supported)
    ENABLED = "enabled"  # future — requires explicit opt-in; not used in 0.1


class DualBusBridge(ABC):
    """Abstract dual-bus (source + target) interface."""

    def __init__(self, transmit_mode: TransmitMode = TransmitMode.DISABLED) -> None:
        self.transmit_mode = transmit_mode

    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def recv(self, *, timeout_s: float | None = None) -> CANFrame | None:
        """Receive one frame from the source (or multiplexed) bus."""

    def send(self, frame: CANFrame) -> None:
        """Transmit to target bus — blocked unless ENABLED + env + allowlist.

        Future-only. Default ``TransmitMode.DISABLED`` / LISTEN_ONLY never TX's.
        """
        from opendashcan.hw.tx_guard import assert_tx_permitted

        if self.transmit_mode != TransmitMode.ENABLED:
            raise RuntimeError(
                f"TX blocked: transmit_mode={self.transmit_mode.value} "
                "(OpenDashCAN default is DISABLED / LISTEN_ONLY)"
            )
        # Subclasses may expose an allowlist; default empty → still refused.
        allowlist = getattr(self, "tx_allowlist", None) or set()
        assert_tx_permitted(
            frame.arbitration_id,
            allowlist=allowlist,
            mode_label=self.transmit_mode.value,
        )
        self._send_impl(frame)

    def send_many(self, frames: Iterable[CANFrame]) -> None:
        for fr in frames:
            self.send(fr)

    @abstractmethod
    def _send_impl(self, frame: CANFrame) -> None:
        """Backend-specific TX (only reached when ENABLED)."""


class NullBridge(DualBusBridge):
    """Software placeholder bridge — never opens hardware."""

    def open(self) -> None:
        return None

    def close(self) -> None:
        return None

    def recv(self, *, timeout_s: float | None = None) -> CANFrame | None:
        _ = timeout_s
        return None

    def _send_impl(self, frame: CANFrame) -> None:
        _ = frame
        raise RuntimeError("NullBridge cannot transmit")
