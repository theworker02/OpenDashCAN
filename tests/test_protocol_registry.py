"""Tests for Phase-2/3 protocol registry."""

from __future__ import annotations

from opendashcan.registry import VEHICLES, get_decoder, get_encoder, get_registry
from opendashcan.registry.loader import normalize_platform_id


def test_phase1_api_still_exported():
    assert "honda_civic_8th_gen" in VEHICLES
    dec = get_decoder("honda_civic_8th_gen")
    assert dec.vehicle_id in ("honda-civic8", "honda_civic_8th_gen")
    enc = get_encoder("honda_civic_10th_gen", emit_synthetic_research=True)
    assert enc.cluster_id  # any non-empty id


def test_civic8_decoder_class_name():
    from opendashcan.protocols.honda.civic8 import Civic8VehicleDecoder

    assert isinstance(get_decoder("honda:civic:8"), Civic8VehicleDecoder)


def test_registry_discovers_platforms():
    reg = get_registry(reload=True)
    ids = {p.platform_id for p in reg.list_platforms()}
    # Canonical dotted ids (colon aliases still resolve via get())
    assert "honda.civic.gen7.us" in ids or "honda:civic:7" in ids
    assert "honda.civic.gen8.us" in ids or "honda:civic:8" in ids
    assert "honda.civic.gen10.us" in ids or "honda:civic:10" in ids
    assert "honda.civic.gen11.us" in ids or "honda:civic:11" in ids
    assert "honda.accord.gen10.us" in ids or "honda:accord:10" in ids
    assert "honda.accord.gen11.us" in ids or "honda:accord:11" in ids
    assert "honda.crv.gen5.us" in ids or "honda:crv:5" in ids
    assert "honda.crv.gen6.us" in ids or "honda:crv:6" in ids
    assert "honda.pilot.gen4.us" in ids or "honda:pilot:4" in ids
    assert "honda.civic.gen9.us" in ids or "honda:civic:9" in ids
    assert "honda.fit.gen3.us" in ids or "honda:fit:3" in ids
    # Colon aliases resolve
    assert reg.get("honda:civic:8").platform_id.endswith("civic.gen8.us") or (
        reg.get("honda:civic:8").platform_id == "honda:civic:8"
    )
    assert reg.get("honda:civic:7").platform_id.endswith("civic.gen7.us")


def test_normalize_aliases():
    assert normalize_platform_id("honda_civic_8th_gen") in (
        "honda:civic:8",
        "honda.civic.gen8.us",
    )
    assert normalize_platform_id("honda:civic:10:digital") in (
        "honda:civic:10",
        "honda.civic.gen10.us",
    )
    # Variant may normalize to base platform or full variant id
    v = normalize_platform_id("honda:civic:8:r18:auto")
    assert "civic" in v and "8" in v.replace("gen8", "8")


def test_civic7_no_fake_can_encodings():
    pkg = get_registry().get("honda:civic:7")
    assert pkg.platform_id == "honda.civic.gen7.us"
    buses = {b.bus_id: b for b in pkg.buses}
    assert buses["obd_kline"].protocol == "ISO9141"
    assert buses["obd_kline"].confidence.value == "DOCUMENTED"
    assert pkg.messages == []
    rpm = pkg.signal_map()["powertrain.engine_rpm"]
    assert rpm.confidence.value == "UNKNOWN"
    assert rpm.arbitration_id is None


def test_latest_canfd_stubs_research_required():
    reg = get_registry()
    for pid in (
        "honda.accord.gen11.us",
        "honda.crv.gen6.us",
        "honda.pilot.gen4.us",
    ):
        pkg = reg.get(pid)
        assert pkg.messages == []
        assert any(b.can_fd for b in pkg.buses)


def test_civic10_opendbc_ids_documented():
    pkg = get_registry().get("honda:civic:10")
    assert pkg.cluster is not None
    assert pkg.cluster.cluster_id in (
        "honda:civic:10:digital",
        "honda.civic.gen10.cluster.digital",
    )
    msgs = {m.name: m for m in pkg.messages}
    assert msgs["ENGINE_DATA"].arbitration_id == "0x158"
    assert msgs["ENGINE_DATA"].confidence.value == "DOCUMENTED"
    assert len(pkg.requirements) >= 1


def test_list_clusters():
    clusters = dict(get_registry().list_clusters())
    assert "honda:civic:10:digital" in clusters or "honda.civic.gen10.cluster.digital" in clusters
