"""Phase 2/3 registry, planner, compiler, gating, multi-target tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from opendashcan.adaptation.compiler import AdapterStatus, build_adapter
from opendashcan.adaptation.gating import EmissionDecision, EncodeMode, signal_emittable
from opendashcan.adaptation.planner import plan
from opendashcan.adaptation.scheduler import schedule_from_package
from opendashcan.adaptation.virtual_cluster import VirtualCluster, run_software_validation
from opendashcan.core.state import Confidence, SignalValue, Validity, VehicleState
from opendashcan.protocols.honda.civic10.encoder import Civic10Encoder
from opendashcan.registry import get_decoder, get_encoder, get_registry
from opendashcan.registry.ids import adapter_id, normalize_cluster_id, normalize_platform_id
from opendashcan.registry.loader import discover_package_dirs

FIXTURES = Path(__file__).parent / "fixtures"


def test_normalize_dotted_and_legacy() -> None:
    assert normalize_platform_id("honda.civic.gen8.us") == "honda.civic.gen8.us"
    assert normalize_platform_id("honda_civic_8th_gen") == "honda.civic.gen8.us"
    assert normalize_platform_id("honda:civic:8") == "honda.civic.gen8.us"
    assert normalize_platform_id("honda-civic8") == "honda.civic.gen8.us"
    assert normalize_cluster_id("honda:civic:10:digital") == "honda.civic.gen10.cluster.digital"
    aid = adapter_id("honda.civic.gen8.us.r18.auto", "honda.civic.gen10.cluster.digital")
    assert aid == ("honda.civic.gen8.us.r18.auto__to__honda.civic.gen10.cluster.digital")


def test_registry_discovers_us_packages() -> None:
    dirs = discover_package_dirs()
    assert any(p.name == "us" and "civic" in str(p) and "gen8" in str(p) for p in dirs)
    reg = get_registry(reload=True)
    platforms = {p.platform_id for p in reg.list_platforms()}
    assert "honda.civic.gen7.us" in platforms
    assert "honda.civic.gen8.us" in platforms
    assert "honda.civic.gen10.us" in platforms
    assert "honda.civic.gen11.us" in platforms
    assert "honda.accord.gen11.us" in platforms
    assert "honda.crv.gen6.us" in platforms
    assert "honda.pilot.gen4.us" in platforms
    assert "honda.accord.gen10.us" in platforms
    assert "honda.crv.gen5.us" in platforms
    assert "honda.fit.gen3.us" in platforms
    assert "honda.insight.gen3.us" in platforms
    assert "honda.odyssey.gen5.us" in platforms
    assert "honda.element.gen1.us" in platforms
    # Prefer us/ — no duplicate year-range registration for same id
    assert len([p for p in reg.list_platforms() if p.platform_id == "honda.civic.gen8.us"]) == 1


def test_legacy_aliases_resolve() -> None:
    reg = get_registry(reload=True)
    assert reg.get("honda_civic_8th_gen").platform_id == "honda.civic.gen8.us"
    assert reg.get("honda:civic:8").platform_id == "honda.civic.gen8.us"
    assert reg.get_cluster("honda:civic:10:digital").platform_id == "honda.civic.gen10.us"
    assert reg.get_cluster("honda.civic.gen10.cluster.digital").cluster is not None


def test_vehicle_state_namespaced_store() -> None:
    state = VehicleState()
    state.set(
        "powertrain.engine_rpm",
        2400.0,
        unit="rpm",
        confidence=Confidence.INFERRED,
        validity=Validity.VALID,
        source_vehicle="honda.civic.gen8.us",
        source_bus="f_can",
    )
    assert state.engine_rpm.value == 2400.0
    got = state.get("powertrain.engine_rpm")
    assert got.value == 2400.0
    assert got.source_vehicle == "honda.civic.gen8.us"
    # UNKNOWN never coerced
    assert state.get("fuel.level").value is None
    assert state.get("fuel.level").confidence == Confidence.UNKNOWN


def test_encode_mode_no_output_default() -> None:
    enc = Civic10Encoder()
    assert enc.encode_mode == EncodeMode.NO_OUTPUT
    state = VehicleState()
    state.engine_rpm = SignalValue(2000.0, confidence=Confidence.INFERRED, validity=Validity.VALID)
    assert enc.encode(state) == []
    assert enc.last_output_kind().value == "NO_OUTPUT"


def test_encode_mode_synthetic() -> None:
    enc = Civic10Encoder(encode_mode=EncodeMode.SYNTHETIC)
    state = VehicleState()
    state.engine_rpm = SignalValue(2000.0, confidence=Confidence.INFERRED, validity=Validity.VALID)
    state.vehicle_speed = SignalValue(50.0, confidence=Confidence.INFERRED, validity=Validity.VALID)
    frames = enc.encode(state, timestamp=1.0)
    assert len(frames) == 2
    assert frames[0].meta.get("output_kind") == "SYNTHETIC"
    assert enc.last_output_kind().value == "SYNTHETIC"


def test_gating_blocks_unknown_in_production() -> None:
    sig = SignalValue(None, confidence=Confidence.UNKNOWN)
    assert signal_emittable(sig, EncodeMode.PRODUCTION) == EmissionDecision.BLOCK_UNKNOWN_VALUE
    sig2 = SignalValue(1.0, confidence=Confidence.INFERRED)
    assert signal_emittable(sig2, EncodeMode.PRODUCTION) == EmissionDecision.BLOCK_LOW_CONFIDENCE


def test_multi_target_encoders_from_one_decoder() -> None:
    decoder = get_decoder("honda.civic.gen8.us.r18.auto")
    state = VehicleState()
    # Decoder does not invent
    from opendashcan.core.frame import CANFrame

    out = decoder.decode_frame(CANFrame(0x694, b"\x00" * 8, 0.0), state)
    assert out.engine_rpm.value is None

    for target in (
        "honda.civic.gen10.cluster.digital",
        "honda.civic.gen11.cluster.digital",
        "honda.accord.gen10.cluster.digital",
        "honda.crv.gen5.cluster.digital",
    ):
        enc = get_encoder(target)
        assert enc.encode(out) == []


def test_planner_civic8_to_civic10() -> None:
    p = plan("honda.civic.gen8.us.r18.auto", "honda.civic.gen10.cluster.digital")
    assert p.mode == "DOCUMENTATION_ONLY"
    assert p.cluster_id == "honda.civic.gen10.cluster.digital"
    assert p.rows
    text = p.format_text()
    assert "DOCUMENTATION_ONLY" in text
    assert "READINESS" in text


def test_compiler_documentation_only_partial() -> None:
    out = build_adapter(
        "honda.civic.gen8.us.r18.auto",
        "honda.civic.gen10.cluster.digital",
        documentation_only=True,
    )
    manifest = json.loads((out / "adapter_manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "DOCUMENTATION_ONLY"
    assert manifest["status"] in {
        AdapterStatus.PARTIAL.value,
        AdapterStatus.BLOCKED.value,
    }
    # Civic8→Civic10 has documented target layouts → PARTIAL foundation
    assert manifest["status"] == AdapterStatus.PARTIAL.value
    assert (out / "unknowns.json").is_file()
    assert (out / "status.json").is_file()


def test_virtual_cluster_software_only() -> None:
    enc = Civic10Encoder(encode_mode=EncodeMode.SYNTHETIC)
    state = VehicleState()
    state.engine_rpm = SignalValue(1500.0, confidence=Confidence.INFERRED, validity=Validity.VALID)
    state.vehicle_speed = SignalValue(40.0, confidence=Confidence.INFERRED, validity=Validity.VALID)
    frames = enc.encode(state, timestamp=0.0)
    vc = VirtualCluster(cluster_id="honda.civic.gen10.cluster.digital")
    summary = run_software_validation(vc, frames)
    assert summary["label"] == "SOFTWARE VALIDATION ONLY"
    assert summary["hardware_compatibility_claimed"] is False
    assert summary["rpm"] == 1500.0


def test_scheduler_from_package() -> None:
    pkg = get_registry().get("honda.civic.gen10.us")
    sched = schedule_from_package(pkg)
    assert sched.mode == "DOCUMENTATION_ONLY"
    assert any(m.name == "ENGINE_DATA" for m in sched.messages)


def test_cli_smoke_registry_and_plan(capsys: pytest.CaptureFixture[str]) -> None:
    from opendashcan.cli import main

    with pytest.raises(SystemExit) as e:
        main(["registry", "vehicles"])
    assert e.value.code == 0
    out = capsys.readouterr().out
    assert "honda.civic.gen8.us" in out

    with pytest.raises(SystemExit) as e2:
        main(
            [
                "plan",
                "honda.civic.gen8.us.r18.auto",
                "honda.civic.gen10.cluster.digital",
            ]
        )
    assert e2.value.code == 0
    assert "DOCUMENTATION_ONLY" in capsys.readouterr().out
