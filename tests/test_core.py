"""SYNTHETIC fixture only — not real vehicle traffic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from opendashcan.core.frame import BusRole, CANFrame
from opendashcan.core.startup import ClusterStartupSequencer, StartupPhase
from opendashcan.core.state import Confidence, SignalValue, Validity, VehicleState
from opendashcan.core.translator import Translator
from opendashcan.hardware.interfaces import BusConfig, DualBusConfig, LinkMode, NullDualBusAdapter
from opendashcan.protocols.honda.checksum import honda_set_checksum, honda_verify_checksum
from opendashcan.protocols.honda.civic8 import Civic8Decoder
from opendashcan.protocols.honda.civic10 import Civic10Encoder
from opendashcan.replay.reader import read_candump, read_json
from opendashcan.replay.simulator import iter_scenario, synthetic_source_frames

FIXTURES = Path(__file__).parent / "fixtures"


def test_frame_rejects_oversized_classic_payload() -> None:
    with pytest.raises(ValueError):
        CANFrame(arbitration_id=0x100, data=bytes(9), timestamp=0.0)


def test_honda_checksum_roundtrip_opendbc_algo() -> None:
    raw = bytearray(8)
    raw[0] = 0x12
    raw[1] = 0x34
    framed = honda_set_checksum(0x158, raw)
    assert honda_verify_checksum(0x158, framed)


def test_civic8_decoder_does_not_invent_values() -> None:
    dec = Civic8Decoder()
    state = VehicleState()
    frame = CANFrame(
        arbitration_id=0x194,
        data=bytes(8),
        timestamp=1.0,
        meta={"SYNTHETIC": "true"},
    )
    out = dec.decode_frame(frame, state)
    assert out.engine_rpm.value is None
    assert out.engine_rpm.confidence == Confidence.UNKNOWN
    assert 0x194 in dec.seen_watch_ids


def test_translator_synthetic_scenario_encoder_path() -> None:
    encoder = Civic10Encoder(emit_synthetic_research=True)
    translator = Translator(
        Civic8Decoder(),
        encoder,
        sequencer=ClusterStartupSequencer(require_ignition=False),
        emit_while_inactive=True,
    )
    step, state = next(iter_scenario("idle"))
    translator.state = state
    out_frames = translator.encoder.encode(state, timestamp=step.t)
    assert out_frames
    assert all(fr.meta.get("synthetic_research") == "true" for fr in out_frames)
    assert all(fr.meta.get("cluster_compatibility_claimed") == "false" for fr in out_frames)


def test_startup_sequencer_reaches_active() -> None:
    seq = ClusterStartupSequencer(require_ignition=True, min_known_signals=1)
    state = VehicleState(
        ignition_state=SignalValue(
            value="ON",
            confidence=Confidence.INFERRED,
            validity=Validity.VALID,
            source="synthetic",
        ),
        engine_rpm=SignalValue(
            value=800.0,
            confidence=Confidence.INFERRED,
            validity=Validity.VALID,
            source="synthetic",
            unit="rpm",
        ),
    )
    assert seq.observe_state(state) == StartupPhase.POWERED
    assert seq.observe_state(state) == StartupPhase.INITIALIZING
    assert seq.observe_state(state) == StartupPhase.ACTIVE


def test_null_adapter_blocks_tx() -> None:
    cfg = DualBusConfig(
        source=BusConfig(role=BusRole.SOURCE, channel="can0"),
        target=BusConfig(role=BusRole.TARGET, channel="can1"),
        mode=LinkMode.OFFLINE,
        tx_enabled=False,
    )
    adapter = NullDualBusAdapter(cfg)
    adapter.connect()
    with pytest.raises(RuntimeError):
        adapter.write_target(CANFrame(arbitration_id=0x100, data=b"\x00", timestamp=0.0))


def test_read_synthetic_candump_fixture() -> None:
    path = FIXTURES / "synthetic_candump.log"
    frames = list(read_candump(path))
    assert len(frames) >= 1
    assert frames[0].meta.get("format") == "candump"


def test_read_synthetic_json_fixture() -> None:
    path = FIXTURES / "synthetic_frames.json"
    frames = list(read_json(path))
    assert frames


def test_synthetic_source_frames_labeled() -> None:
    frames = synthetic_source_frames("accelerate")
    assert frames
    assert all(fr.meta.get("SYNTHETIC") == "true" for fr in frames)


def test_vehicle_state_as_dict_roundtrip_keys() -> None:
    data = VehicleState().as_dict()
    assert "engine_rpm" in data
    assert data["engine_rpm"]["confidence"] == "UNKNOWN"


def test_synthetic_json_fixture_is_marked() -> None:
    payload = json.loads((FIXTURES / "synthetic_frames.json").read_text(encoding="utf-8"))
    assert payload.get("synthetic") is True
