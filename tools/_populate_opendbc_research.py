#!/usr/bin/env python3
"""Populate Honda 2016-2022 protocol YAML from researched public opendbc facts.

Does NOT invent Civic 8/9 byte layouts. Does NOT copy full DBC files.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTO = ROOT / "opendashcan" / "protocols" / "honda"

# Shared vehicle-bus messages from commaai/opendbc _honda_common.dbc (MIT)
# Decimal IDs from DBC BO_ lines; hex for registry.
COMMON_MSGS = """
messages:
  - arbitration_id: "0x158"
    name: ENGINE_DATA
    bus: vehicle_can
    dlc: 8
    sender: pcm
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: >
      opendbc _honda_common / platform DBC ENGINE_DATA (BO_ 344).
      ENGINE_RPM @23|16 scale 1; XMISSION_SPEED @7|16 scale 0.01 kph.
      Cluster RX for donor swap NOT PHYSICALLY_VERIFIED.
    integrity:
      checksum: {{ type: honda_nibble_v1 }}
      counter: {{ type: honda_2bit_v1 }}

  - arbitration_id: "0x17C"
    name: POWERTRAIN_DATA
    bus: vehicle_can
    dlc: 8
    sender: pcm
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: >
      opendbc POWERTRAIN_DATA (BO_ 380). Also carries ENGINE_RPM.
      Cluster RX NOT PHYSICALLY_VERIFIED.

  - arbitration_id: "0x309"
    name: CAR_SPEED
    bus: vehicle_can
    dlc: 8
    sender: pcm
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: >
      opendbc CAR_SPEED (BO_ 777) CAR_SPEED@7|16 scale 0.01 kph.
      Cluster RX NOT PHYSICALLY_VERIFIED.

  - arbitration_id: "0x191"
    name: GEARBOX
    bus: vehicle_can
    dlc: 8
    sender: pcm
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: >
      Classic Civic 2016-2021 generated DBCs: GEARBOX BO_ 401 with GEAR_SHIFTER @5|6
      (VAL_ P/R/N/D/S/L). Newer opendbc _gearbox_common.dbc redefines 401 as GEARBOX_CVT
      and adds 419 GEARBOX_AUTO with different bitfields — see conflicts.yaml.
      Confirm against the year-specific generated DBC before encoding.

  - arbitration_id: "0x1A4"
    name: VSA_STATUS
    bus: vehicle_can
    dlc: 8
    sender: vsa
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: >
      opendbc VSA_STATUS (BO_ 420). ESP_DISABLED bit present.
      Cluster warning mapping NOT PHYSICALLY_VERIFIED.

  - arbitration_id: "0x1D0"
    name: WHEEL_SPEEDS
    bus: vehicle_can
    dlc: 8
    sender: vsa
    receivers: []
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: opendbc WHEEL_SPEEDS (BO_ 464). Useful for correlation; cluster need UNKNOWN.

  - arbitration_id: "0x1C2"
    name: EPB_STATUS
    bus: vehicle_can
    dlc: 8
    sender: epb
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: opendbc EPB_STATUS (BO_ 450). EPB_ACTIVE / EPB_STATE. Not on all trims.

  - arbitration_id: "0x305"
    name: SEATBELT_STATUS
    bus: vehicle_can
    dlc: 7
    sender: body
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: opendbc SEATBELT_STATUS (BO_ 773).

  - arbitration_id: "0x405"
    name: DOORS_STATUS
    bus: vehicle_can
    dlc: 8
    sender: body
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: opendbc DOORS_STATUS (BO_ 1029). Door open + trunk bits.

  - arbitration_id: "0x374"
    name: STALK_STATUS
    bus: vehicle_can
    dlc: 8
    sender: UNKNOWN
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: opendbc STALK_STATUS (BO_ 884). Headlights / high-beam hold/flash.

  - arbitration_id: "0x37B"
    name: STALK_STATUS_2
    bus: vehicle_can
    dlc: 8
    sender: UNKNOWN
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: opendbc STALK_STATUS_2 (BO_ 891). LOW_BEAMS / HIGH_BEAMS / PARK_LIGHTS.

  - arbitration_id: "0x324"
    name: CRUISE
    bus: vehicle_can
    dlc: 8
    sender: pcm
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: opendbc CRUISE (BO_ 804). HUD speeds / trip fuel consumed. Not coolant temp.
"""

COMMON_SIGS = """
signals:
  - signal: powertrain.engine_rpm
    message:
      arbitration_id: "0x158"
      bus: vehicle_can
      name: ENGINE_DATA
      dlc: 8
    encoding:
      start_bit: 23
      length: 16
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: rpm
    transport:
      period_ms: UNKNOWN
    integrity:
      counter: {{ type: honda_2bit_v1 }}
      checksum: {{ type: honda_nibble_v1 }}
    source_module: pcm
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false
    notes: From opendbc ENGINE_DATA. Cluster display path NOT PHYSICALLY_VERIFIED.

  - signal: vehicle.speed
    message:
      arbitration_id: "0x309"
      bus: vehicle_can
      name: CAR_SPEED
      dlc: 8
    encoding:
      start_bit: 7
      length: 16
      byte_order: motorola
      signed: false
      scale: 0.01
      offset: 0
      unit: kph
    transport:
      period_ms: UNKNOWN
    integrity:
      counter: {{ type: honda_2bit_v1 }}
      checksum: {{ type: honda_nibble_v1 }}
    source_module: pcm
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false
    notes: Also XMISSION_SPEED on 0x158. Cluster RX NOT PHYSICALLY_VERIFIED.

  - signal: vehicle.odometer
    message:
      arbitration_id: "0x516"
      bus: vehicle_can
      name: ODOMETER
      dlc: 8
    encoding:
      start_bit: 7
      length: 24
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: km
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false
    notes: opendbc ODOMETER (BO_ 1302). Also partial odometer nibble on ENGINE_DATA.

  - signal: transmission.gear
    message:
      arbitration_id: "0x191"
      bus: vehicle_can
      name: GEARBOX
      dlc: 8
    encoding:
      start_bit: 5
      length: 6
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: null
    source_module: pcm
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false
    notes: GEAR_SHIFTER bitfield in opendbc VAL_ (P/R/N/D/S/L). Confirm per-year DBC.

  - signal: brakes.parking_brake
    message:
      arbitration_id: "0x1C2"
      bus: vehicle_can
      name: EPB_STATUS
      dlc: 8
    encoding:
      start_bit: 3
      length: 1
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: null
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false
    notes: EPB_ACTIVE. Mechanical parking brake platforms may differ.

  - signal: stability.vsa_warning
    message:
      arbitration_id: "0x1A4"
      bus: vehicle_can
      name: VSA_STATUS
      dlc: 8
    encoding:
      start_bit: 28
      length: 1
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: null
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false
    notes: ESP_DISABLED in opendbc. Warning-lamp semantics for cluster INFERRED.

  - signal: safety.seatbelt_driver
    message:
      arbitration_id: "0x305"
      bus: vehicle_can
      name: SEATBELT_STATUS
      dlc: 7
    encoding:
      start_bit: 13
      length: 1
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: null
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false
    notes: SEATBELT_DRIVER_LATCHED.

  - signal: body.driver_door
    message:
      arbitration_id: "0x405"
      bus: vehicle_can
      name: DOORS_STATUS
      dlc: 8
    encoding:
      start_bit: 37
      length: 1
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: null
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false

  - signal: body.passenger_door
    message:
      arbitration_id: "0x405"
      bus: vehicle_can
      name: DOORS_STATUS
      dlc: 8
    encoding:
      start_bit: 38
      length: 1
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: null
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false

  - signal: body.rear_left_door
    message:
      arbitration_id: "0x405"
      bus: vehicle_can
      name: DOORS_STATUS
      dlc: 8
    encoding:
      start_bit: 39
      length: 1
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: null
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false

  - signal: body.rear_right_door
    message:
      arbitration_id: "0x405"
      bus: vehicle_can
      name: DOORS_STATUS
      dlc: 8
    encoding:
      start_bit: 40
      length: 1
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: null
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false

  - signal: body.trunk
    message:
      arbitration_id: "0x405"
      bus: vehicle_can
      name: DOORS_STATUS
      dlc: 8
    encoding:
      start_bit: 41
      length: 1
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: null
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false

  - signal: lighting.high_beam
    message:
      arbitration_id: "0x37B"
      bus: vehicle_can
      name: STALK_STATUS_2
      dlc: 8
    encoding:
      start_bit: 34
      length: 1
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: null
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false
    notes: HIGH_BEAMS on STALK_STATUS_2. Turn indicators still UNKNOWN in common DBC.

  - signal: lighting.low_beam
    message:
      arbitration_id: "0x37B"
      bus: vehicle_can
      name: STALK_STATUS_2
      dlc: 8
    encoding:
      start_bit: 35
      length: 1
      byte_order: motorola
      signed: false
      scale: 1
      offset: 0
      unit: null
    confidence: DOCUMENTED
    evidence: [{ev}]
    physical_validation: false

  - signal: fuel.level
    message:
      arbitration_id: UNKNOWN
      bus: UNKNOWN
    encoding:
      unit: percent
    confidence: UNKNOWN
    evidence: []
    physical_validation: false
    notes: Not present as a clear fuel-level signal in opendbc _honda_common.

  - signal: powertrain.coolant_temperature
    message:
      arbitration_id: UNKNOWN
      bus: vehicle_can
    encoding:
      unit: C
    confidence: UNKNOWN
    evidence: []
    physical_validation: false
    notes: Not clearly identified in opendbc _honda_common (do not confuse CRUISE 0x324).

  - signal: lighting.left_indicator
    message:
      arbitration_id: UNKNOWN
      bus: UNKNOWN
    encoding: {{}}
    confidence: UNKNOWN
    evidence: []
    physical_validation: false
    notes: Turn stalk encoding not in _honda_common; may be platform-specific / B-CAN.

  - signal: lighting.right_indicator
    message:
      arbitration_id: UNKNOWN
      bus: UNKNOWN
    encoding: {{}}
    confidence: UNKNOWN
    evidence: []
    physical_validation: false

  - signal: vehicle.ignition_state
    message:
      arbitration_id: UNKNOWN
      bus: UNKNOWN
    encoding: {{}}
    confidence: UNKNOWN
    evidence: []
    physical_validation: false
    notes: Startup / ignition sequencing for donor cluster UNKNOWN without bench.
"""

# Fix double braces for format - I'll write files differently without .format for YAML braces


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.lstrip("\n"), encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


PLATFORMS = [
    ("civic/gen10/us", "ev_opendbc_civic10"),
    ("civic/gen11/us", "ev_opendbc_civic11"),
    ("accord/gen10/us", "ev_opendbc_accord10"),
    ("crv/gen5/us", "ev_opendbc_crv5"),
]


def main() -> None:
    # Use replace not format to avoid brace issues
    for rel, ev in PLATFORMS:
        base = PROTO / rel
        msgs = COMMON_MSGS.replace("{ev}", ev).replace("{{", "{").replace("}}", "}")
        sigs = COMMON_SIGS.replace("{ev}", ev).replace("{{", "{").replace("}}", "}")
        write(base / "messages.yaml", msgs)
        write(base / "signals.yaml", sigs)

        # Ensure ODOMETER message present (0x516 = 1302)
        # Already in signals; add to messages if missing - included via append
        # Add ODOMETER to messages file
        extra = f"""
  - arbitration_id: "0x516"
    name: ODOMETER
    bus: vehicle_can
    dlc: 8
    sender: UNKNOWN
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [{ev}]
    notes: opendbc ODOMETER (BO_ 1302).
"""
        # messages already written - append odometer before end by rewriting with include
        # Simpler: append to file
        with (base / "messages.yaml").open("a", encoding="utf-8") as f:
            f.write(extra)

    print("done platforms", len(PLATFORMS))


if __name__ == "__main__":
    main()
