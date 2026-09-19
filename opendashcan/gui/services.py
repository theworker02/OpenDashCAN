"""Data helpers for the GUI — registry, plans, gaps, research paths.

No Qt imports here so smoke tests can run without a display or PySide6.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_SOURCE = "honda.civic.gen8.us.r18.auto"
DEFAULT_CLUSTER = "honda.civic.gen10.cluster.digital"
DEFAULT_LISTEN_VEHICLE = "honda.civic.gen10.us"

EVIDENCE_SUBMISSION_URL = (
    "https://github.com/theworker02/OpenDashCAN/issues/new"
    "?template=evidence_submission.yml"
)
EVIDENCE_GUIDE_REL = "docs/submitting-evidence.md"

DBC_INDEX_DIR = REPO_ROOT / "dbc" / "opendbc" / "index"

RESEARCH_REPORTS: tuple[tuple[str, str], ...] = (
    ("Honda adaptation report", "HONDA_ADAPTATION_REPORT.md"),
    ("Donor protocol report", "research/DONOR_PROTOCOL_REPORT.md"),
    ("Cluster CAN evidence", "research/CLUSTER_CAN_EVIDENCE.md"),
    ("2009–2022 Honda CAN research", "research/honda_2009_2022_can_research.md"),
    ("Research index", "research/README.md"),
    ("Civic8→Civic10 adaptation notes", "docs/adaptations/civic8_r18_auto_to_civic10.md"),
    ("Evidence policy", "docs/evidence-policy.md"),
    ("Submitting evidence guide", "docs/submitting-evidence.md"),
)


@dataclass(frozen=True)
class PlatformRow:
    platform_id: str
    display: str
    roles: str
    years: str
    kind: str  # "platform" | "cluster"
    cluster_id: str | None = None
    status: str | None = None


@dataclass(frozen=True)
class SignalHit:
    platform_id: str
    signal: str
    arbitration_id: str
    confidence: str
    notes: str


@dataclass(frozen=True)
class MessageHit:
    platform_id: str
    name: str
    arbitration_id: str
    confidence: str
    period_ms: str


@dataclass(frozen=True)
class DbcHit:
    taxonomy: str
    vehicle_id: str
    message: str
    arbitration_id: str
    dbc_signal: str
    knowledge_level: str
    source_dbc: str


@dataclass(frozen=True)
class ResearchDoc:
    title: str
    path: Path
    exists: bool


def _registry():
    from opendashcan.registry import get_registry

    return get_registry()


def list_browser_rows() -> list[PlatformRow]:
    """Platform + cluster entries for the left browser."""
    reg = _registry()
    rows: list[PlatformRow] = []
    for pkg in reg.list_platforms():
        v = pkg.vehicle
        years = f"{v.years_start or '?'}-{v.years_end or '?'}"
        rows.append(
            PlatformRow(
                platform_id=pkg.platform_id,
                display=f"{v.manufacturer} {v.model} gen{v.generation}",
                roles=",".join(v.roles) if v.roles else "source",
                years=years,
                kind="platform",
            )
        )
    for cid, pkg in reg.list_clusters():
        c = pkg.cluster
        assert c is not None
        years = f"{c.years_start or '?'}-{c.years_end or '?'}"
        rows.append(
            PlatformRow(
                platform_id=pkg.platform_id,
                display=f"Cluster: {cid}",
                roles="cluster",
                years=years,
                kind="cluster",
                cluster_id=cid,
                status=c.compatibility_status,
            )
        )
    return rows


def platform_detail(platform_id: str) -> dict[str, Any]:
    pkg = _registry().get(platform_id)
    v = pkg.vehicle
    detail: dict[str, Any] = {
        "platform_id": pkg.platform_id,
        "manufacturer": v.manufacturer,
        "model": v.model,
        "generation": v.generation,
        "years": f"{v.years_start}-{v.years_end}",
        "roles": list(v.roles),
        "physical_validation": v.physical_validation,
        "research_active": v.research_active,
        "buses": [
            {
                "id": b.bus_id,
                "name": b.manufacturer_name or b.bus_id,
                "bitrate": b.bitrate,
                "confidence": b.confidence.value,
            }
            for b in pkg.buses
        ],
        "message_count": len(pkg.messages),
        "signal_count": len(pkg.signals),
        "module_count": len(pkg.modules),
        "mode": "DOCUMENTATION_ONLY",
    }
    if pkg.cluster is not None:
        c = pkg.cluster
        detail["cluster"] = {
            "cluster_id": c.cluster_id,
            "display_type": c.display_type,
            "compatibility_status": c.compatibility_status,
            "requirements": len(pkg.requirements),
        }
    return detail


def _aid_str(aid: str | int | None) -> str:
    if aid is None:
        return "UNKNOWN"
    if isinstance(aid, int):
        return f"0x{aid:X}"
    return str(aid)


def lookup_signals(query: str) -> list[SignalHit]:
    """Find signals by name substring or exact taxonomy path."""
    q = query.strip().lower()
    if not q:
        return []
    hits: list[SignalHit] = []
    for pkg in _registry().list_platforms():
        for sig in pkg.signals:
            name = sig.signal
            msg_name = sig.message_name or ""
            if q not in name.lower() and q not in msg_name.lower():
                continue
            hits.append(
                SignalHit(
                    platform_id=pkg.platform_id,
                    signal=name,
                    arbitration_id=_aid_str(sig.arbitration_id),
                    confidence=sig.confidence.value,
                    notes=(sig.notes or "")[:120],
                )
            )
    return hits


def lookup_messages(query: str) -> list[MessageHit]:
    q = query.strip().lower()
    if not q:
        return []
    hits: list[MessageHit] = []
    for pkg in _registry().list_platforms():
        for msg in pkg.messages:
            name = msg.name or ""
            aid_s = _aid_str(msg.arbitration_id)
            if q not in name.lower() and q not in aid_s.lower():
                continue
            hits.append(
                MessageHit(
                    platform_id=pkg.platform_id,
                    name=name or "(unnamed)",
                    arbitration_id=aid_s,
                    confidence=msg.confidence.value,
                    period_ms=str(msg.period_ms if msg.period_ms is not None else "UNKNOWN"),
                )
            )
    return hits


def lookup_dbc_index(query: str, *, index_dir: Path | None = None) -> list[DbcHit]:
    """Search imported opendbc taxonomy index (DOCUMENTATION_ONLY — not cluster RX)."""
    q = query.strip().lower()
    if not q:
        return []
    root = index_dir or DBC_INDEX_DIR
    if not root.is_dir():
        return []
    try:
        from opendashcan.dbc import taxonomy_implementations_from_imports
    except Exception:  # noqa: BLE001
        return []
    try:
        cross = taxonomy_implementations_from_imports(root)
    except Exception:  # noqa: BLE001
        return []
    hits: list[DbcHit] = []
    for tax, rows in cross.items():
        tax_l = tax.lower()
        for row in rows:
            dbc_sig = str(row.get("dbc_signal") or "")
            msg = str(row.get("message") or "")
            aid = str(row.get("arbitration_id") or "")
            hay = " ".join((tax_l, dbc_sig.lower(), msg.lower(), aid.lower()))
            if q not in hay and q not in tax_l:
                continue
            hits.append(
                DbcHit(
                    taxonomy=tax,
                    vehicle_id=str(row.get("vehicle_id") or ""),
                    message=msg,
                    arbitration_id=aid,
                    dbc_signal=dbc_sig,
                    knowledge_level=str(row.get("knowledge_level") or "DOCUMENTED"),
                    source_dbc=str(row.get("source_dbc") or ""),
                )
            )
            if len(hits) >= 200:
                return hits
    return hits


def _phase4_gaps(cluster_id: str) -> dict[str, Any] | None:
    """Use Phase 4 ``cluster.gaps`` / env loader APIs when present."""
    phase4_err: str | None = None
    try:
        gaps_mod = importlib.import_module("opendashcan.cluster.gaps")
        build = getattr(gaps_mod, "build_gap_report", None)
        fmt = getattr(gaps_mod, "format_gaps_text", None)
        if callable(build):
            report = build(cluster_id)
            if isinstance(report, dict):
                report = dict(report)
                report.setdefault("source", "phase4.gaps")
                report.setdefault("label", "DOCUMENTATION_ONLY")
                if callable(fmt):
                    try:
                        report["text"] = fmt(report)
                    except Exception as exc:  # noqa: BLE001
                        report["format_note"] = str(exc)
                return report
    except Exception as exc:  # noqa: BLE001
        phase4_err = str(exc)

    try:
        env_mod = importlib.import_module("opendashcan.cluster.environment_loader")
    except ImportError:
        if phase4_err is None:
            return None
        return {
            "source": "phase4",
            "error": phase4_err,
            "label": "DOCUMENTATION_ONLY",
        }
    load_fn = getattr(env_mod, "load_cluster_env", None)
    if load_fn is None:
        return None
    try:
        env = load_fn(cluster_id)
    except Exception as exc:  # noqa: BLE001
        return {
            "source": "phase4",
            "error": str(exc),
            "label": "DOCUMENTATION_ONLY",
        }
    data: dict[str, Any] = {
        "source": "phase4.environment_loader",
        "cluster_id": getattr(env, "cluster_id", cluster_id),
        "label": "DOCUMENTATION_ONLY",
        "key": getattr(env, "key", None),
        "platform_id": getattr(env, "platform_id", None),
        "requirements": list(env.requirement_rows()) if hasattr(env, "requirement_rows") else {},
        "rx_messages": list(env.rx_rows()) if hasattr(env, "rx_rows") else {},
    }
    if phase4_err:
        data["gaps_module_note"] = phase4_err
    return data


def cluster_gaps(cluster_id: str = DEFAULT_CLUSTER) -> dict[str, Any]:
    """Cluster gaps view — Phase 4 when available, else registry environment."""
    phase4 = _phase4_gaps(cluster_id)
    if phase4 is not None and "error" not in phase4:
        return phase4

    try:
        from opendashcan.adaptation.environment import ClusterEnvironment
    except Exception as exc:  # noqa: BLE001
        return {
            "cluster_id": cluster_id,
            "source": "error",
            "error": f"adaptation.environment unavailable: {exc}",
            "label": "DOCUMENTATION_ONLY",
            "unknowns": [],
            "rows": [],
        }

    try:
        pkg = _registry().get_cluster(cluster_id)
        env = ClusterEnvironment.from_package(pkg)
        report = env.gap_report()
        report["source"] = "adaptation.environment"
        if phase4 and "error" in phase4:
            report["phase4_note"] = phase4["error"]
        return report
    except Exception as exc:  # noqa: BLE001
        return {
            "cluster_id": cluster_id,
            "source": "error",
            "error": str(exc),
            "label": "DOCUMENTATION_ONLY",
            "unknowns": [],
            "rows": [],
        }


def gap_table_rows(report: dict[str, Any]) -> list[list[str]]:
    """Flatten Phase 4 gap rows for a QTableWidget (DOCUMENTATION_ONLY labels)."""
    rows_out: list[list[str]] = []
    raw = report.get("rows")
    if not isinstance(raw, list):
        return rows_out
    for item in raw:
        if not isinstance(item, dict):
            continue
        axes = item.get("axes") or {}
        overall = str(item.get("overall") or item.get("status") or "")
        signal = str(item.get("signal") or item.get("taxonomy") or "")
        # Prefer axis B (donor encoding) + E (cluster RX) when present
        donor = ""
        rx = ""
        if isinstance(axes, dict):
            b = axes.get("B") or {}
            e = axes.get("E") or {}
            if isinstance(b, dict):
                donor = str(b.get("status") or "")
            if isinstance(e, dict):
                rx = str(e.get("status") or "")
        note = str(item.get("notes") or item.get("note") or "")[:80]
        rows_out.append([signal, overall, donor, rx, note])
        if len(rows_out) >= 500:
            break
    return rows_out


def adaptation_plan(
    source: str = DEFAULT_SOURCE,
    cluster: str = DEFAULT_CLUSTER,
) -> dict[str, Any]:
    from opendashcan.adaptation.planner import plan

    adaptation = plan(source, cluster)
    return {
        "text": adaptation.format_text(),
        "dict": adaptation.to_dict(),
        "mode": adaptation.mode,
        "source_id": adaptation.source_id,
        "cluster_id": adaptation.cluster_id,
        "readiness_summary": adaptation.readiness_summary(),
        "physical_compatibility": adaptation.physical_compatibility,
        "electrical_compatibility": adaptation.electrical_compatibility,
        "protocol_compatibility": adaptation.protocol_compatibility,
    }


def research_docs(root: Path | None = None) -> list[ResearchDoc]:
    base = root or REPO_ROOT
    docs: list[ResearchDoc] = []
    for title, rel in RESEARCH_REPORTS:
        path = base / rel
        docs.append(ResearchDoc(title=title, path=path, exists=path.is_file()))
    return docs


def project_mode_banner() -> str:
    return (
        "OpenDashCAN Desktop — DOCUMENTATION_ONLY / LISTEN_ONLY. "
        "PC-side OBD/CAN sniff → decode → VehicleState. "
        "NOT a website · NOT an ECU flash tool · NO physical CAN TX by default."
    )


AFFILIATION_DISCLAIMER = (
    "Not affiliated with, endorsed by, or sponsored by Honda Motor Co., Ltd."
)

TRADEMARK_NOTICE = (
    "Honda®, the Honda logo, and related marks are trademarks and/or "
    "copyrighted works of Honda Motor Co., Ltd. All rights reserved. "
    "OpenDashCAN does not claim ownership of those marks."
)


@dataclass(frozen=True)
class WiringChecklistItem:
    interface: str
    meaning: str
    status: str
    confidence: str


WIRING_CHECKLIST: tuple[WiringChecklistItem, ...] = (
    WiringChecklistItem(
        "Power (+12V / ACC)",
        "Cluster supply rails — fused; exact pins unknown",
        "Must match donor rails",
        "REQUIRES_BENCH",
    ),
    WiringChecklistItem(
        "Ground",
        "Chassis / signal grounds",
        "Required",
        "REQUIRES_BENCH",
    ),
    WiringChecklistItem(
        "CAN-H / CAN-L",
        "High-speed bus to cluster / gateway",
        "F-CAN role known; cluster RX unknown",
        "DOCUMENTED / UNKNOWN",
    ),
    WiringChecklistItem(
        "Ignition sense",
        "Key/IG wake line for gauges",
        "Often required",
        "UNKNOWN",
    ),
    WiringChecklistItem(
        "Illumination / dimmer",
        "Night brightness input",
        "Common cluster input",
        "UNKNOWN",
    ),
    WiringChecklistItem(
        "Speakers / chimes",
        "Warning audio path",
        "May be off-CAN",
        "UNKNOWN",
    ),
    WiringChecklistItem(
        "Immobilizer / gateway",
        "Security / network gateway",
        "Dual-bus / MICU",
        "UNKNOWN / REQUIRES_BENCH",
    ),
    WiringChecklistItem(
        "ABS / steering-angle feeds",
        "Extra IDs some digital clusters expect",
        "Vehicle-bus documented; RX unconfirmed",
        "DOCUMENTED / UNKNOWN",
    ),
)

WIRING_DIAGRAMS: tuple[tuple[str, str], ...] = (
    ("OBD listen path (LISTEN_ONLY)", "assets/wiring/01_obd_listen_path.png"),
    ("Dual-bus bridge (FUTURE / NO TX)", "assets/wiring/02_dual_bus_future.png"),
    ("Harness interfaces checklist", "assets/wiring/03_harness_interfaces.png"),
)

WIRING_DOCS: tuple[tuple[str, str], ...] = (
    ("Wiring index", "docs/wiring/README.md"),
    ("OBD-II listen tap", "docs/wiring/obd_listen_tap.md"),
    ("Bus roles (F-CAN / B-CAN)", "docs/wiring/bus_roles.md"),
    ("Cluster swap checklist", "docs/wiring/cluster_swap_checklist.md"),
    ("Pi recorder design", "hardware/can_recorder_rpi/README.md"),
)


def wiring_checklist() -> list[WiringChecklistItem]:
    return list(WIRING_CHECKLIST)


def wiring_diagram_paths(root: Path | None = None) -> list[tuple[str, Path, bool]]:
    base = root or REPO_ROOT
    out: list[tuple[str, Path, bool]] = []
    for title, rel in WIRING_DIAGRAMS:
        path = base / rel
        out.append((title, path, path.is_file()))
    return out


def wiring_docs(root: Path | None = None) -> list[ResearchDoc]:
    base = root or REPO_ROOT
    return [
        ResearchDoc(title=t, path=base / rel, exists=(base / rel).is_file())
        for t, rel in WIRING_DOCS
    ]


def about_text() -> str:
    from opendashcan import __version__

    return (
        f"OpenDashCAN Desktop {__version__}\n\n"
        "Installable Python program (CLI + Qt) for Honda OEM cluster research.\n"
        "Primary mode: PC-side OBD/CAN listen → decode documented layouts → "
        "show VehicleState, ID rates, and cluster gaps.\n\n"
        f"{AFFILIATION_DISCLAIMER}\n"
        f"{TRADEMARK_NOTICE}\n"
        "See docs/TRADEMARKS.md. Boot splash is Honda-themed; official logo "
        "files are not shipped in this repository.\n\n"
        "This is NOT a website.\n"
        "This is NOT an ECU flash / reprogramming tool.\n"
        "This does NOT auto-transmit to the vehicle or cluster.\n"
        "Wiring docs are NOT OEM service instructions.\n\n"
        "Default safety: LinkMode.LISTEN_ONLY / EncodeMode.NO_OUTPUT.\n"
        "Decode only registered layouts (e.g. Civic10VehicleDecoder).\n"
        "No claim of cluster control or physical compatibility.\n\n"
        "Get frames onto the PC: hardware/can_recorder_rpi/\n"
        "Wiring: docs/wiring/  ·  GUI Wiring tab\n"
        "Install: pip install -e \".[gui,hw]\"\n"
        "Listen:  opendashcan listen --virtual\n"
        f"Evidence: {EVIDENCE_SUBMISSION_URL}"
    )


def gui_missing_deps_message() -> str:
    """Clear install hint when GUI or hw extras are missing."""
    parts: list[str] = []
    try:
        import PySide6  # noqa: F401
    except ImportError:
        parts.append('PySide6 missing — install:  pip install -e ".[gui]"')
    try:
        import can  # noqa: F401
    except ImportError:
        parts.append(
            'python-can missing — live interfaces need:  pip install -e ".[hw]"\n'
            "  (Virtual / Play file still work without python-can.)"
        )
    if not parts:
        return ""
    return "\n\n".join(parts) + '\n\nFull desktop:  pip install -e ".[gui,hw]"'


def listen_vehicle_ids() -> list[str]:
    """Decoder ids the Live tab may select (registered layouts only)."""
    return [
        "honda.civic.gen10.us",
        "honda_civic_10th_gen",
        "honda.civic.gen8.us",
        "honda_civic_8th_gen",
    ]


def run_virtual_listen_session(
    *,
    vehicle: str = DEFAULT_LISTEN_VEHICLE,
    max_frames: int = 32,
    capture: Path | None = None,
) -> dict[str, Any]:
    """Headless virtual listen → session summary (no Qt / no display).

    Feeds the same ListenSession path the Live tab uses. LISTEN_ONLY — no TX.
    """
    from opendashcan.hw.listen import resolve_virtual_fixture
    from opendashcan.hw.session import ListenSession
    from opendashcan.registry import get_decoder
    from opendashcan.replay.reader import read_capture

    path = Path(capture) if capture is not None else resolve_virtual_fixture()
    if not path.is_file():
        raise FileNotFoundError(f"Capture not found: {path}")
    decoder = get_decoder(vehicle)
    session = ListenSession(decoder=decoder)
    for i, frame in enumerate(read_capture(path)):
        if i >= max_frames:
            break
        session.ingest(frame)
    id_rows = [
        {
            "arbitration_id": f"{r.arbitration_id:#05x}",
            "count": r.count,
            "rate_hz": r.rate_hz,
            "last_data_hex": r.last_data_hex,
        }
        for r in session.id_rate_rows()
    ]
    return {
        "mode": "LISTEN_ONLY",
        "label": "DOCUMENTATION_ONLY decode — synthetic/offline feed",
        "path": str(path),
        "vehicle": vehicle,
        "frame_count": session.frame_count,
        "id_rows": id_rows,
        "signal_rows": [
            {"name": n, "value": v, "confidence": c, "last_update": t}
            for n, v, c, t in session.signal_rows()
        ],
    }


def confidence_tier(label: str) -> str:
    """Map a confidence / knowledge string to a UI tier: high|mid|low|unknown."""
    u = (label or "").upper()
    if any(
        k in u
        for k in (
            "PHYSICALLY_VERIFIED",
            "VERIFIED",
            "BENCH",
            "DOCUMENTED",
            "SUPPORTED_BY_MULTIPLE",
            "VEHICLE_PROTOCOL",
            "CLUSTER_RELEVANT",
        )
    ):
        if "COMMUNITY" in u or "INFERRED" in u:
            return "mid"
        return "high"
    if any(k in u for k in ("COMMUNITY", "REPORTED", "LIKELY", "PARTIAL")):
        return "mid"
    if any(k in u for k in ("INFERRED", "HEURISTIC")):
        return "low"
    if "UNKNOWN" in u or "ABSENT" in u or not u:
        return "unknown"
    return "mid"
