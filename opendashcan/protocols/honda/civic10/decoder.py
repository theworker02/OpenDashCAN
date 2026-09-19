"""Civic 10 vehicle-bus decoder from public opendbc layouts (MIT).

Decodes documented vehicle-bus messages into VehicleState.
Does NOT claim physical donor-cluster compatibility.
"""

from __future__ import annotations

from opendashcan.core.decoder import VehicleDecoder
from opendashcan.core.frame import CANFrame
from opendashcan.core.state import (
    Confidence,
    DoorStates,
    GearPosition,
    Validity,
    VehicleState,
)
from opendashcan.protocols.honda.bitpack import unpack_be_bool, unpack_be_unsigned
from opendashcan.protocols.honda.checksum import honda_verify_checksum

ENGINE_DATA = 0x158
POWERTRAIN_DATA = 0x17C
CAR_SPEED = 0x309
GEARBOX = 0x191
VSA_STATUS = 0x1A4
EPB_STATUS = 0x1C2
WHEEL_SPEEDS = 0x1D0
SEATBELT_STATUS = 0x305
DOORS_STATUS = 0x405
STALK_STATUS = 0x374
STALK_STATUS_2 = 0x37B
SCM_FEEDBACK = 0x326
STEERING_SENSORS = 0x14A
ODOMETER = 0x516
ACC_HUD = 0x30C

_GEAR_BITS = (
    (1, GearPosition.PARK),
    (2, GearPosition.REVERSE),
    (4, GearPosition.NEUTRAL),
    (8, GearPosition.DRIVE),
    (16, GearPosition.DRIVE),
    (32, GearPosition.LOW),
)

_CONF = Confidence.DOCUMENTED
_SRC = "opendbc_honda_civic_2016_2017"


def _meta(message: str) -> dict[str, str | None]:
    return {
        "source": _SRC,
        "source_vehicle": "honda.civic.gen10.us",
        "source_bus": "vehicle_can",
        "source_message": message,
    }


class Civic10VehicleDecoder(VehicleDecoder):
    vehicle_id = "honda.civic.gen10.us"
    display_name = "Honda Civic 10th Gen vehicle-bus (opendbc DOCUMENTED)"

    def __init__(self, *, require_checksum: bool = False) -> None:
        self.require_checksum = require_checksum
        self.checksum_failures = 0

    def _ok(self, frame: CANFrame) -> bool:
        if not self.require_checksum:
            return True
        if honda_verify_checksum(frame.arbitration_id, frame.data):
            return True
        self.checksum_failures += 1
        return False

    def decode_frame(self, frame: CANFrame, state: VehicleState) -> VehicleState:
        data = frame.data
        if len(data) < 3 or not self._ok(frame):
            return state
        ts = frame.timestamp
        aid = frame.arbitration_id

        if aid == ENGINE_DATA and len(data) >= 8:
            m = _meta("ENGINE_DATA")
            state.set(
                "powertrain.engine_rpm",
                float(unpack_be_unsigned(data, 23, 16)),
                unit="rpm",
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc ENGINE_RPM @23|16",
                **m,
            )
            state.set(
                "vehicle.speed",
                unpack_be_unsigned(data, 7, 16) * 0.01,
                unit="kph",
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc XMISSION_SPEED @7|16 scale 0.01",
                **m,
            )
        elif aid == CAR_SPEED and len(data) >= 8:
            state.set(
                "vehicle.speed",
                unpack_be_unsigned(data, 7, 16) * 0.01,
                unit="kph",
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc CAR_SPEED @7|16",
                **_meta("CAR_SPEED"),
            )
        elif aid == POWERTRAIN_DATA and len(data) >= 8:
            m = _meta("POWERTRAIN_DATA")
            state.set(
                "powertrain.throttle_position",
                float(unpack_be_unsigned(data, 7, 8)),
                unit="raw",
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc PEDAL_GAS 0-255 raw",
                **m,
            )
            state.set(
                "brakes.service_brake",
                unpack_be_bool(data, 53),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc BRAKE_PRESSED",
                **m,
            )
            state.set(
                "adas.acc_state",
                unpack_be_bool(data, 38),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc ACC_STATUS",
                **m,
            )
        elif aid == GEARBOX and len(data) >= 8:
            bits = unpack_be_unsigned(data, 5, 6)
            gear = GearPosition.UNKNOWN
            for mask, g in _GEAR_BITS:
                if bits & mask:
                    gear = g
                    break
            state.set(
                "transmission.gear",
                gear.value,
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID if gear != GearPosition.UNKNOWN else Validity.UNKNOWN,
                evidence_refs=("ev_opendbc_civic10",),
                notes=f"opendbc GEAR_SHIFTER raw={bits}; S mapped to D",
                **_meta("GEARBOX"),
            )
        elif aid == SCM_FEEDBACK and len(data) >= 8:
            m = _meta("SCM_FEEDBACK")
            state.set(
                "lighting.left_indicator",
                unpack_be_bool(data, 26),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc LEFT_BLINKER SCM_FEEDBACK",
                **m,
            )
            state.set(
                "lighting.right_indicator",
                unpack_be_bool(data, 27),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc RIGHT_BLINKER SCM_FEEDBACK",
                **m,
            )
        elif aid == STALK_STATUS_2 and len(data) >= 8:
            m = _meta("STALK_STATUS_2")
            state.set(
                "lighting.high_beam",
                unpack_be_bool(data, 34),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                **m,
            )
            state.set(
                "lighting.low_beam",
                unpack_be_bool(data, 35),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                **m,
            )
        elif aid == STALK_STATUS and len(data) >= 8:
            # HEADLIGHTS_ON / HIGH_BEAM_FLASH documented in opendbc; beams also on 0x37B.
            # Store headlights separately; do not invent cluster lamp semantics.
            m = _meta("STALK_STATUS")
            state.set(
                "lighting.headlights_on",
                unpack_be_bool(data, 54),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc HEADLIGHTS_ON STALK_STATUS; taxonomy extra path",
                **m,
            )
        elif aid == STEERING_SENSORS and len(data) >= 8:
            # STEER_ANGLE 7|16@0- scale -0.1 deg (_steering_sensors_a.dbc)
            raw = unpack_be_unsigned(data, 7, 16)
            if raw & 0x8000:
                raw -= 0x10000
            angle = raw * -0.1
            state.set(
                "chassis.steering_angle",
                angle,
                unit="deg",
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc STEER_ANGLE @7|16 scale -0.1; not a cluster gauge claim",
                **_meta("STEERING_SENSORS"),
            )
        elif aid == EPB_STATUS and len(data) >= 8:
            state.set(
                "brakes.parking_brake",
                unpack_be_bool(data, 3),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc EPB_ACTIVE",
                **_meta("EPB_STATUS"),
            )
        elif aid == VSA_STATUS and len(data) >= 8:
            state.set(
                "stability.vsa_warning",
                unpack_be_bool(data, 28),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc ESP_DISABLED",
                **_meta("VSA_STATUS"),
            )
        elif aid == SEATBELT_STATUS and len(data) >= 7:
            m = _meta("SEATBELT_STATUS")
            state.set(
                "safety.seatbelt_driver",
                unpack_be_bool(data, 13),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                **m,
            )
            state.set(
                "safety.seatbelt_passenger",
                unpack_be_bool(data, 11),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="SEATBELT_PASS_LATCHED",
                **m,
            )
        elif aid == DOORS_STATUS and len(data) >= 8:
            doors = DoorStates(
                driver=unpack_be_bool(data, 37),
                passenger=unpack_be_bool(data, 38),
                rear_left=unpack_be_bool(data, 39),
                rear_right=unpack_be_bool(data, 40),
            )
            m = _meta("DOORS_STATUS")
            for path, val in (
                ("body.driver_door", doors.driver),
                ("body.passenger_door", doors.passenger),
                ("body.rear_left_door", doors.rear_left),
                ("body.rear_right_door", doors.rear_right),
                ("body.trunk", unpack_be_bool(data, 41)),
            ):
                state.set(
                    path,
                    val,
                    timestamp=ts,
                    confidence=_CONF,
                    validity=Validity.VALID,
                    evidence_refs=("ev_opendbc_civic10",),
                    **m,
                )
            state.door_states = state.get("body.driver_door").with_update(
                value=doors, confidence=_CONF, validity=Validity.VALID
            )
        elif aid == ODOMETER and len(data) >= 8:
            state.set(
                "vehicle.odometer",
                float(unpack_be_unsigned(data, 7, 24)),
                unit="km",
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                **_meta("ODOMETER"),
            )
        elif aid == ACC_HUD and len(data) >= 8:
            state.set(
                "adas.acc_state",
                unpack_be_bool(data, 52),
                timestamp=ts,
                confidence=_CONF,
                validity=Validity.VALID,
                evidence_refs=("ev_opendbc_civic10",),
                notes="opendbc ACC_ON ACC_HUD",
                **_meta("ACC_HUD"),
            )
        elif aid == WHEEL_SPEEDS and len(data) >= 8:
            if state.vehicle_speed.confidence == Confidence.UNKNOWN:
                fl = unpack_be_unsigned(data, 7, 15) * 0.01
                fr = unpack_be_unsigned(data, 8, 15) * 0.01
                state.set(
                    "vehicle.speed",
                    (fl + fr) / 2.0,
                    unit="kph",
                    timestamp=ts,
                    confidence=_CONF,
                    validity=Validity.VALID,
                    evidence_refs=("ev_opendbc_civic10",),
                    notes="mean FL/FR WHEEL_SPEEDS fallback",
                    **_meta("WHEEL_SPEEDS"),
                )
        return state

    def supported_signals(self) -> dict[str, str]:
        return {
            "powertrain.engine_rpm": "DOCUMENTED",
            "vehicle.speed": "DOCUMENTED",
            "vehicle.odometer": "DOCUMENTED",
            "powertrain.throttle_position": "DOCUMENTED",
            "transmission.gear": "DOCUMENTED",
            "lighting.left_indicator": "DOCUMENTED",
            "lighting.right_indicator": "DOCUMENTED",
            "lighting.high_beam": "DOCUMENTED",
            "lighting.low_beam": "DOCUMENTED",
            "brakes.parking_brake": "DOCUMENTED",
            "brakes.service_brake": "DOCUMENTED",
            "stability.vsa_warning": "DOCUMENTED",
            "safety.seatbelt_driver": "DOCUMENTED",
            "safety.seatbelt_passenger": "DOCUMENTED",
            "body.driver_door": "DOCUMENTED",
            "body.passenger_door": "DOCUMENTED",
            "body.rear_left_door": "DOCUMENTED",
            "body.rear_right_door": "DOCUMENTED",
            "body.trunk": "DOCUMENTED",
            "adas.acc_state": "DOCUMENTED",
            "lighting.headlights_on": "DOCUMENTED",
            "chassis.steering_angle": "DOCUMENTED",
            "fuel.level": "UNKNOWN",
            "powertrain.coolant_temperature": "UNKNOWN",
        }


Civic10Decoder = Civic10VehicleDecoder
