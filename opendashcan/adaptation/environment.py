"""ClusterEnvironment — modules/messages a donor cluster expects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendashcan.core.state import VehicleState
from opendashcan.registry.models import ClusterRequirement, PlatformPackage


@dataclass
class ClusterEnvironment:
    """Software model of the environment a donor cluster expects.

    Populated from target protocol documentation only. Does not invent
    safety-critical frames. DOCUMENTATION_ONLY / SOFTWARE VALIDATION ONLY.
    """

    cluster_id: str
    platform_id: str
    requirements: list[ClusterRequirement] = field(default_factory=list)
    expected_messages: list[dict[str, Any]] = field(default_factory=list)
    emulated_modules: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    state: VehicleState = field(default_factory=VehicleState)

    @classmethod
    def from_package(cls, pkg: PlatformPackage) -> ClusterEnvironment:
        if pkg.cluster is None:
            raise ValueError(f"{pkg.platform_id} has no cluster.yaml")
        unknowns: list[str] = []
        expected: list[dict[str, Any]] = []
        for msg in pkg.messages:
            expected.append(
                {
                    "arbitration_id": msg.arbitration_id,
                    "name": msg.name,
                    "confidence": msg.confidence.value,
                    "period_ms": msg.period_ms,
                    "checksum_type": msg.checksum_type,
                    "counter_type": msg.counter_type,
                }
            )
            if msg.confidence.value == "UNKNOWN" or msg.arbitration_id is None:
                unknowns.append(f"message:{msg.name or 'unnamed'}")
        for req in pkg.requirements:
            if req.priority in ("REQUIRED", "OPTIONAL") and req.confidence.value == "UNKNOWN":
                unknowns.append(f"requirement:{req.signal or req.name or 'unnamed'}")
        modules = [m.module_id for m in pkg.modules if m.role in ("powertrain", "cluster", None)]
        return cls(
            cluster_id=pkg.cluster.cluster_id,
            platform_id=pkg.platform_id,
            requirements=list(pkg.requirements),
            expected_messages=expected,
            emulated_modules=modules,
            unknowns=unknowns,
        )

    def observe_state(self, state: VehicleState) -> None:
        """Accept normalized VehicleState for later encoding (no invented CAN)."""
        self.state = state

    def gap_report(self) -> dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "platform_id": self.platform_id,
            "expected_message_count": len(self.expected_messages),
            "requirement_count": len(self.requirements),
            "unknowns": list(self.unknowns),
            "label": "SOFTWARE VALIDATION ONLY / DOCUMENTATION_ONLY",
        }
