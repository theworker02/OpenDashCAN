"""Virtual cluster — SOFTWARE VALIDATION ONLY consumer of target frames."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from opendashcan.core.frame import CANFrame
from opendashcan.protocols.honda.bitpack import unpack_be_bool, unpack_be_unsigned

# opendbc-documented IDs used by Civic10 encoder (research frames)
_ENGINE_DATA = 0x158
_POWERTRAIN_DATA = 0x17C
_GEARBOX = 0x191
_VSA_STATUS = 0x1A4
_EPB_STATUS = 0x1C2
_SEATBELT_STATUS = 0x305
_CAR_SPEED = 0x309
_SCM_FEEDBACK = 0x326
_STALK_STATUS_2 = 0x37B
_DOORS_STATUS = 0x405
_ODOMETER = 0x516

_KNOWN_IDS = frozenset(
    {
        _ENGINE_DATA,
        _POWERTRAIN_DATA,
        _GEARBOX,
        _VSA_STATUS,
        _EPB_STATUS,
        _SEATBELT_STATUS,
        _CAR_SPEED,
        _SCM_FEEDBACK,
        _STALK_STATUS_2,
        _DOORS_STATUS,
        _ODOMETER,
    }
)


def _be16(data: bytes, offset: int) -> int:
    return (data[offset] << 8) | data[offset + 1]


@dataclass
class VirtualCluster:
    """Interprets known target frames for software tests only.

    Label every result: SOFTWARE VALIDATION ONLY.
    Does not prove hardware compatibility.
    """

    cluster_id: str
    rpm: float | None = None
    speed_kph: float | None = None
    gear: str | None = None
    left_blinker: bool | None = None
    right_blinker: bool | None = None
    high_beam: bool | None = None
    low_beam: bool | None = None
    parking_brake: bool | None = None
    vsa_warning: bool | None = None
    odometer_km: float | None = None
    driver_door: bool | None = None
    passenger_door: bool | None = None
    trunk: bool | None = None
    seatbelt_driver: bool | None = None
    pedal_gas_raw: float | None = None
    brake_pressed: bool | None = None
    frames_seen: int = 0
    unknown_ids: list[int] = field(default_factory=list)
    last_meta: dict[str, Any] = field(default_factory=dict)

    def consume(self, frame: CANFrame) -> None:
        self.frames_seen += 1
        self.last_meta = dict(frame.meta or {})
        data = bytes(frame.data)
        aid = frame.arbitration_id

        if aid == _ENGINE_DATA and len(data) >= 4:
            self.speed_kph = unpack_be_unsigned(data, 7, 16) * 0.01
            self.rpm = float(unpack_be_unsigned(data, 23, 16))
        elif aid == _CAR_SPEED and len(data) >= 2:
            self.speed_kph = unpack_be_unsigned(data, 7, 16) * 0.01
        elif aid == _POWERTRAIN_DATA and len(data) >= 8:
            self.pedal_gas_raw = float(unpack_be_unsigned(data, 7, 8))
            self.brake_pressed = unpack_be_bool(data, 53)
        elif aid == _GEARBOX and len(data) >= 8:
            bits = unpack_be_unsigned(data, 5, 6)
            for mask, label in (
                (1, "P"),
                (2, "R"),
                (4, "N"),
                (8, "D"),
                (16, "S"),
                (32, "L"),
            ):
                if bits & mask:
                    self.gear = label
                    break
        elif aid == _SCM_FEEDBACK and len(data) >= 8:
            self.left_blinker = unpack_be_bool(data, 26)
            self.right_blinker = unpack_be_bool(data, 27)
        elif aid == _STALK_STATUS_2 and len(data) >= 8:
            self.high_beam = unpack_be_bool(data, 34)
            self.low_beam = unpack_be_bool(data, 35)
        elif aid == _DOORS_STATUS and len(data) >= 8:
            self.driver_door = unpack_be_bool(data, 37)
            self.passenger_door = unpack_be_bool(data, 38)
            self.trunk = unpack_be_bool(data, 41)
        elif aid == _EPB_STATUS and len(data) >= 8:
            self.parking_brake = unpack_be_bool(data, 3)
        elif aid == _SEATBELT_STATUS and len(data) >= 7:
            self.seatbelt_driver = unpack_be_bool(data, 13)
        elif aid == _VSA_STATUS and len(data) >= 8:
            self.vsa_warning = unpack_be_bool(data, 28)
        elif aid == _ODOMETER and len(data) >= 8:
            self.odometer_km = float(unpack_be_unsigned(data, 7, 24))
        else:
            if aid not in _KNOWN_IDS and aid not in self.unknown_ids:
                self.unknown_ids.append(aid)

    def consume_many(self, frames: list[CANFrame]) -> None:
        for f in frames:
            self.consume(f)

    def snapshot(self) -> dict[str, Any]:
        return {
            "label": "SOFTWARE VALIDATION ONLY",
            "cluster_id": self.cluster_id,
            "rpm": self.rpm,
            "speed_kph": self.speed_kph,
            "gear": self.gear,
            "left_blinker": self.left_blinker,
            "right_blinker": self.right_blinker,
            "high_beam": self.high_beam,
            "low_beam": self.low_beam,
            "parking_brake": self.parking_brake,
            "vsa_warning": self.vsa_warning,
            "odometer_km": self.odometer_km,
            "driver_door": self.driver_door,
            "passenger_door": self.passenger_door,
            "trunk": self.trunk,
            "seatbelt_driver": self.seatbelt_driver,
            "pedal_gas_raw": self.pedal_gas_raw,
            "brake_pressed": self.brake_pressed,
            "frames_seen": self.frames_seen,
            "unknown_ids": [hex(i) for i in self.unknown_ids],
            "last_meta": self.last_meta,
            "hardware_compatibility_claimed": False,
        }


def run_software_validation(cluster: VirtualCluster, frames: list[CANFrame]) -> dict[str, Any]:
    cluster.consume_many(frames)
    return cluster.snapshot()
