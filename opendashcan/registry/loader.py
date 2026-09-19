"""Filesystem discovery and loading of protocol platform packages."""

from __future__ import annotations

import contextlib
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

from opendashcan.registry.ids import (
    CLUSTER_TO_PLATFORM,
    LEGACY_ALIASES,
    LEGACY_CLUSTER_IDS,
    adapter_id,
    infer_platform_id_from_path,
    normalize_cluster_id,
    normalize_platform_id,
    normalize_variant_id,
)
from opendashcan.registry.models import (
    BusDefinition,
    ClusterManifest,
    ClusterRequirement,
    MessageDefinition,
    ModuleDefinition,
    PlatformPackage,
    SignalEncoding,
    VehicleManifest,
)

PROTOCOLS_ROOT = Path(__file__).resolve().parent.parent / "protocols"

# Re-export for callers that imported from loader
__all__ = [
    "CLUSTER_ALIASES",
    "LEGACY_ALIASES",
    "PROTOCOLS_ROOT",
    "ProtocolRegistry",
    "adapter_id",
    "discover_package_dirs",
    "get_registry",
    "infer_platform_id_from_path",
    "iter_signal_implementations",
    "load_platform",
    "normalize_cluster_id",
    "normalize_platform_id",
    "normalize_variant_id",
]

# Back-compat name used by older imports
CLUSTER_ALIASES = {**LEGACY_CLUSTER_IDS, **CLUSTER_TO_PLATFORM}


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be mapping: {path}")
    return data


def _infer_platform_id(vehicle_yaml: dict[str, Any], package_dir: Path) -> str:
    if "platform_id" in vehicle_yaml:
        raw = str(vehicle_yaml["platform_id"])
        # Accept already-canonical dotted or legacy forms
        try:
            return normalize_platform_id(raw)
        except KeyError:
            # Variant id stored as platform_id — keep as-is if dotted with gen
            if ".gen" in raw.replace(":", "."):
                return normalize_variant_id(raw)
            raise
    inferred = infer_platform_id_from_path(package_dir)
    if inferred is None:
        raise ValueError(f"cannot infer platform_id from {package_dir}")
    return inferred


def discover_package_dirs(root: Path | None = None) -> list[Path]:
    """Find directories containing vehicle.yaml under protocols/.

    Prefers ``.../genN/us/`` over ``.../genN/YYYY_YYYY/`` when both exist for
    the same generation (avoids duplicate platform registration).
    """
    base = root or PROTOCOLS_ROOT
    if not base.is_dir():
        return []
    found = sorted(p.parent for p in base.rglob("vehicle.yaml"))
    # Group by (mfr, model, gen) parent
    by_gen: dict[tuple[str, ...], list[Path]] = {}
    for d in found:
        parts = d.parts
        try:
            idx = parts.index("protocols")
            key = parts[idx + 1 : idx + 4]  # honda, civic, gen8
        except (ValueError, IndexError):
            key = (str(d),)
        by_gen.setdefault(key, []).append(d)

    selected: list[Path] = []
    for dirs in by_gen.values():
        us_dirs = [d for d in dirs if d.name.lower() == "us"]
        year_dirs = [d for d in dirs if re.fullmatch(r"\d{4}_\d{4}", d.name)]
        other = [d for d in dirs if d not in us_dirs and d not in year_dirs]
        if us_dirs:
            selected.extend(us_dirs)
            # Keep non-year extras (e.g. eu/) but skip year-range duplicates
            selected.extend(other)
        else:
            selected.extend(dirs)
    return sorted(set(selected))


def load_platform(package_dir: Path) -> PlatformPackage:
    vehicle_raw = _load_yaml(package_dir / "vehicle.yaml")
    platform_id = _infer_platform_id(vehicle_raw, package_dir)
    vehicle = VehicleManifest.from_dict(vehicle_raw, platform_id=platform_id, path=package_dir)

    buses_raw = _load_yaml(package_dir / "buses.yaml")
    buses = [BusDefinition.from_dict(b) for b in (buses_raw.get("buses") or [])]

    modules_raw = _load_yaml(package_dir / "modules.yaml")
    modules = [ModuleDefinition.from_dict(m) for m in (modules_raw.get("modules") or [])]

    signals_raw = _load_yaml(package_dir / "signals.yaml")
    signals = [SignalEncoding.from_dict(s) for s in (signals_raw.get("signals") or [])]

    messages_raw = _load_yaml(package_dir / "messages.yaml")
    messages = [MessageDefinition.from_dict(m) for m in (messages_raw.get("messages") or [])]

    cluster = None
    cluster_raw = _load_yaml(package_dir / "cluster.yaml")
    if cluster_raw:
        raw_cid = str(cluster_raw.get("cluster_id", ""))
        if raw_cid:
            try:
                cid = normalize_cluster_id(raw_cid)
            except Exception:  # noqa: BLE001
                cid = raw_cid.replace(":", ".")
        else:
            from opendashcan.registry.ids import platform_to_cluster_id

            cid = platform_to_cluster_id(platform_id)
        cluster = ClusterManifest.from_dict(cluster_raw, cluster_id=cid)
        if cluster.platform_id is None:
            cluster.platform_id = platform_id
        else:
            try:
                cluster.platform_id = normalize_platform_id(str(cluster.platform_id))
            except KeyError:
                cluster.platform_id = str(cluster.platform_id).replace(":", ".")

    requirements_raw = _load_yaml(package_dir / "requirements.yaml")
    requirements = [
        ClusterRequirement.from_dict(r) for r in (requirements_raw.get("requirements") or [])
    ]

    evidence_index: dict[str, dict[str, Any]] = {}
    evidence_dir = package_dir / "evidence"
    if evidence_dir.is_dir():
        for ev_path in sorted(evidence_dir.glob("*.yaml")):
            doc = _load_yaml(ev_path)
            records = doc.get("evidence") or doc.get("records") or []
            if isinstance(records, list):
                for rec in records:
                    if isinstance(rec, dict) and "evidence_id" in rec:
                        evidence_index[str(rec["evidence_id"])] = rec
            elif "evidence_id" in doc:
                evidence_index[str(doc["evidence_id"])] = doc

    conflicts_raw = _load_yaml(package_dir / "conflicts.yaml")
    conflicts = list(conflicts_raw.get("conflicts") or [])

    return PlatformPackage(
        vehicle=vehicle,
        buses=buses,
        modules=modules,
        signals=signals,
        messages=messages,
        cluster=cluster,
        requirements=requirements,
        evidence_index=evidence_index,
        conflicts=conflicts,
        root=package_dir,
    )


class ProtocolRegistry:
    """In-memory multi-vehicle protocol registry (canonical knowledge base)."""

    def __init__(self) -> None:
        self._platforms: dict[str, PlatformPackage] = {}
        self._alias: dict[str, str] = dict(LEGACY_ALIASES)
        self._alias.update(CLUSTER_TO_PLATFORM)
        self._alias.update(LEGACY_CLUSTER_IDS)
        self._clusters: dict[str, PlatformPackage] = {}
        self._variants: dict[str, str] = {}  # variant_id → platform_id

    def load_all(self, root: Path | None = None) -> None:
        for d in discover_package_dirs(root):
            pkg = load_platform(d)
            self.register(pkg)

    def register(self, pkg: PlatformPackage) -> None:
        pid = pkg.platform_id
        if pid in self._platforms:
            # Prefer us/ package over year-range if both somehow loaded
            existing = self._platforms[pid]
            if existing.root and pkg.root:
                if existing.root.name == "us" and pkg.root.name != "us":
                    return
                if pkg.root.name == "us" and existing.root.name != "us":
                    pass  # replace below
                else:
                    raise ValueError(f"duplicate platform_id: {pid}")
            else:
                raise ValueError(f"duplicate platform_id: {pid}")
        self._platforms[pid] = pkg
        for alias in pkg.vehicle.aliases:
            self._alias[alias.lower()] = pid
            with contextlib.suppress(Exception):
                self._alias[normalize_variant_id(alias)] = pid
        # Hyphen / colon forms of dotted id
        self._alias[pid.replace(".", "-")] = pid
        self._alias[pid.replace(".", ":")] = pid
        # Short colon form honda:civic:8
        parts = pid.split(".")
        if len(parts) >= 3 and parts[2].startswith("gen"):
            short = f"{parts[0]}:{parts[1]}:{parts[2][3:]}"
            self._alias[short] = pid

        if pkg.cluster is not None:
            cid = pkg.cluster.cluster_id.lower()
            self._clusters[cid] = pkg
            self._alias[cid] = pid
            # Legacy colon cluster alias
            for legacy, dotted in LEGACY_CLUSTER_IDS.items():
                if dotted == cid:
                    self._alias[legacy] = pid
                    self._clusters[legacy] = pkg

    def register_variant(self, variant_id: str, platform_id: str) -> None:
        self._variants[normalize_variant_id(variant_id)] = normalize_platform_id(platform_id)
        self._alias[normalize_variant_id(variant_id)] = normalize_platform_id(platform_id)

    def resolve(self, platform_id: str) -> str:
        key = platform_id.strip().lower()
        if key in self._alias:
            target = self._alias[key]
            # Alias may point at cluster id — resolve to platform
            return CLUSTER_TO_PLATFORM.get(target, target)
        if key in self._variants:
            return self._variants[key]
        return normalize_platform_id(platform_id)

    def get(self, platform_id: str) -> PlatformPackage:
        pid = self.resolve(platform_id)
        try:
            return self._platforms[pid]
        except KeyError as exc:
            raise KeyError(f"unknown platform: {platform_id}") from exc

    def get_cluster(self, cluster_id: str) -> PlatformPackage:
        key = cluster_id.strip().lower()
        if key in self._clusters:
            return self._clusters[key]
        try:
            cid = normalize_cluster_id(cluster_id)
            if cid in self._clusters:
                return self._clusters[cid]
        except Exception:  # noqa: BLE001
            pass
        return self.get(cluster_id)

    def list_platforms(self) -> list[PlatformPackage]:
        return sorted(self._platforms.values(), key=lambda p: p.platform_id)

    def list_clusters(self) -> list[tuple[str, PlatformPackage]]:
        return sorted(
            ((c.cluster.cluster_id, c) for c in self._platforms.values() if c.cluster),
            key=lambda t: t[0],
        )

    def platforms_for_signal(self, signal: str) -> list[tuple[PlatformPackage, SignalEncoding]]:
        out: list[tuple[PlatformPackage, SignalEncoding]] = []
        for pkg in self.list_platforms():
            enc = pkg.signal_map().get(signal)
            if enc is not None:
                out.append((pkg, enc))
        return out

    def all_signal_names(self) -> set[str]:
        names: set[str] = set()
        for pkg in self._platforms.values():
            names.update(s.signal for s in pkg.signals)
        return names

    def to_dict(self) -> dict[str, Any]:
        platforms = []
        for pkg in self.list_platforms():
            platforms.append(
                {
                    "platform_id": pkg.platform_id,
                    "manufacturer": pkg.vehicle.manufacturer,
                    "model": pkg.vehicle.model,
                    "generation": pkg.vehicle.generation,
                    "years": {
                        "start": pkg.vehicle.years_start,
                        "end": pkg.vehicle.years_end,
                    },
                    "roles": pkg.vehicle.roles,
                    "aliases": pkg.vehicle.aliases,
                    "physical_validation": pkg.vehicle.physical_validation,
                    "buses": [
                        {
                            "id": b.bus_id,
                            "manufacturer_name": b.manufacturer_name,
                            "bitrate": b.bitrate,
                            "confidence": b.confidence.value,
                        }
                        for b in pkg.buses
                    ],
                    "modules": [
                        {
                            "module_id": m.module_id,
                            "display_name": m.display_name,
                            "bus": m.bus,
                            "confidence": m.confidence.value,
                        }
                        for m in pkg.modules
                    ],
                    "messages": [
                        {
                            "arbitration_id": m.arbitration_id,
                            "name": m.name,
                            "bus": m.bus,
                            "period_ms": m.period_ms,
                            "confidence": m.confidence.value,
                        }
                        for m in pkg.messages
                    ],
                    "signals": [
                        {
                            "signal": s.signal,
                            "arbitration_id": s.arbitration_id,
                            "bus": s.bus,
                            "confidence": s.confidence.value,
                            "physical_validation": s.physical_validation,
                        }
                        for s in pkg.signals
                    ],
                    "cluster": None
                    if pkg.cluster is None
                    else {
                        "cluster_id": pkg.cluster.cluster_id,
                        "compatibility_status": pkg.cluster.compatibility_status,
                        "display_type": pkg.cluster.display_type,
                    },
                    "conflicts": pkg.conflicts,
                    "path": str(pkg.root) if pkg.root else None,
                }
            )
        return {"version": 3, "id_style": "dotted", "platforms": platforms}


_GLOBAL: ProtocolRegistry | None = None


def get_registry(*, reload: bool = False) -> ProtocolRegistry:
    global _GLOBAL
    if _GLOBAL is None or reload:
        reg = ProtocolRegistry()
        reg.load_all()
        # Built-in variant registration
        reg.register_variant("honda.civic.gen8.us.r18.auto", "honda.civic.gen8.us")
        reg.register_variant("honda:civic:8:r18:auto", "honda.civic.gen8.us")
        _GLOBAL = reg
    return _GLOBAL


def iter_signal_implementations(signal: str) -> Iterable[tuple[str, SignalEncoding]]:
    reg = get_registry()
    for pkg, enc in reg.platforms_for_signal(signal):
        yield pkg.platform_id, enc
