"""Translation tests using SYNTHETIC fixtures only."""

from __future__ import annotations

from pathlib import Path

from opendashcan.core.frame import CANFrame
from opendashcan.core.registry import create_decoder, create_encoder, list_vehicles
from opendashcan.core.startup import ClusterStartupSequencer, StartupPhase
from opendashcan.core.state import Confidence, SignalValue, Validity, VehicleState
from opendashcan.core.translator import Translator
from opendashcan.replay.reader import read_candump

FIXTURES = Path(__file__).parent / "fixtures"


def test_registry_has_civic8_and_civic10() -> None:
    ids = {e.vehicle_id for e in list_vehicles()}
    assert "honda-civic8" in ids
    assert "honda-civic10" in ids


def test_civic8_decoder_does_not_invent_values() -> None:
    decoder = create_decoder("honda-civic8")
    state = VehicleState()
    frame = CANFrame(arbitration_id=0x694, data=b"\x00" * 8, timestamp=0.0)
    out = decoder.decode_frame(frame, state)
    assert out.engine_rpm.value is None
    assert out.engine_rpm.confidence == Confidence.UNKNOWN


def test_civic10_encoder_returns_empty_by_default() -> None:
    encoder = create_encoder("honda-civic10")
    state = VehicleState()
    state.engine_rpm = SignalValue(
        value=2000.0,
        confidence=Confidence.INFERRED,
        validity=Validity.VALID,
        source="SYNTHETIC",
        notes="SYNTHETIC",
    )
    assert encoder.encode(state, timestamp=1.0) == []


def test_translate_synthetic_capture() -> None:
    frames = list(read_candump(FIXTURES / "synthetic_candump.log"))
    assert frames
    assert all(fr.arbitration_id in {0x194, 0x494, 0x694} for fr in frames)

    translator = Translator(
        create_decoder("honda-civic8"),
        create_encoder("honda-civic10"),
        sequencer=ClusterStartupSequencer(require_ignition=False, min_known_signals=0),
        emit_while_inactive=True,
    )
    result = translator.process_frames(frames)
    assert result.startup_phase in {
        StartupPhase.POWERED,
        StartupPhase.INITIALIZING,
        StartupPhase.ACTIVE,
    }
    assert result.output_frames == []
    assert result.state.engine_rpm.value is None
