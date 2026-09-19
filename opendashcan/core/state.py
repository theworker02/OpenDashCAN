"""Normalized vehicle state with per-signal evidence metadata.

Unknown stays UNKNOWN: defaults are ``None`` / missing SignalValue entries —
never invented numeric defaults that pretend to be measured values.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any, Generic, TypeVar

from opendashcan.core.taxonomy import (
    FLAT_TO_TAXONOMY,
    SIGNAL_UNITS,
    TAXONOMY_TO_FLAT,
    resolve_signal_path,
)

T = TypeVar("T")


class Confidence(str, Enum):
    """Evidence confidence for a decoded or encoded signal value."""

    VERIFIED = "VERIFIED"
    SUPPORTED_BY_MULTIPLE_SOURCES = "SUPPORTED_BY_MULTIPLE_SOURCES"
    COMMUNITY_REPORTED = "COMMUNITY_REPORTED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"
    # Phase-2 labels also accepted on SignalValue
    HYPOTHESIS = "HYPOTHESIS"
    DOCUMENTED = "DOCUMENTED"
    CAPTURE_VERIFIED = "CAPTURE_VERIFIED"
    PHYSICALLY_VERIFIED = "PHYSICALLY_VERIFIED"


class Validity(str, Enum):
    VALID = "valid"
    STALE = "stale"
    INVALID = "invalid"
    UNKNOWN = "unknown"


class GearPosition(str, Enum):
    PARK = "P"
    REVERSE = "R"
    NEUTRAL = "N"
    DRIVE = "D"
    LOW = "L"
    MANUAL = "M"
    UNKNOWN = "UNKNOWN"


class IgnitionState(str, Enum):
    OFF = "OFF"
    ACC = "ACC"
    ON = "ON"
    RUN = "RUN"
    START = "START"
    UNKNOWN = "UNKNOWN"


class TransmissionState(str, Enum):
    UNKNOWN = "UNKNOWN"
    PARKED = "PARKED"
    IN_GEAR = "IN_GEAR"
    SHIFTING = "SHIFTING"


@dataclass(frozen=True, slots=True)
class DoorStates:
    """Per-door open/closed flags. ``None`` means unknown (not assumed closed)."""

    driver: bool | None = None
    passenger: bool | None = None
    rear_left: bool | None = None
    rear_right: bool | None = None


@dataclass(frozen=True, slots=True)
class SignalValue(Generic[T]):
    """A typed vehicle signal with provenance metadata."""

    value: T | None
    timestamp: float | None = None
    source: str | None = None
    confidence: Confidence = Confidence.UNKNOWN
    validity: Validity = Validity.UNKNOWN
    unit: str | None = None
    notes: str | None = None
    evidence_refs: tuple[str, ...] = ()
    # Namespaced provenance (Phase 2/3)
    source_vehicle: str | None = None
    source_bus: str | None = None
    source_module: str | None = None
    source_message: str | None = None

    def with_update(
        self,
        value: T | None,
        *,
        timestamp: float | None = None,
        source: str | None = None,
        confidence: Confidence | None = None,
        validity: Validity | None = None,
        unit: str | None = None,
        notes: str | None = None,
        evidence_refs: tuple[str, ...] | None = None,
        source_vehicle: str | None = None,
        source_bus: str | None = None,
        source_module: str | None = None,
        source_message: str | None = None,
    ) -> SignalValue[T]:
        return SignalValue(
            value=value,
            timestamp=timestamp if timestamp is not None else self.timestamp,
            source=source if source is not None else self.source,
            confidence=confidence if confidence is not None else self.confidence,
            validity=validity if validity is not None else self.validity,
            unit=unit if unit is not None else self.unit,
            notes=notes if notes is not None else self.notes,
            evidence_refs=evidence_refs if evidence_refs is not None else self.evidence_refs,
            source_vehicle=source_vehicle if source_vehicle is not None else self.source_vehicle,
            source_bus=source_bus if source_bus is not None else self.source_bus,
            source_module=source_module if source_module is not None else self.source_module,
            source_message=source_message if source_message is not None else self.source_message,
        )

    def to_meta_dict(self) -> dict[str, Any]:
        value: Any = self.value
        if isinstance(value, DoorStates):
            value = {
                "driver": value.driver,
                "passenger": value.passenger,
                "rear_left": value.rear_left,
                "rear_right": value.rear_right,
            }
        return {
            "value": value,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "source": self.source,
            "source_vehicle": self.source_vehicle,
            "source_bus": self.source_bus,
            "source_module": self.source_module,
            "source_message": self.source_message,
            "confidence": self.confidence.value,
            "validity": self.validity.value,
            "notes": self.notes,
            "evidence_refs": list(self.evidence_refs),
        }


def _unknown(unit: str | None = None) -> SignalValue[Any]:
    return SignalValue(
        value=None,
        unit=unit,
        confidence=Confidence.UNKNOWN,
        validity=Validity.UNKNOWN,
    )


# Flat Phase-1 field names that live as attributes on VehicleState
_FLAT_FIELDS = frozenset(FLAT_TO_TAXONOMY.keys()) | {
    "warning_lamps",
    "door_states",
}


@dataclass(slots=True)
class VehicleState:
    """Normalized vehicle state shared by decoders and encoders.

    Flat Phase-1 fields are preserved for backward compatibility. Prefer
    ``get`` / ``set`` with dotted taxonomy paths for new code. Never coerce
    UNKNOWN to 0/false.
    """

    engine_rpm: SignalValue[float] = field(default_factory=lambda: _unknown("rpm"))
    vehicle_speed: SignalValue[float] = field(default_factory=lambda: _unknown("kph"))
    coolant_temperature: SignalValue[float] = field(default_factory=lambda: _unknown("C"))
    fuel_level: SignalValue[float] = field(default_factory=lambda: _unknown("percent"))
    gear_position: SignalValue[str] = field(default_factory=_unknown)
    transmission_state: SignalValue[str] = field(default_factory=_unknown)
    turn_signal_left: SignalValue[bool] = field(default_factory=_unknown)
    turn_signal_right: SignalValue[bool] = field(default_factory=_unknown)
    hazards: SignalValue[bool] = field(default_factory=_unknown)
    high_beam: SignalValue[bool] = field(default_factory=_unknown)
    low_beam: SignalValue[bool] = field(default_factory=_unknown)
    parking_brake: SignalValue[bool] = field(default_factory=_unknown)
    warning_lamps: SignalValue[dict[str, bool]] = field(default_factory=_unknown)
    door_states: SignalValue[DoorStates | dict[str, bool | None]] = field(default_factory=_unknown)
    trunk_state: SignalValue[bool] = field(default_factory=_unknown)
    ignition_state: SignalValue[str] = field(default_factory=_unknown)

    # Namespaced store for taxonomy paths (and any extra signals)
    _store: dict[str, SignalValue[Any]] = field(default_factory=dict, repr=False)

    def get(self, path: str) -> SignalValue[Any]:
        """Get by dotted taxonomy path or flat Phase-1 name. Missing → UNKNOWN."""
        try:
            dotted = resolve_signal_path(path) if "." in path or path in FLAT_TO_TAXONOMY else path
        except KeyError:
            dotted = path
        if dotted in self._store:
            return self._store[dotted]
        flat = TAXONOMY_TO_FLAT.get(dotted)
        if flat is not None and hasattr(self, flat):
            return getattr(self, flat)  # type: ignore[no-any-return]
        if path in _FLAT_FIELDS and hasattr(self, path):
            return getattr(self, path)  # type: ignore[no-any-return]
        unit = SIGNAL_UNITS.get(dotted)
        return _unknown(unit)

    def set(
        self,
        path: str,
        value: Any,
        *,
        unit: str | None = None,
        timestamp: float | None = None,
        source: str | None = None,
        source_vehicle: str | None = None,
        source_bus: str | None = None,
        source_module: str | None = None,
        source_message: str | None = None,
        confidence: Confidence = Confidence.UNKNOWN,
        validity: Validity = Validity.UNKNOWN,
        notes: str | None = None,
        evidence_refs: tuple[str, ...] = (),
    ) -> None:
        """Set by dotted path. Does not coerce None/UNKNOWN to 0/false."""
        try:
            dotted = resolve_signal_path(path)
        except KeyError:
            dotted = path if "." in path else path

        sig: SignalValue[Any] = SignalValue(
            value=value,
            unit=unit if unit is not None else SIGNAL_UNITS.get(dotted),
            timestamp=timestamp,
            source=source,
            source_vehicle=source_vehicle,
            source_bus=source_bus,
            source_module=source_module,
            source_message=source_message,
            confidence=confidence,
            validity=validity,
            notes=notes,
            evidence_refs=evidence_refs,
        )
        self._store[dotted] = sig
        flat = TAXONOMY_TO_FLAT.get(dotted)
        if flat is not None and hasattr(self, flat):
            setattr(self, flat, sig)

    def as_dict(self) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for f in fields(self):
            if f.name.startswith("_"):
                continue
            sig: SignalValue[Any] = getattr(self, f.name)
            out[f.name] = sig.to_meta_dict()
        for path, sig in self._store.items():
            out[path] = sig.to_meta_dict()
        return out

    def known_signals(self) -> list[str]:
        names: list[str] = []
        for f in fields(self):
            if f.name.startswith("_"):
                continue
            sig: SignalValue[Any] = getattr(self, f.name)
            if sig.value is not None and sig.confidence != Confidence.UNKNOWN:
                names.append(f.name)
        for path, sig in self._store.items():
            if (
                sig.value is not None
                and sig.confidence != Confidence.UNKNOWN
                and path not in names
                and TAXONOMY_TO_FLAT.get(path) not in names
            ):
                names.append(path)
        return names
