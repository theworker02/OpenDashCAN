"""Periodic TX scheduler hooks (documentation / software validation only).

Does not transmit on hardware. Schedules describe intended periods from
protocol documentation when known; UNKNOWN periods stay None.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendashcan.core.encoder import PeriodicFrameSpec
from opendashcan.registry.models import MessageDefinition, PlatformPackage


@dataclass
class ScheduledMessage:
    arbitration_id: str | None
    name: str | None
    period_ms: float | None
    confidence: str
    bus: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "arbitration_id": self.arbitration_id,
            "name": self.name,
            "period_ms": self.period_ms,
            "confidence": self.confidence,
            "bus": self.bus,
            "notes": self.notes,
        }


@dataclass
class SchedulePlan:
    platform_id: str
    messages: list[ScheduledMessage] = field(default_factory=list)
    mode: str = "DOCUMENTATION_ONLY"

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform_id": self.platform_id,
            "mode": self.mode,
            "messages": [m.to_dict() for m in self.messages],
            "label": "SOFTWARE VALIDATION ONLY — no hardware TX",
        }


def schedule_from_package(pkg: PlatformPackage) -> SchedulePlan:
    msgs: list[ScheduledMessage] = []
    for m in pkg.messages:
        msgs.append(
            ScheduledMessage(
                arbitration_id=m.arbitration_id,
                name=m.name,
                period_ms=m.period_ms,
                confidence=m.confidence.value,
                bus=m.bus,
                notes=m.notes,
            )
        )
    return SchedulePlan(platform_id=pkg.platform_id, messages=msgs)


def schedule_from_specs(
    platform_id: str, specs: list[PeriodicFrameSpec]
) -> SchedulePlan:
    msgs = [
        ScheduledMessage(
            arbitration_id=hex(s.arbitration_id),
            name=s.name,
            period_ms=s.period_ms,
            confidence="SYNTHETIC" if s.synthetic else "DOCUMENTED",
            notes=s.notes,
        )
        for s in specs
    ]
    return SchedulePlan(platform_id=platform_id, messages=msgs)


def message_due(msg: MessageDefinition, elapsed_ms: float, last_tx_ms: float | None) -> bool:
    """Return True if period is known and elapsed since last TX."""
    if msg.period_ms is None:
        return False
    if last_tx_ms is None:
        return True
    return (elapsed_ms - last_tx_ms) >= msg.period_ms
