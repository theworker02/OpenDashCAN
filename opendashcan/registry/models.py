"""Protocol platform models loaded from YAML (canonical CAN knowledge)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from opendashcan.core.confidence import Confidence


def _unk(value: Any) -> Any:
    if value is None or value == "" or value == "UNKNOWN":
        return None
    return value


@dataclass(slots=True)
class VehicleManifest:
    platform_id: str
    manufacturer: str
    model: str
    generation: int | str
    years_start: int | None
    years_end: int | None
    platform_code: str | None = None
    markets: list[str] = field(default_factory=list)
    engines: list[str] = field(default_factory=list)
    transmissions: list[str] = field(default_factory=list)
    protocols: list[str] = field(default_factory=list)
    research_active: bool = True
    physical_validation: str = "incomplete"
    notes: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=lambda: ["source"])
    parent_variant: str | None = None
    path: Path | None = None

    @property
    def colon_id(self) -> str:
        """Legacy colon form derived from dotted id (honda.civic.gen8.us → honda:civic:8)."""
        parts = self.platform_id.split(".")
        if len(parts) >= 3 and parts[2].startswith("gen"):
            return f"{parts[0]}:{parts[1]}:{parts[2][3:]}"
        return self.platform_id.replace(".", ":")

    @property
    def dotted_id(self) -> str:
        """Canonical dotted platform id."""
        return self.platform_id

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, platform_id: str, path: Path) -> VehicleManifest:
        years = data.get("years") or {}
        status = data.get("status") or {}
        return cls(
            platform_id=platform_id,
            manufacturer=str(data.get("manufacturer", "UNKNOWN")),
            model=str(data.get("model", "UNKNOWN")),
            generation=data.get("generation", "UNKNOWN"),
            years_start=_unk(years.get("start")),
            years_end=_unk(years.get("end")),
            platform_code=_unk(data.get("platform")),
            markets=list(data.get("markets") or []),
            engines=list(data.get("engines") or []),
            transmissions=list(data.get("transmissions") or []),
            protocols=list(data.get("protocols") or ["CAN"]),
            research_active=bool(
                status.get("research", "active") == "active" or status.get("research") is True
            ),
            physical_validation=str(status.get("physical_validation", "incomplete")),
            notes=list(data.get("notes") or []),
            aliases=list(data.get("aliases") or []),
            roles=list(data.get("roles") or ["source"]),
            parent_variant=_unk(data.get("parent_variant")),
            path=path,
        )


@dataclass(slots=True)
class BusDefinition:
    bus_id: str
    manufacturer_name: str | None
    protocol: str | None
    bitrate: int | float | str | None
    identifier_width: str | None
    can_fd: bool | None
    gateway_to: list[str] = field(default_factory=list)
    termination: str | None = None
    known_modules: list[str] = field(default_factory=list)
    confidence: Confidence = Confidence.UNKNOWN
    evidence: list[str] = field(default_factory=list)
    notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BusDefinition:
        conf = Confidence(data.get("confidence", "UNKNOWN"))
        return cls(
            bus_id=str(data["id"]),
            manufacturer_name=_unk(data.get("manufacturer_name")),
            protocol=_unk(data.get("protocol")),
            bitrate=_unk(data.get("bitrate")),
            identifier_width=_unk(data.get("identifier_width")),
            can_fd=(
                None
                if data.get("can_fd") in (None, "UNKNOWN", "")
                else bool(data.get("can_fd"))
                if "can_fd" in data
                else None
            ),
            gateway_to=list(data.get("gateway_to") or data.get("gateway_relationships") or []),
            termination=_unk(data.get("termination")),
            known_modules=list(data.get("known_modules") or []),
            confidence=conf,
            evidence=list(data.get("evidence") or []),
            notes=_unk(data.get("notes")),
        )


@dataclass(slots=True)
class ModuleDefinition:
    module_id: str
    display_name: str
    bus: str | None
    role: str | None = None
    tx_ids: list[str] = field(default_factory=list)
    rx_ids: list[str] = field(default_factory=list)
    years: str | None = None
    trim_restrictions: list[str] = field(default_factory=list)
    part_numbers: list[str] = field(default_factory=list)
    confidence: Confidence = Confidence.UNKNOWN
    evidence: list[str] = field(default_factory=list)
    notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModuleDefinition:
        return cls(
            module_id=str(data["module_id"]),
            display_name=str(data.get("display_name", data["module_id"])),
            bus=_unk(data.get("bus")),
            role=_unk(data.get("role")),
            tx_ids=[str(x) for x in (data.get("tx_ids") or [])],
            rx_ids=[str(x) for x in (data.get("rx_ids") or [])],
            years=_unk(data.get("years")),
            trim_restrictions=list(data.get("trim_restrictions") or []),
            part_numbers=list(data.get("part_numbers") or []),
            confidence=Confidence(data.get("confidence", "UNKNOWN")),
            evidence=list(data.get("evidence") or []),
            notes=_unk(data.get("notes")),
        )


@dataclass(slots=True)
class SignalEncoding:
    signal: str
    arbitration_id: str | None
    bus: str | None
    dlc: int | None
    start_bit: int | None
    length: int | None
    byte_order: str | None
    signed: bool | None
    scale: float | None
    offset: float | None
    unit: str | None
    period_ms: float | None
    counter_type: str | None
    checksum_type: str | None
    source_module: str | None
    confidence: Confidence
    evidence: list[str] = field(default_factory=list)
    physical_validation: bool = False
    notes: str | None = None
    message_name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SignalEncoding:
        msg = data.get("message") or {}
        enc = data.get("encoding") or {}
        transport = data.get("transport") or {}
        integrity = data.get("integrity") or {}
        counter = integrity.get("counter") or {}
        checksum = integrity.get("checksum") or {}

        def parse_num(v: Any) -> float | int | None:
            u = _unk(v)
            if u is None:
                return None
            if isinstance(u, (int, float)):
                return u
            try:
                if isinstance(u, str) and u.lower().startswith("0x"):
                    return int(u, 16)
                return float(u) if "." in str(u) else int(u)
            except (TypeError, ValueError):
                return None

        def parse_int(v: Any) -> int | None:
            num = parse_num(v)
            if num is None:
                return None
            return int(num)

        arb = _unk(msg.get("arbitration_id"))
        if isinstance(arb, int):
            arb = hex(arb)

        return cls(
            signal=str(data["signal"]),
            arbitration_id=str(arb) if arb is not None else None,
            bus=_unk(msg.get("bus")),
            dlc=parse_int(msg.get("dlc")),
            start_bit=parse_int(enc.get("start_bit")),
            length=parse_int(enc.get("length")),
            byte_order=_unk(enc.get("byte_order")),
            signed=enc.get("signed") if "signed" in enc else None,
            scale=parse_num(enc.get("scale")),
            offset=parse_num(enc.get("offset")),
            unit=_unk(enc.get("unit")),
            period_ms=parse_num(transport.get("period_ms")),
            counter_type=_unk(counter.get("type")),
            checksum_type=_unk(checksum.get("type")),
            source_module=_unk(data.get("source_module")),
            confidence=Confidence(data.get("confidence", "UNKNOWN")),
            evidence=list(data.get("evidence") or []),
            physical_validation=bool(data.get("physical_validation", False)),
            notes=_unk(data.get("notes")),
            message_name=_unk(msg.get("name")),
        )


@dataclass(slots=True)
class MessageDefinition:
    arbitration_id: str | None
    name: str | None
    bus: str | None
    dlc: int | None
    sender: str | None
    receivers: list[str]
    period_ms: float | None
    confidence: Confidence
    evidence: list[str]
    notes: str | None = None
    checksum_type: str | None = None
    counter_type: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MessageDefinition:
        arb = _unk(data.get("arbitration_id"))
        if isinstance(arb, int):
            arb = hex(arb)
        return cls(
            arbitration_id=str(arb) if arb is not None else None,
            name=_unk(data.get("name")),
            bus=_unk(data.get("bus")),
            dlc=data.get("dlc") if data.get("dlc") not in (None, "UNKNOWN") else None,
            sender=_unk(data.get("sender") or data.get("source_module")),
            receivers=list(data.get("receivers") or []),
            period_ms=(
                None if data.get("period_ms") in (None, "UNKNOWN") else float(data["period_ms"])
            ),
            confidence=Confidence(data.get("confidence", "UNKNOWN")),
            evidence=list(data.get("evidence") or []),
            notes=_unk(data.get("notes")),
            checksum_type=_unk((data.get("integrity") or {}).get("checksum", {}).get("type"))
            if isinstance(data.get("integrity"), dict)
            else _unk(data.get("checksum_type")),
            counter_type=_unk((data.get("integrity") or {}).get("counter", {}).get("type"))
            if isinstance(data.get("integrity"), dict)
            else _unk(data.get("counter_type")),
        )


@dataclass(slots=True)
class ClusterManifest:
    cluster_id: str
    manufacturer: str
    vehicle: str
    generation: int | str
    years_start: int | None
    years_end: int | None
    part_numbers: list[str] = field(default_factory=list)
    display_type: str | None = None
    can_buses: list[str] = field(default_factory=list)
    can_fd: bool | None = None
    physical_fit: dict[str, Any] = field(default_factory=dict)
    compatibility_status: str = "UNKNOWN"
    security_dependencies: list[str] = field(default_factory=list)
    immobilizer_dependencies: list[str] = field(default_factory=list)
    gateway_dependencies: list[str] = field(default_factory=list)
    adas_dependencies: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    platform_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, cluster_id: str) -> ClusterManifest:
        years = data.get("years") or {}
        return cls(
            cluster_id=cluster_id,
            manufacturer=str(data.get("manufacturer", "UNKNOWN")),
            vehicle=str(data.get("vehicle", "UNKNOWN")),
            generation=data.get("generation", "UNKNOWN"),
            years_start=_unk(years.get("start")),
            years_end=_unk(years.get("end")),
            part_numbers=list(data.get("part_numbers") or []),
            display_type=_unk(data.get("display_type")),
            can_buses=list(data.get("CAN_buses") or data.get("can_buses") or []),
            can_fd=data.get("CAN_FD") if "CAN_FD" in data else data.get("can_fd"),
            physical_fit=dict(data.get("physical_fit") or {}),
            compatibility_status=str(data.get("compatibility_status", "UNKNOWN")),
            security_dependencies=list(data.get("security_dependencies") or []),
            immobilizer_dependencies=list(data.get("immobilizer_dependencies") or []),
            gateway_dependencies=list(data.get("gateway_dependencies") or []),
            adas_dependencies=list(
                data.get("ADAS_dependencies") or data.get("adas_dependencies") or []
            ),
            evidence=list(data.get("evidence") or []),
            notes=list(data.get("notes") or []),
            platform_id=_unk(data.get("platform_id")),
        )


@dataclass(slots=True)
class ClusterRequirement:
    """What a donor cluster needs (REQUIRED|OPTIONAL|COSMETIC|UNKNOWN)."""

    signal: str | None = None
    priority: str = "UNKNOWN"  # REQUIRED | OPTIONAL | COSMETIC | UNKNOWN
    confidence: Confidence = Confidence.UNKNOWN
    message: str | None = None
    arbitration_id: str | None = None
    evidence: list[str] = field(default_factory=list)
    notes: str | None = None
    name: str | None = None
    # Legacy Phase-2 fields
    kind: str = "UNKNOWN"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClusterRequirement:
        arb = _unk(data.get("arbitration_id"))
        if isinstance(arb, int):
            arb = hex(arb)
        priority = str(
            data.get("priority") or data.get("kind") or data.get("type") or "UNKNOWN"
        )
        return cls(
            signal=_unk(data.get("signal")),
            priority=priority,
            confidence=Confidence(data.get("confidence", "UNKNOWN")),
            message=_unk(data.get("message")),
            arbitration_id=str(arb) if arb is not None else None,
            evidence=list(data.get("evidence") or []),
            notes=_unk(data.get("notes")),
            name=_unk(data.get("name") or data.get("id")),
            kind=str(data.get("kind") or data.get("type") or priority),
        )


@dataclass(slots=True)
class PlatformPackage:
    """Fully loaded protocol package for one vehicle/platform."""

    vehicle: VehicleManifest
    buses: list[BusDefinition] = field(default_factory=list)
    modules: list[ModuleDefinition] = field(default_factory=list)
    signals: list[SignalEncoding] = field(default_factory=list)
    messages: list[MessageDefinition] = field(default_factory=list)
    cluster: ClusterManifest | None = None
    requirements: list[ClusterRequirement] = field(default_factory=list)
    evidence_index: dict[str, dict[str, Any]] = field(default_factory=dict)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    root: Path | None = None

    @property
    def platform_id(self) -> str:
        return self.vehicle.platform_id

    def signal_map(self) -> dict[str, SignalEncoding]:
        return {s.signal: s for s in self.signals}

    def bus_ids(self) -> set[str]:
        return {b.bus_id for b in self.buses}

    def module_ids(self) -> set[str]:
        return {m.module_id for m in self.modules}
