"""Abstract cluster encoder interface with periodic / checksum hooks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

from opendashcan.core.frame import CANFrame
from opendashcan.core.state import VehicleState

__all__ = [
    "ChecksumProtocol",
    "ClusterEncoder",
    "CounterProtocol",
    "EncodeMode",
    "EncoderContext",
    "OutputKind",
    "PeriodicFrameSpec",
    "gate_encode",
]


class EncodeMode(str, Enum):
    """Encoder emission policy.

    NO_OUTPUT — default; encode() returns [].
    RESEARCH_DOCUMENTED — may emit frames whose layouts are DOCUMENTED (tagged).
    SYNTHETIC — emit clearly labeled SYNTHETIC research frames only.
    PRODUCTION — blocks UNKNOWN/HYPOTHESIS/INFERRED; requires high confidence.
    """

    NO_OUTPUT = "NO_OUTPUT"
    RESEARCH_DOCUMENTED = "RESEARCH_DOCUMENTED"
    SYNTHETIC = "SYNTHETIC"
    PRODUCTION = "PRODUCTION"


class OutputKind(str, Enum):
    """What encode() produced — for tests and adapter reports."""

    NO_OUTPUT = "NO_OUTPUT"
    RESEARCH_DOCUMENTED = "RESEARCH_DOCUMENTED"
    SYNTHETIC = "SYNTHETIC"


def gate_encode(mode: EncodeMode) -> bool:
    """Return True if encode() is allowed to produce any frames under mode."""
    return mode != EncodeMode.NO_OUTPUT


@dataclass(frozen=True, slots=True)
class PeriodicFrameSpec:
    """Describes a periodic outbound frame schedule (architecture hook only)."""

    arbitration_id: int
    period_ms: float
    dlc: int = 8
    name: str | None = None
    notes: str | None = None
    requires_checksum: bool = False
    requires_counter: bool = False
    synthetic: bool = False


class ChecksumProtocol(Protocol):
    def apply(self, data: bytearray, *, nibble_index: int | None = None) -> bytes: ...


class CounterProtocol(Protocol):
    def next_value(self) -> int: ...

    def embed(self, data: bytearray, counter: int) -> bytes: ...


@dataclass
class EncoderContext:
    counters: dict[int, int] = field(default_factory=dict)
    last_tx_ms: dict[int, float] = field(default_factory=dict)


class ClusterEncoder(ABC):
    """Encode normalized VehicleState into target-cluster CAN frames.

    Default policy: ``EncodeMode.NO_OUTPUT`` — return ``[]`` until evidence
    and an explicit mode allow emission.
    """

    cluster_id: str
    display_name: str
    encode_mode: EncodeMode = EncodeMode.NO_OUTPUT

    @abstractmethod
    def encode(self, state: VehicleState, timestamp: float | None = None) -> list[CANFrame]:
        """Produce frames for the target cluster bus (offline / simulated)."""

    @abstractmethod
    def supported_signals(self) -> dict[str, str]:
        """Map signal name -> confidence label for documented capabilities."""

    def last_output_kind(self) -> OutputKind:
        return OutputKind.NO_OUTPUT

    def allows_emission(self) -> bool:
        return gate_encode(self.encode_mode)

    def periodic_specs(self) -> list[PeriodicFrameSpec]:
        return []

    def checksum_protocol(self) -> ChecksumProtocol | None:
        return None

    def counter_protocol(self) -> CounterProtocol | None:
        return None
