"""Global normalized signal taxonomy (Phase 2).

Canonical dotted paths are the single source of truth for signal *names*.
Platform-specific CAN encodings live in protocol YAML — never duplicated here.
"""

from __future__ import annotations

from typing import Final

# Flat Phase-1 field → taxonomy path (backward compatibility).
FLAT_TO_TAXONOMY: Final[dict[str, str]] = {
    "engine_rpm": "powertrain.engine_rpm",
    "vehicle_speed": "vehicle.speed",
    "coolant_temperature": "powertrain.coolant_temperature",
    "fuel_level": "fuel.level",
    "gear_position": "transmission.gear",
    "transmission_state": "transmission.selector_position",
    "turn_signal_left": "lighting.left_indicator",
    "turn_signal_right": "lighting.right_indicator",
    "hazards": "lighting.hazards",
    "high_beam": "lighting.high_beam",
    "low_beam": "lighting.low_beam",
    "parking_brake": "brakes.parking_brake",
    "trunk_state": "body.trunk",
    "ignition_state": "vehicle.ignition_state",
}

TAXONOMY_TO_FLAT: Final[dict[str, str]] = {v: k for k, v in FLAT_TO_TAXONOMY.items()}

# All known normalized signal paths. Platforms may implement a subset.
SIGNAL_TAXONOMY: Final[tuple[str, ...]] = (
    # POWERTRAIN
    "powertrain.engine_rpm",
    "powertrain.engine_running",
    "powertrain.throttle_position",
    "powertrain.engine_load",
    "powertrain.coolant_temperature",
    "powertrain.intake_temperature",
    "powertrain.oil_temperature",
    "powertrain.oil_pressure",
    # VEHICLE
    "vehicle.speed",
    "vehicle.odometer",
    "vehicle.trip_distance",
    "vehicle.ignition_state",
    # TRANSMISSION
    "transmission.gear",
    "transmission.selector_position",
    "transmission.temperature",
    # FUEL
    "fuel.level",
    "fuel.range",
    "fuel.consumption",
    "fuel.low_warning",
    # LIGHTING
    "lighting.left_indicator",
    "lighting.right_indicator",
    "lighting.hazards",
    "lighting.low_beam",
    "lighting.high_beam",
    "lighting.fog_lights",
    "lighting.headlights_on",
    # CHASSIS
    "chassis.steering_angle",
    # BRAKES / STABILITY
    "brakes.parking_brake",
    "brakes.service_brake",
    "brakes.abs_warning",
    "stability.vsa_active",
    "stability.vsa_warning",
    # BODY
    "body.driver_door",
    "body.passenger_door",
    "body.rear_left_door",
    "body.rear_right_door",
    "body.trunk",
    "body.hood",
    # SAFETY
    "safety.srs_warning",
    "safety.seatbelt_driver",
    "safety.seatbelt_passenger",
    "safety.check_engine",
    "safety.oil_pressure_warning",
    "safety.battery_warning",
    # ELECTRICAL
    "electrical.battery_voltage",
    "electrical.charging_warning",
    # ADAS (unsupported unless platform evidence says otherwise)
    "adas.acc_state",
    "adas.lane_assist_state",
    "adas.collision_warning",
)

SIGNAL_UNITS: Final[dict[str, str | None]] = {
    "powertrain.engine_rpm": "rpm",
    "powertrain.throttle_position": "percent",
    "powertrain.engine_load": "percent",
    "powertrain.coolant_temperature": "C",
    "powertrain.intake_temperature": "C",
    "powertrain.oil_temperature": "C",
    "powertrain.oil_pressure": "kPa",
    "vehicle.speed": "kph",
    "vehicle.odometer": "km",
    "vehicle.trip_distance": "km",
    "chassis.steering_angle": "deg",
    "fuel.level": "percent",
    "fuel.range": "km",
    "fuel.consumption": "L/100km",
    "transmission.temperature": "C",
    "electrical.battery_voltage": "V",
}


def is_valid_signal_path(path: str) -> bool:
    return path in SIGNAL_TAXONOMY


def resolve_signal_path(name: str) -> str:
    """Accept flat Phase-1 names or dotted taxonomy paths."""
    if name in SIGNAL_TAXONOMY:
        return name
    if name in FLAT_TO_TAXONOMY:
        return FLAT_TO_TAXONOMY[name]
    raise KeyError(f"unknown signal name: {name}")
