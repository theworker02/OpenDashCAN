"""Protocol diff, DBC conflict, and documentation generation tests."""

from __future__ import annotations

from pathlib import Path

from opendashcan.analysis.protocol_diff import diff_platforms
from opendashcan.core.donor_knowledge import DonorKnowledge
from opendashcan.dbc import (
    import_dbc,
    parse_dbc,
    parse_dbc_messages,
    taxonomy_implementations_from_imports,
)


def test_protocol_diff_civic8_vs_civic10() -> None:
    d = diff_platforms("honda.civic.gen8.us", "honda.civic.gen10.us")
    assert d.source_id == "honda.civic.gen8.us"
    assert d.target_id == "honda.civic.gen10.us"
    text = d.format_text()
    assert "PROTOCOL DIFF" in text
    assert "UNKNOWN" in text or "powertrain.engine_rpm" in text


def test_dbc_parse_and_conflict_detection(tmp_path: Path) -> None:
    dbc = tmp_path / "sample.dbc"
    dbc.write_text(
        "BO_ 344 ENGINE_DATA: 8 PCM\n"
        ' SG_ ENGINE_RPM : 23|16@0+ (1,0) [0|15000] "rpm" EON\n'
        "BO_ 999 FAKE_MSG: 8 XXX\n",
        encoding="utf-8",
    )
    msgs = parse_dbc_messages(dbc.read_text(encoding="utf-8"))
    assert len(msgs) == 2
    assert msgs[0].arbitration_id == 344
    assert msgs[0].signals[0].name == "ENGINE_RPM"
    assert msgs[0].signals[0].start_bit == 23
    assert msgs[0].signals[0].length == 16
    assert not msgs[0].signals[0].is_little_endian

    result = import_dbc(dbc, compare_platform="honda.civic.gen10.us")
    assert result.messages
    assert any(t["taxonomy"] == "powertrain.engine_rpm" for t in result.taxonomy_mapped)
    assert result.taxonomy_mapped[0]["knowledge_level"] in {
        DonorKnowledge.VEHICLE_PROTOCOL_DOCUMENTED.value,
        DonorKnowledge.CLUSTER_RELEVANT_SIGNAL_DOCUMENTED.value,
    }
    assert any("not in registry" in n for n in result.notes)


def test_opendbc_vendored_civic_touring_import() -> None:
    path = Path("dbc/opendbc/generated/honda_civic_touring_2016_can_generated.dbc")
    if not path.is_file():
        return  # optional if DBC not vendored in CI checkout
    result = import_dbc(
        path,
        vehicle="honda.civic.gen10.us.touring_2016",
        source="opendbc",
        compare_platform="honda.civic.gen10.us",
    )
    assert len(result.messages) >= 30
    assert any(m.name == "ENGINE_DATA" and m.arbitration_id == 344 for m in result.messages)
    assert "fuel.level" in result.absent_signals
    assert "powertrain.coolant_temperature" in result.absent_signals
    # Never auto cluster RX
    blob = str(result.to_dict())
    assert "CLUSTER_RX_CONFIRMED" not in blob or all(
        s.get("knowledge_level") != "CLUSTER_RX_CONFIRMED"
        for m in result.to_dict()["messages"]
        for s in m["signals"]
    )


def test_cross_vehicle_index_rpm() -> None:
    index = Path("dbc/opendbc/index")
    if not (index / "cross_vehicle_signal_index.json").is_file():
        return
    cross = taxonomy_implementations_from_imports(index)
    assert "powertrain.engine_rpm" in cross
    assert len(cross["powertrain.engine_rpm"]) >= 5


def test_parse_dbc_alias() -> None:
    msgs = parse_dbc("BO_ 1 X: 8 Y\n")
    assert msgs[0].name == "X"


FIXTURES = Path(__file__).parent / "fixtures"
