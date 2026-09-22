"""10th-gen Civic target encoder.

Default: EncodeMode.NO_OUTPUT → encode() returns [].
SYNTHETIC / RESEARCH_DOCUMENTED modes may emit labeled research frames using
public opendbc vehicle-bus layouts. Does NOT claim physical donor-cluster
compatibility.
"""

from __future__ import annotations

from typing import TypeVar

from opendashcan.core.encoder import ClusterEncoder, EncodeMode, OutputKind, PeriodicFrameSpec
from opendashcan.core.frame import BusRole, CANFrame, FrameDirection
from opendashcan.core.state import Confidence, GearPosition, SignalValue, VehicleState
from opendashcan.protocols.honda.bitpack import pack_be_unsigned
from opendashcan.protocols.honda.checksum import honda_set_checksum, honda_set_counter
from opendashcan.protocols.honda.civic10.signals import documented_signal_confidence

_T = TypeVar("_T")

ENGINE_DATA = 0x158
POWERTRAIN_DATA = 0x17C
GEARBOX = 0x191
VSA_STATUS = 0x1A4
EPB_STATUS = 0x1C2
SEATBELT_STATUS = 0x305
CAR_SPEED = 0x309
SCM_FEEDBACK = 0x326
STALK_STATUS_2 = 0x37B
DOORS_STATUS = 0x405
ODOMETER = 0x516

_GEAR_TO_BITS = {
    GearPosition.PARK.value: 1,
    GearPosition.REVERSE.value: 2,
    GearPosition.NEUTRAL.value: 4,
    GearPosition.DRIVE.value: 8,
    GearPosition.LOW.value: 32,
    "P": 1,
    "R": 2,
    "N": 4,
    "D": 8,
    "S": 16,
    "L": 32,
}


def _known(sig: SignalValue[_T]) -> bool:
    return sig.value is not None and sig.confidence != Confidence.UNKNOWN


def _finalize(address: int, buf: bytearray, counter: int, *, dlc: int | None = None) -> bytes:
    if dlc is not None and len(buf) != dlc:
        padded = bytearray(dlc)
        padded[: len(buf)] = buf[:dlc]
        buf = padded
    buf = bytearray(honda_set_counter(bytes(buf), counter))
    return honda_set_checksum(address, buf)


def _pack_engine_data(rpm: float | None, xmission_kph: float | None, counter: int) -> bytes:
    buf = bytearray(8)
    speed_raw = int(round((xmission_kph if xmission_kph is not None else 0.0) / 0.01))
    rpm_raw = int(round(rpm if rpm is not None else 0.0))
    pack_be_unsigned(buf, 7, 16, speed_raw)
    pack_be_unsigned(buf, 23, 16, rpm_raw)
    return _finalize(ENGINE_DATA, buf, counter)


def _pack_car_speed(kph: float | None, counter: int) -> bytes:
    buf = bytearray(8)
    speed_raw = int(round((kph if kph is not None else 0.0) / 0.01))
    pack_be_unsigned(buf, 7, 16, speed_raw)
    return _finalize(CAR_SPEED, buf, counter)


def _pack_powertrain(
    pedal_raw: float | None,
    brake: bool | None,
    acc: bool | None,
    rpm: float | None,
    counter: int,
) -> bytes:
    buf = bytearray(8)
    if pedal_raw is not None:
        pack_be_unsigned(buf, 7, 8, int(round(pedal_raw)) & 0xFF)
    if rpm is not None:
        pack_be_unsigned(buf, 23, 16, int(round(rpm)))
    if acc is not None:
        pack_be_unsigned(buf, 38, 1, 1 if acc else 0)
    if brake is not None:
        pack_be_unsigned(buf, 53, 1, 1 if brake else 0)
    return _finalize(POWERTRAIN_DATA, buf, counter)


def _pack_gearbox(gear: str | None, counter: int) -> bytes:
    buf = bytearray(8)
    bits = _GEAR_TO_BITS.get(str(gear), 0) if gear is not None else 0
    pack_be_unsigned(buf, 5, 6, bits)
    return _finalize(GEARBOX, buf, counter)


def _pack_scm_feedback(left: bool | None, right: bool | None, counter: int) -> bytes:
    buf = bytearray(8)
    if left is not None:
        pack_be_unsigned(buf, 26, 1, 1 if left else 0)
    if right is not None:
        pack_be_unsigned(buf, 27, 1, 1 if right else 0)
    return _finalize(SCM_FEEDBACK, buf, counter)


def _pack_doors(
    driver: bool | None,
    passenger: bool | None,
    rear_left: bool | None,
    rear_right: bool | None,
    trunk: bool | None,
    counter: int,
) -> bytes:
    buf = bytearray(8)
    for bit, val in (
        (37, driver),
        (38, passenger),
        (39, rear_left),
        (40, rear_right),
        (41, trunk),
    ):
        if val is not None:
            pack_be_unsigned(buf, bit, 1, 1 if val else 0)
    return _finalize(DOORS_STATUS, buf, counter)


def _pack_epb(active: bool | None, counter: int) -> bytes:
    buf = bytearray(8)
    if active is not None:
        pack_be_unsigned(buf, 3, 1, 1 if active else 0)
    return _finalize(EPB_STATUS, buf, counter)


def _pack_seatbelt(driver: bool | None, passenger: bool | None, counter: int) -> bytes:
    buf = bytearray(7)
    if driver is not None:
        pack_be_unsigned(buf, 13, 1, 1 if driver else 0)
    if passenger is not None:
        pack_be_unsigned(buf, 11, 1, 1 if passenger else 0)
    return _finalize(SEATBELT_STATUS, buf, counter, dlc=7)


def _pack_vsa(esp_disabled: bool | None, counter: int) -> bytes:
    buf = bytearray(8)
    if esp_disabled is not None:
        pack_be_unsigned(buf, 28, 1, 1 if esp_disabled else 0)
    return _finalize(VSA_STATUS, buf, counter)


def _pack_odometer(km: float | None, counter: int) -> bytes:
    buf = bytearray(8)
    if km is not None:
        pack_be_unsigned(buf, 7, 24, int(round(km)) & 0xFFFFFF)
    return _finalize(ODOMETER, buf, counter)


def _pack_stalk2(high: bool | None, low: bool | None, counter: int) -> bytes:
    buf = bytearray(8)
    if high is not None:
        pack_be_unsigned(buf, 34, 1, 1 if high else 0)
    if low is not None:
        pack_be_unsigned(buf, 35, 1, 1 if low else 0)
    return _finalize(STALK_STATUS_2, buf, counter)


def _meta_frame(
    aid: int,
    data: bytes,
    ts: float,
    message: str,
    tag: str,
) -> CANFrame:
    return CANFrame(
        arbitration_id=aid,
        data=data,
        timestamp=ts,
        bus=BusRole.TARGET,
        direction=FrameDirection.TX,
        meta={
            "message": message,
            "evidence": "commaai_opendbc_civic10",
            "output_kind": tag,
            "synthetic": "SYNTHETIC" if tag == "SYNTHETIC" else "false",
            "synthetic_research": "true" if tag == "SYNTHETIC" else "false",
            "cluster_compatibility_claimed": "false",
        },
    )


class Civic10ClusterEncoder(ClusterEncoder):
    cluster_id = "honda.civic.gen10.cluster.digital"
    display_name = "Honda Civic 10th Gen cluster (2016–2021) — research target"

    def __init__(
        self,
        *,
        encode_mode: EncodeMode | None = None,
        emit_synthetic_research: bool = False,
    ) -> None:
        self._counter = 0
        self._last_kind = OutputKind.NO_OUTPUT
        if encode_mode is not None:
            self.encode_mode = encode_mode
        elif emit_synthetic_research:
            self.encode_mode = EncodeMode.SYNTHETIC
        else:
            self.encode_mode = EncodeMode.NO_OUTPUT
        self.emit_synthetic_research = self.encode_mode == EncodeMode.SYNTHETIC
        self.claim_cluster_compatibility = False

    def last_output_kind(self) -> OutputKind:
        return self._last_kind

    def encode(self, state: VehicleState, timestamp: float | None = None) -> list[CANFrame]:
        mode = self.encode_mode
        if mode == EncodeMode.NO_OUTPUT:
            self._last_kind = OutputKind.NO_OUTPUT
            return []
        if mode == EncodeMode.PRODUCTION:
            self._last_kind = OutputKind.NO_OUTPUT
            return []

        ts = timestamp if timestamp is not None else 0.0
        counter = self._counter & 0x3
        self._counter = (self._counter + 1) & 0x3

        if mode == EncodeMode.SYNTHETIC:
            tag = "SYNTHETIC"
            kind = OutputKind.SYNTHETIC
        else:
            tag = "RESEARCH_DOCUMENTED"
            kind = OutputKind.RESEARCH_DOCUMENTED

        frames: list[CANFrame] = []

        rpm = state.engine_rpm.value if _known(state.engine_rpm) else None
        speed = state.vehicle_speed.value if _known(state.vehicle_speed) else None
        if rpm is not None or speed is not None:
            frames.append(
                _meta_frame(
                    ENGINE_DATA,
                    _pack_engine_data(rpm, speed, counter),
                    ts,
                    "ENGINE_DATA",
                    tag,
                )
            )
            frames.append(
                _meta_frame(
                    CAR_SPEED,
                    _pack_car_speed(speed, counter),
                    ts,
                    "CAR_SPEED",
                    tag,
                )
            )

        pedal = state.get("powertrain.throttle_position")
        brake = state.get("brakes.service_brake")
        acc = state.get("adas.acc_state")
        if _known(pedal) or _known(brake) or _known(acc):
            frames.append(
                _meta_frame(
                    POWERTRAIN_DATA,
                    _pack_powertrain(
                        float(pedal.value) if _known(pedal) and pedal.value is not None else None,
                        bool(brake.value) if _known(brake) and brake.value is not None else None,
                        bool(acc.value) if _known(acc) and acc.value is not None else None,
                        rpm,
                        counter,
                    ),
                    ts,
                    "POWERTRAIN_DATA",
                    tag,
                )
            )

        if _known(state.gear_position):
            frames.append(
                _meta_frame(
                    GEARBOX,
                    _pack_gearbox(str(state.gear_position.value), counter),
                    ts,
                    "GEARBOX",
                    tag,
                )
            )

        left = state.turn_signal_left if _known(state.turn_signal_left) else None
        right = state.turn_signal_right if _known(state.turn_signal_right) else None
        if left is not None or right is not None:
            frames.append(
                _meta_frame(
                    SCM_FEEDBACK,
                    _pack_scm_feedback(
                        bool(left.value) if left is not None else None,
                        bool(right.value) if right is not None else None,
                        counter,
                    ),
                    ts,
                    "SCM_FEEDBACK",
                    tag,
                )
            )

        door_keys = (
            ("body.driver_door", 0),
            ("body.passenger_door", 1),
            ("body.rear_left_door", 2),
            ("body.rear_right_door", 3),
            ("body.trunk", 4),
        )
        door_vals: list[bool | None] = [None] * 5
        any_door = False
        for path, idx in door_keys:
            sig = state.get(path)
            if _known(sig):
                door_vals[idx] = bool(sig.value)
                any_door = True
        if any_door:
            frames.append(
                _meta_frame(
                    DOORS_STATUS,
                    _pack_doors(
                        door_vals[0],
                        door_vals[1],
                        door_vals[2],
                        door_vals[3],
                        door_vals[4],
                        counter,
                    ),
                    ts,
                    "DOORS_STATUS",
                    tag,
                )
            )

        if _known(state.parking_brake):
            frames.append(
                _meta_frame(
                    EPB_STATUS,
                    _pack_epb(bool(state.parking_brake.value), counter),
                    ts,
                    "EPB_STATUS",
                    tag,
                )
            )

        sb_d = state.get("safety.seatbelt_driver")
        sb_p = state.get("safety.seatbelt_passenger")
        if _known(sb_d) or _known(sb_p):
            frames.append(
                _meta_frame(
                    SEATBELT_STATUS,
                    _pack_seatbelt(
                        bool(sb_d.value) if _known(sb_d) else None,
                        bool(sb_p.value) if _known(sb_p) else None,
                        counter,
                    ),
                    ts,
                    "SEATBELT_STATUS",
                    tag,
                )
            )

        vsa = state.get("stability.vsa_warning")
        if _known(vsa):
            frames.append(
                _meta_frame(
                    VSA_STATUS,
                    _pack_vsa(bool(vsa.value), counter),
                    ts,
                    "VSA_STATUS",
                    tag,
                )
            )

        odo = state.get("vehicle.odometer")
        if _known(odo) and odo.value is not None:
            frames.append(
                _meta_frame(
                    ODOMETER,
                    _pack_odometer(float(odo.value), counter),
                    ts,
                    "ODOMETER",
                    tag,
                )
            )

        high = state.high_beam if _known(state.high_beam) else None
        low = state.low_beam if _known(state.low_beam) else None
        if high is not None or low is not None:
            frames.append(
                _meta_frame(
                    STALK_STATUS_2,
                    _pack_stalk2(
                        bool(high.value) if high is not None else None,
                        bool(low.value) if low is not None else None,
                        counter,
                    ),
                    ts,
                    "STALK_STATUS_2",
                    tag,
                )
            )

        if not frames:
            self._last_kind = OutputKind.NO_OUTPUT
            return []
        self._last_kind = kind
        return frames

    def supported_signals(self) -> dict[str, str]:
        return documented_signal_confidence()

    def periodic_specs(self) -> list[PeriodicFrameSpec]:
        return [
            PeriodicFrameSpec(
                arbitration_id=ENGINE_DATA,
                period_ms=10.0,
                name="ENGINE_DATA (opendbc research)",
                notes="Vehicle-bus layout; cluster RX NOT bench-verified.",
                requires_checksum=True,
                requires_counter=True,
                synthetic=True,
            ),
            PeriodicFrameSpec(
                arbitration_id=CAR_SPEED,
                period_ms=100.0,
                name="CAR_SPEED (opendbc research)",
                notes="Vehicle-bus layout; cluster RX NOT bench-verified.",
                synthetic=True,
            ),
            PeriodicFrameSpec(
                arbitration_id=SCM_FEEDBACK,
                period_ms=100.0,
                name="SCM_FEEDBACK blinkers (opendbc research)",
                notes="Bosch/Nidec-B LEFT/RIGHT_BLINKER @26/27; cluster RX NOT verified.",
                synthetic=True,
            ),
            PeriodicFrameSpec(
                arbitration_id=GEARBOX,
                period_ms=100.0,
                name="GEARBOX classic packing (opendbc research)",
                notes=(
                    "Classic GEAR_SHIFTER @5|6; CONFLICT with _gearbox_common — see conflicts.yaml."
                ),
                synthetic=True,
            ),
            PeriodicFrameSpec(
                arbitration_id=DOORS_STATUS,
                period_ms=100.0,
                name="DOORS_STATUS (opendbc research)",
                synthetic=True,
            ),
        ]


Civic10Encoder = Civic10ClusterEncoder
