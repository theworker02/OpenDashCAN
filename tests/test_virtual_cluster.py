"""Virtual cluster software-validation tests."""

from __future__ import annotations

from opendashcan.adaptation.virtual_cluster import VirtualCluster, run_software_validation
from opendashcan.core.frame import BusRole, CANFrame, FrameDirection
from opendashcan.core.state import Confidence, SignalValue, Validity, VehicleState
from opendashcan.protocols.honda.civic10.encoder import Civic10Encoder


def test_virtual_cluster_reads_encoder_frames():
    enc = Civic10Encoder(emit_synthetic_research=True)
    state = VehicleState()
    state.engine_rpm = SignalValue(2437.0, confidence=Confidence.INFERRED, validity=Validity.VALID)
    state.vehicle_speed = SignalValue(50.0, confidence=Confidence.INFERRED, validity=Validity.VALID)
    frames = enc.encode(state, timestamp=1.0)
    assert frames
    vc = VirtualCluster(cluster_id="honda.civic.gen10.cluster.digital")
    snap = run_software_validation(vc, frames)
    assert snap["label"] == "SOFTWARE VALIDATION ONLY"
    assert snap["hardware_compatibility_claimed"] is False
    assert snap["rpm"] == 2437.0
    assert snap["speed_kph"] == 50.0


def test_virtual_cluster_unknown_id():
    vc = VirtualCluster(cluster_id="test")
    frame = CANFrame(
        arbitration_id=0x7FF,
        data=bytes(8),
        timestamp=0.0,
        bus=BusRole.TARGET,
        direction=FrameDirection.TX,
    )
    vc.consume(frame)
    assert "0x7ff" in vc.snapshot()["unknown_ids"]
