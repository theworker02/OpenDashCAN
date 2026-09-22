"""Phase 4 tests: lineage, gaps CLI, correlate, generate-trace (synthetic)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from opendashcan.adaptation.gating import EncodeMode
from opendashcan.analysis.lineage import build_lineage, compare_encodings
from opendashcan.analysis.similarity import correlate_signal
from opendashcan.cli import build_parser
from opendashcan.cluster.classify import ClusterCandidateClass, classify_message
from opendashcan.cluster.environment_loader import list_cluster_envs, load_cluster_env
from opendashcan.cluster.gaps import build_gap_report
from opendashcan.cluster.trace import generate_trace


def test_cluster_envs_present() -> None:
    keys = list_cluster_envs()
    assert set(keys) >= {"civic10", "civic11", "accord10", "crv5"}
    civic = load_cluster_env("civic10")
    assert civic.platform_id == "honda.civic.gen10.us"
    assert civic.requirement_rows()


def test_classify_never_auto_confirms() -> None:
    # Without confirmed set, 0x158 is LIKELY for civic10 hint only
    c = classify_message(
        arbitration_id=0x158,
        name="ENGINE_DATA",
        platform_hint="honda.civic.gen10.us",
    )
    assert c == ClusterCandidateClass.CLUSTER_LIKELY_RX
    assert c != ClusterCandidateClass.CLUSTER_CONFIRMED_RX
    # Accord must not inherit CivicX LIKELY via missing hint
    c2 = classify_message(
        arbitration_id=0x158,
        name="ENGINE_DATA",
        signal_taxonomies=["powertrain.engine_rpm"],
        platform_hint="honda.accord.gen10.us",
    )
    assert c2 == ClusterCandidateClass.DISPLAY_RELEVANT


def test_lineage_builds() -> None:
    data = build_lineage()
    assert data["message_instances"] > 0
    assert data["unique_ids"] > 0
    # ENGINE_DATA 0x158 should appear
    ids = {g["id_dec"] for g in data["id_groups"]}
    assert 0x158 in ids
    a = {
        "id_dec": 0x158,
        "id_hex": "0x158",
        "name": "ENGINE_DATA",
        "dlc": 8,
        "signals": [
            {
                "name": "ENGINE_RPM",
                "start_bit": 23,
                "length": 16,
                "byte_order": "motorola",
                "signed": False,
                "scale": 1.0,
                "offset": 0.0,
            }
        ],
    }
    b = dict(a)
    assert compare_encodings(a, b)["identical_encoding"] is True
    b2 = {
        **a,
        "signals": [
            {
                "name": "ENGINE_RPM",
                "start_bit": 22,
                "length": 16,
                "byte_order": "motorola",
                "signed": False,
                "scale": 1.0,
                "offset": 0.0,
            }
        ],
    }
    assert compare_encodings(a, b2)["identical_encoding"] is False


def test_gaps_civic10_real_counts() -> None:
    report = build_gap_report("civic10")
    c = report["completeness"]
    assert c["signals_evaluated"] >= 5
    assert c["cluster_rx_confirmed"] == 0  # never fake confirmation
    assert c["donor_encoding_documented"] >= 1
    assert "fractions" in c
    assert "note" in c
    # fuel absent
    fuel = next(r for r in report["rows"] if r["signal"] == "fuel.level")
    assert fuel["axes"]["B"]["status"] == "ABSENT"


def test_correlate_rpm() -> None:
    hits = correlate_signal(target="honda.civic.gen10", signal="powertrain.engine_rpm")
    assert hits
    assert all(h.signal == "powertrain.engine_rpm" for h in hits)


def test_generate_trace_synthetic_omits_unknowns() -> None:
    result = generate_trace(
        cluster="civic10",
        scenario="idle",
        encode_mode=EncodeMode.SYNTHETIC,
    )
    assert result["frame_count"] > 0
    assert result["candump_lines"]
    assert any("omitted" in o.lower() or "ABSENT" in o for o in result["manifest"]["omissions"])
    # NO_OUTPUT produces nothing
    empty = generate_trace(
        cluster="civic10",
        scenario="idle",
        encode_mode=EncodeMode.NO_OUTPUT,
    )
    assert empty["frame_count"] == 0


def test_cli_cluster_gaps_and_correlate(capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_parser()
    args = parser.parse_args(["cluster", "gaps", "civic10"])
    assert args.func(args) == 0
    out = capsys.readouterr().out
    assert "CLUSTER GAPS" in out
    assert "donor_encoding_documented" in out

    args = parser.parse_args(
        ["correlate", "--target", "honda.civic.gen10", "--signal", "powertrain.engine_rpm"]
    )
    assert args.func(args) == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data


def test_cli_generate_trace(tmp_path: Path) -> None:
    parser = build_parser()
    out = tmp_path / "t.candump.log"
    args = parser.parse_args(
        ["generate-trace", "--cluster", "civic10", "--scenario", "idle", "-o", str(out)]
    )
    assert args.func(args) == 0
    assert out.is_file()
    man = out.parent / (out.name[: -len(".candump.log")] + ".manifest.json")
    assert man.is_file()
    manifest = json.loads(man.read_text(encoding="utf-8"))
    assert manifest["frame_count"] > 0
    assert "omissions" in manifest["manifest"]
