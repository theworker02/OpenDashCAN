"""Tests for Civic10 vehicle-bus decoder (opendbc-documented layouts)."""

from __future__ import annotations

from pathlib import Path

from opendashcan.core.encoder import EncodeMode
from opendashcan.core.frame import CANFrame
from opendashcan.core.state import Confidence, VehicleState
from opendashcan.protocols.honda.bitpack import pack_be_unsigned, unpack_be_unsigned
from opendashcan.protocols.honda.checksum import honda_set_checksum, honda_set_counter
from opendashcan.protocols.honda.civic10.decoder import Civic10VehicleDecoder
from opendashcan.protocols.honda.civic10.encoder import Civic10Encoder
from opendashcan.replay.reader import read_asc, read_candump, read_capture

ROOT = Path(__file__).resolve().parents[1]
SYNTH_LOG = ROOT / "captures" / "synthetic" / "idle_scenario.log"
SYNTH_ASC = ROOT / "captures" / "synthetic" / "idle_scenario.asc"


def test_bitpack_roundtrip_rpm_field() -> None:
    buf = bytearray(8)
    pack_be_unsigned(buf, 23, 16, 2500)
    assert unpack_be_unsigned(bytes(buf), 23, 16) == 2500


def test_default_encode_mode_is_no_output() -> None:
    enc = Civic10Encoder()
    assert enc.encode_mode == EncodeMode.NO_OUTPUT
    state = VehicleState()
    state.set("powertrain.engine_rpm", 1000.0, confidence=Confidence.DOCUMENTED)
    assert enc.encode(state) == []


def test_decode_engine_data_from_encoder_synthetic() -> None:
    enc = Civic10Encoder(encode_mode=EncodeMode.SYNTHETIC)
    state = VehicleState()
    state.set("powertrain.engine_rpm", 2000.0, confidence=Confidence.DOCUMENTED)
    state.set("vehicle.speed", 40.0, confidence=Confidence.DOCUMENTED)
    frames = enc.encode(state, timestamp=1.0)
    assert frames
    dec = Civic10VehicleDecoder()
    out = VehicleState()
    for fr in frames:
        out = dec.decode_frame(fr, out)
    assert out.engine_rpm.value == 2000.0
    assert out.vehicle_speed.value == 40.0
    assert out.engine_rpm.confidence == Confidence.DOCUMENTED


def test_encoder_packs_gear_blinkers_doors_roundtrip() -> None:
    enc = Civic10Encoder(encode_mode=EncodeMode.RESEARCH_DOCUMENTED)
    state = VehicleState()
    state.set("transmission.gear", "D", confidence=Confidence.DOCUMENTED)
    state.set("lighting.left_indicator", True, confidence=Confidence.DOCUMENTED)
    state.set("lighting.right_indicator", False, confidence=Confidence.DOCUMENTED)
    state.set("body.driver_door", True, confidence=Confidence.DOCUMENTED)
    state.set("brakes.parking_brake", True, confidence=Confidence.DOCUMENTED)
    state.set("safety.seatbelt_driver", False, confidence=Confidence.DOCUMENTED)
    state.set("stability.vsa_warning", True, confidence=Confidence.DOCUMENTED)
    state.set("vehicle.odometer", 999.0, confidence=Confidence.DOCUMENTED)
    state.set("lighting.high_beam", True, confidence=Confidence.DOCUMENTED)
    state.set("lighting.low_beam", False, confidence=Confidence.DOCUMENTED)
    frames = enc.encode(state, timestamp=0.0)
    ids = {f.arbitration_id for f in frames}
    assert 0x191 in ids
    assert 0x326 in ids
    assert 0x405 in ids
    assert 0x1C2 in ids
    assert 0x305 in ids
    assert 0x1A4 in ids
    assert 0x516 in ids
    assert 0x37B in ids
    out = Civic10VehicleDecoder().decode_frames(frames)
    assert out.gear_position.value == "D"
    assert out.turn_signal_left.value is True
    assert out.get("body.driver_door").value is True
    assert out.parking_brake.value is True
    assert out.get("safety.seatbelt_driver").value is False
    assert out.get("stability.vsa_warning").value is True
    assert out.get("vehicle.odometer").value == 999.0
    assert out.high_beam.value is True


def test_decode_scm_feedback_blinkers() -> None:
    buf = bytearray(8)
    pack_be_unsigned(buf, 26, 1, 1)  # LEFT
    pack_be_unsigned(buf, 27, 1, 0)
    data = honda_set_checksum(0x326, honda_set_counter(bytes(buf), 1))
    dec = Civic10VehicleDecoder()
    st = dec.decode_frame(CANFrame(0x326, data, 0.0), VehicleState())
    assert st.turn_signal_left.value is True
    assert st.turn_signal_right.value is False


def test_decode_gearbox_park() -> None:
    buf = bytearray(8)
    pack_be_unsigned(buf, 5, 6, 1)  # P
    data = honda_set_checksum(0x191, honda_set_counter(bytes(buf), 0))
    st = Civic10VehicleDecoder().decode_frame(CANFrame(0x191, data, 0.0), VehicleState())
    assert st.gear_position.value == "P"


def test_decode_steering_sensors() -> None:
    buf = bytearray(8)
    # +10.0 deg → raw = 10 / -0.1 = -100 → 0xFF9C as signed
    pack_be_unsigned(buf, 7, 16, (-100) & 0xFFFF)
    data = honda_set_checksum(0x14A, honda_set_counter(bytes(buf), 0))
    st = Civic10VehicleDecoder().decode_frame(CANFrame(0x14A, data, 0.0), VehicleState())
    assert abs(float(st.get("chassis.steering_angle").value) - 10.0) < 0.05


def test_decode_stalk_status_headlights() -> None:
    buf = bytearray(8)
    pack_be_unsigned(buf, 54, 1, 1)
    data = honda_set_checksum(0x374, honda_set_counter(bytes(buf), 0))
    st = Civic10VehicleDecoder().decode_frame(CANFrame(0x374, data, 0.0), VehicleState())
    assert st.get("lighting.headlights_on").value is True


def test_synthetic_idle_scenario_fixture() -> None:
    assert SYNTH_LOG.is_file()
    frames = list(read_candump(SYNTH_LOG))
    assert len(frames) >= 10
    ids = {f.arbitration_id for f in frames}
    assert 0x158 in ids
    assert 0x326 in ids
    assert 0x405 in ids
    st = Civic10VehicleDecoder().decode_frames(frames)
    assert st.engine_rpm.value is not None
    assert st.gear_position.value == "P"


def test_asc_idle_scenario_ingest() -> None:
    assert SYNTH_ASC.is_file()
    frames = list(read_asc(SYNTH_ASC))
    assert frames
    assert frames[0].meta.get("format") == "asc"
    via_capture = list(read_capture(SYNTH_ASC))
    assert len(via_capture) == len(frames)


def test_registry_get_decoder_civic10() -> None:
    from opendashcan.registry.vehicles import get_decoder

    d = get_decoder("honda.civic.gen10.us")
    assert "powertrain.engine_rpm" in d.supported_signals()
    assert d.supported_signals()["fuel.level"] == "UNKNOWN"
