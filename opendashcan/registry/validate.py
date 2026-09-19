"""Validate protocol packages against schemas and referential integrity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from opendashcan.core.confidence import (
    Confidence,
    validate_confidence_promotion,
)
from opendashcan.core.taxonomy import is_valid_signal_path
from opendashcan.registry.loader import (
    ProtocolRegistry,
    discover_package_dirs,
    get_registry,
    load_platform,
)
from opendashcan.registry.models import PlatformPackage

# Re-export loader helpers used by validate tools
__all__ = [
    "validate_platform",
    "validate_registry",
    "ValidationReport",
]


class ValidationReport:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def validate_platform(pkg: PlatformPackage) -> ValidationReport:
    report = ValidationReport()
    pid = pkg.platform_id
    bus_ids = pkg.bus_ids()
    module_ids = pkg.module_ids()
    evidence_ids = set(pkg.evidence_index.keys())

    # Duplicate signals
    seen_signals: set[str] = set()
    for sig in pkg.signals:
        if sig.signal in seen_signals:
            report.error(f"{pid}: duplicate signal definition {sig.signal}")
        seen_signals.add(sig.signal)
        if not is_valid_signal_path(sig.signal):
            report.warn(f"{pid}: signal {sig.signal} not in global taxonomy")
        if sig.bus and sig.bus not in bus_ids:
            report.error(f"{pid}: signal {sig.signal} references unknown bus {sig.bus}")
        if sig.source_module and sig.source_module not in module_ids:
            report.error(
                f"{pid}: signal {sig.signal} references unknown module {sig.source_module}"
            )
        for eid in sig.evidence:
            if evidence_ids and eid not in evidence_ids:
                report.warn(f"{pid}: signal {sig.signal} evidence id {eid} not in evidence/")

        # Confidence promotion
        ev_records: list[dict[str, Any]] = []
        for eid in sig.evidence:
            if eid in pkg.evidence_index:
                ev_records.append(pkg.evidence_index[eid])
        # Also accept inline evidence dicts stored under evidence_index by claim
        report.errors.extend(
            validate_confidence_promotion(sig.confidence, ev_records, path=f"{pid}:{sig.signal}")
        )
        if sig.physical_validation and sig.confidence not in (
            Confidence.PHYSICALLY_VERIFIED,
            Confidence.VERIFIED,
            Confidence.CAPTURE_VERIFIED,
        ):
            report.error(
                f"{pid}: signal {sig.signal} physical_validation=true requires "
                "CAPTURE_VERIFIED or PHYSICALLY_VERIFIED"
            )

    for bus in pkg.buses:
        for mid in bus.known_modules:
            if module_ids and mid not in module_ids:
                report.warn(f"{pid}: bus {bus.bus_id} lists unknown module {mid}")

    for mod in pkg.modules:
        if mod.bus and mod.bus not in bus_ids:
            report.error(f"{pid}: module {mod.module_id} references unknown bus {mod.bus}")

    for msg in pkg.messages:
        if msg.bus and msg.bus not in bus_ids:
            report.error(f"{pid}: message {msg.name or msg.arbitration_id} unknown bus {msg.bus}")
        if msg.sender and msg.sender not in module_ids:
            report.warn(
                f"{pid}: message {msg.name or msg.arbitration_id} unknown sender {msg.sender}"
            )

    # Duplicate arbitration IDs on same bus (warn — multiplexing can be legitimate)
    seen_ids: dict[tuple[str | None, str | None], str] = {}
    for msg in pkg.messages:
        key = (msg.bus, msg.arbitration_id)
        if msg.arbitration_id and key in seen_ids:
            report.warn(
                f"{pid}: duplicate arbitration_id {msg.arbitration_id} on bus {msg.bus} "
                f"({seen_ids[key]} vs {msg.name})"
            )
        if msg.arbitration_id:
            seen_ids[key] = msg.name or msg.arbitration_id

    return report


def validate_registry(registry: ProtocolRegistry | None = None) -> ValidationReport:
    reg = registry or get_registry()
    report = ValidationReport()
    for pkg in reg.list_platforms():
        sub = validate_platform(pkg)
        report.errors.extend(sub.errors)
        report.warnings.extend(sub.warnings)
    return report


def validate_all_packages_on_disk(root: Path | None = None) -> ValidationReport:
    report = ValidationReport()
    for d in discover_package_dirs(root):
        try:
            pkg = load_platform(d)
        except Exception as exc:  # noqa: BLE001 — collect all load failures
            report.error(f"failed to load {d}: {exc}")
            continue
        sub = validate_platform(pkg)
        report.errors.extend(sub.errors)
        report.warnings.extend(sub.warnings)
    return report
