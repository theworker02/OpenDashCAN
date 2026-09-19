"""Phase-1 vehicle / decoder / encoder discovery API."""

from __future__ import annotations

from dataclasses import dataclass

from opendashcan.core.decoder import VehicleDecoder
from opendashcan.core.encoder import ClusterEncoder
from opendashcan.protocols.honda.civic8 import Civic8VehicleDecoder
from opendashcan.protocols.honda.civic10 import Civic10Encoder, Civic10VehicleDecoder
from opendashcan.protocols.honda.stubs import accord10_encoder, civic11_encoder, crv5_encoder
from opendashcan.registry.ids import LEGACY_ALIASES, normalize_cluster_id, normalize_platform_id


@dataclass(frozen=True)
class VehicleInfo:
    vehicle_id: str
    display_name: str
    role: str
    years: str
    notes: str


VEHICLES: dict[str, VehicleInfo] = {
    "honda_civic_8th_gen": VehicleInfo(
        vehicle_id="honda_civic_8th_gen",
        display_name="Honda Civic 8th gen (FA/FG)",
        role="source",
        years="2006-2011",
        notes="F-CAN source decoder - encodings largely UNKNOWN; community IDs tracked only.",
    ),
    "honda_civic_10th_gen": VehicleInfo(
        vehicle_id="honda_civic_10th_gen",
        display_name="Honda Civic 10th gen cluster/PCM subset",
        role="target",
        years="2016-2021",
        notes="opendbc-mapped encoder subset - no physical cluster compatibility claim.",
    ),
    "honda-civic8": VehicleInfo(
        vehicle_id="honda-civic8",
        display_name="Honda Civic 8th gen (FA/FG)",
        role="source",
        years="2006-2011",
        notes="Primary id for honda_civic_8th_gen decoder.",
    ),
    "honda-civic10": VehicleInfo(
        vehicle_id="honda-civic10",
        display_name="Honda Civic 10th gen cluster/PCM subset",
        role="target",
        years="2016-2021",
        notes="Primary id for honda_civic_10th_gen encoder (SYNTHETIC research frames only).",
    ),
    "honda.civic.gen8.us": VehicleInfo(
        vehicle_id="honda.civic.gen8.us",
        display_name="Honda Civic 8th gen US (FA/FG)",
        role="source",
        years="2006-2011",
        notes="Canonical dotted platform id for Civic 8 US.",
    ),
    "honda.civic.gen10.us": VehicleInfo(
        vehicle_id="honda.civic.gen10.us",
        display_name="Honda Civic 10th gen US",
        role="target",
        years="2016-2021",
        notes="Canonical dotted platform id for Civic 10 US / digital cluster.",
    ),
    "honda:civic:8": VehicleInfo(
        vehicle_id="honda:civic:8",
        display_name="Honda Civic 8th gen (FA/FG)",
        role="source",
        years="2006-2011",
        notes="Legacy colon alias for honda.civic.gen8.us.",
    ),
    "honda:civic:10": VehicleInfo(
        vehicle_id="honda:civic:10",
        display_name="Honda Civic 10th gen cluster/PCM subset",
        role="target",
        years="2016-2021",
        notes="Legacy colon alias for honda.civic.gen10.us.",
    ),
}

_DECODER_ALIASES: dict[str, str] = {
    "honda_civic_8th_gen": "honda_civic_8th_gen",
    "honda-civic8": "honda_civic_8th_gen",
    "honda:civic:8": "honda_civic_8th_gen",
    "honda:civic:8:r18:auto": "honda_civic_8th_gen",
    "honda.civic.gen8.us": "honda_civic_8th_gen",
    "honda.civic.gen8.us.r18.auto": "honda_civic_8th_gen",
    "honda_civic_10th_gen": "civic10",
    "honda-civic10": "civic10",
    "honda:civic:10": "civic10",
    "honda.civic.gen10.us": "civic10",
}

_ENCODER_ALIASES: dict[str, str] = {
    "honda_civic_10th_gen": "civic10",
    "honda-civic10": "civic10",
    "honda:civic:10": "civic10",
    "honda:civic:10:digital": "civic10",
    "honda.civic.gen10.us": "civic10",
    "honda.civic.gen10.cluster.digital": "civic10",
    "honda:civic:11:digital": "civic11",
    "honda.civic.gen11.us": "civic11",
    "honda.civic.gen11.cluster.digital": "civic11",
    "honda:accord:10:digital": "accord10",
    "honda.accord.gen10.us": "accord10",
    "honda.accord.gen10.cluster.digital": "accord10",
    "honda:crv:5:digital": "crv5",
    "honda.crv.gen5.us": "crv5",
    "honda.crv.gen5.cluster.digital": "crv5",
}


def _resolve_decoder_key(vehicle_id: str) -> str:
    if vehicle_id in _DECODER_ALIASES:
        return _DECODER_ALIASES[vehicle_id]
    # Try legacy map / normalize
    if vehicle_id in LEGACY_ALIASES:
        canon = LEGACY_ALIASES[vehicle_id]
        return _DECODER_ALIASES.get(canon, vehicle_id)
    try:
        pid = normalize_platform_id(vehicle_id)
        return _DECODER_ALIASES.get(pid, vehicle_id)
    except KeyError:
        return vehicle_id


def _resolve_encoder_key(cluster_id: str) -> str:
    if cluster_id in _ENCODER_ALIASES:
        return _ENCODER_ALIASES[cluster_id]
    if cluster_id in LEGACY_ALIASES:
        canon = LEGACY_ALIASES[cluster_id]
        return _ENCODER_ALIASES.get(canon, cluster_id)
    try:
        cid = normalize_cluster_id(cluster_id)
        via_cluster = _ENCODER_ALIASES.get(cid)
        if via_cluster:
            return via_cluster
        return _ENCODER_ALIASES.get(normalize_platform_id(cluster_id), cluster_id)
    except KeyError:
        return cluster_id


def get_decoder(vehicle_id: str) -> VehicleDecoder:
    key = _resolve_decoder_key(vehicle_id)
    if key == "honda_civic_8th_gen":
        return Civic8VehicleDecoder()
    if key == "civic10":
        return Civic10VehicleDecoder()
    raise KeyError(f"no decoder for {vehicle_id!r}")


def get_encoder(cluster_id: str, *, emit_synthetic_research: bool = False) -> ClusterEncoder:
    key = _resolve_encoder_key(cluster_id)
    if key == "civic10":
        return Civic10Encoder(emit_synthetic_research=emit_synthetic_research)
    if key == "civic11":
        return civic11_encoder()
    if key == "accord10":
        return accord10_encoder()
    if key == "crv5":
        return crv5_encoder()
    raise KeyError(f"no encoder for {cluster_id!r}")
