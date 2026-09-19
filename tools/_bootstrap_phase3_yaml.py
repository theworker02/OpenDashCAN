#!/usr/bin/env python3
"""One-shot bootstrap for Phase 3 protocol YAML / adaptation stubs / research docs."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTO = ROOT / "opendashcan" / "protocols" / "honda"


def w(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.lstrip("\n") if text.startswith("\n") else text, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


# ---------------------------------------------------------------------------
# Civic 8 (2006-2011) — reference source
# ---------------------------------------------------------------------------
C8 = PROTO / "civic" / "gen8" / "2006_2011"

w(
    C8 / "vehicle.yaml",
    """
platform_id: honda:civic:8
manufacturer: honda
model: civic
generation: 8
platform: FA/FG
years:
  start: 2006
  end: 2011
markets: [US, CA, EU, JP]
engines: [R18, K20Z3, R16]
transmissions: [manual, automatic]
protocols: [CAN]
roles: [source]
aliases:
  - honda_civic_8th_gen
  - honda-civic8
  - honda:civic:8:r18:auto
status:
  research: active
  physical_validation: incomplete
notes:
  - Reference adaptation source is US-market Civic with R18 + automatic (variant honda:civic:8:r18:auto).
  - F-CAN / B-CAN bitrates documented from Honda service literature.
  - Speculative Autosport Labs arbitration IDs are COMMUNITY_REPORTED without encodings.
  - No verified byte layouts for RPM/speed/fuel/gear on Civic 8 in this repository.
""",
)

w(
    C8 / "buses.yaml",
    """
buses:
  - id: f_can
    manufacturer_name: F-CAN
    protocol: CAN
    bitrate: 500000
    identifier_width: 11
    can_fd: false
    gateway_to: [b_can]
    known_modules: [pcm, abs_vsa, gauge]
    confidence: DOCUMENTED
    evidence: [ev_civic8_fcan_bitrate]
    notes: High-speed powertrain/chassis CAN at 500 kbps per Honda service manuals.
  - id: b_can
    manufacturer_name: B-CAN
    protocol: CAN
    bitrate: 33333
    identifier_width: 11
    can_fd: false
    gateway_to: [f_can]
    known_modules: [bcm, gauge]
    confidence: DOCUMENTED
    evidence: [ev_civic8_bcan_bitrate]
    notes: Body CAN ~33.33 kbps; gauge often acts as F-CAN/B-CAN gateway.
""",
)

w(
    C8 / "modules.yaml",
    """
modules:
  - module_id: pcm
    display_name: Powertrain Control Module (ECM/PCM)
    bus: f_can
    role: powertrain
    tx_ids: []
    confidence: DOCUMENTED
    evidence: [ev_civic8_fcan_bitrate]
    notes: Module presence DOCUMENTED; TX arbitration IDs UNKNOWN without captures.
  - module_id: abs_vsa
    display_name: ABS / VSA
    bus: f_can
    role: chassis
    confidence: DOCUMENTED
    evidence: [ev_civic8_fcan_bitrate]
    notes: Presence on F-CAN DOCUMENTED; message set UNKNOWN.
  - module_id: bcm
    display_name: Body Control Module
    bus: b_can
    role: body
    confidence: DOCUMENTED
    evidence: [ev_civic8_bcan_bitrate]
  - module_id: gauge
    display_name: Instrument Cluster / Gauge (gateway)
    bus: f_can
    role: cluster_gateway
    confidence: DOCUMENTED
    evidence: [ev_civic8_gauge_gateway]
    notes: Cluster participates as F-CAN/B-CAN gateway — exact donor-swap message set UNKNOWN.
""",
)

w(
    C8 / "messages.yaml",
    """
messages:
  - arbitration_id: "0x694"
    name: community_speculative_694
    bus: f_can
    dlc: UNKNOWN
    sender: UNKNOWN
    receivers: []
    period_ms: UNKNOWN
    confidence: COMMUNITY_REPORTED
    evidence: [ev_civic8_autosport_ids]
    notes: Speculative Autosport Labs / community ID. NO encoding. Do not decode.
  - arbitration_id: "0x494"
    name: community_speculative_494
    bus: f_can
    dlc: UNKNOWN
    sender: UNKNOWN
    receivers: []
    period_ms: UNKNOWN
    confidence: COMMUNITY_REPORTED
    evidence: [ev_civic8_autosport_ids]
    notes: Speculative ID only. Byte layout UNKNOWN.
  - arbitration_id: "0x194"
    name: community_speculative_194
    bus: f_can
    dlc: UNKNOWN
    sender: UNKNOWN
    receivers: []
    period_ms: UNKNOWN
    confidence: COMMUNITY_REPORTED
    evidence: [ev_civic8_autosport_ids]
    notes: Speculative ID only. Byte layout UNKNOWN.
""",
)

w(
    C8 / "signals.yaml",
    """
signals:
  - signal: powertrain.engine_rpm
    message: { arbitration_id: UNKNOWN, bus: f_can, name: UNKNOWN, dlc: UNKNOWN }
    encoding: { start_bit: UNKNOWN, length: UNKNOWN, byte_order: UNKNOWN, signed: UNKNOWN, scale: UNKNOWN, offset: UNKNOWN, unit: rpm }
    transport: { period_ms: UNKNOWN }
    integrity: { counter: { type: UNKNOWN }, checksum: { type: UNKNOWN } }
    source_module: pcm
    confidence: UNKNOWN
    evidence: []
    physical_validation: false
    notes: No verified Civic 8 F-CAN RPM layout. Need captures.

  - signal: vehicle.speed
    message: { arbitration_id: UNKNOWN, bus: f_can, name: UNKNOWN, dlc: UNKNOWN }
    encoding: { start_bit: UNKNOWN, length: UNKNOWN, byte_order: UNKNOWN, signed: UNKNOWN, scale: UNKNOWN, offset: UNKNOWN, unit: kph }
    transport: { period_ms: UNKNOWN }
    confidence: UNKNOWN
    evidence: []
    physical_validation: false
    notes: UNKNOWN — need source-vehicle captures correlated with GPS/speedo.

  - signal: powertrain.coolant_temperature
    message: { arbitration_id: UNKNOWN, bus: f_can }
    encoding: { unit: C }
    confidence: UNKNOWN
    evidence: []
    physical_validation: false

  - signal: fuel.level
    message: { arbitration_id: UNKNOWN, bus: UNKNOWN }
    encoding: { unit: percent }
    confidence: UNKNOWN
    evidence: []
    physical_validation: false

  - signal: transmission.gear
    message: { arbitration_id: UNKNOWN, bus: f_can }
    encoding: {}
    confidence: UNKNOWN
    evidence: []
    physical_validation: false

  - signal: lighting.left_indicator
    message: { arbitration_id: UNKNOWN, bus: b_can }
    encoding: {}
    confidence: UNKNOWN
    evidence: []
    physical_validation: false

  - signal: lighting.right_indicator
    message: { arbitration_id: UNKNOWN, bus: b_can }
    encoding: {}
    confidence: UNKNOWN
    evidence: []
    physical_validation: false

  - signal: vehicle.ignition_state
    message: { arbitration_id: UNKNOWN, bus: UNKNOWN }
    encoding: {}
    confidence: UNKNOWN
    evidence: []
    physical_validation: false
    notes: Ignition / power modality for cluster wake UNKNOWN without bench captures.
""",
)

w(
    C8 / "evidence" / "catalog.yaml",
    """
evidence:
  - evidence_id: ev_civic8_fcan_bitrate
    source_type: OEM_DOCUMENTATION
    source_url: null
    title: Honda Civic 8th-gen service / wiring literature (F-CAN)
    claim: F-CAN high-speed network operates at 500 kbps on 8th-gen Civic.
    confidence: DOCUMENTED
    license: proprietary_oem_docs_not_redistributed
    vehicle: honda:civic:8
    bus: f_can

  - evidence_id: ev_civic8_bcan_bitrate
    source_type: OEM_DOCUMENTATION
    source_url: null
    title: Honda Civic 8th-gen service literature (B-CAN)
    claim: B-CAN body network operates at approximately 33.33 kbps.
    confidence: DOCUMENTED
    license: proprietary_oem_docs_not_redistributed
    vehicle: honda:civic:8
    bus: b_can

  - evidence_id: ev_civic8_gauge_gateway
    source_type: OEM_DOCUMENTATION
    source_url: null
    title: Honda service manuals — instrument cluster as F-CAN/B-CAN gateway
    claim: Gauge/cluster participates as gateway between F-CAN and B-CAN.
    confidence: DOCUMENTED
    license: proprietary_oem_docs_not_redistributed
    vehicle: honda:civic:8

  - evidence_id: ev_civic8_autosport_ids
    source_type: COMMUNITY_RESEARCH
    source_url: null
    title: Autosport Labs / community forum speculation for 8th-gen Civic CAN IDs
    claim: Arbitration IDs 0x194 / 0x494 / 0x694 reported without verified byte layouts.
    confidence: COMMUNITY_REPORTED
    license: unknown_community
    vehicle: honda:civic:8
    notes: Tracked as COMMUNITY_REPORTED messages only — encodings remain UNKNOWN.
""",
)

w(
    C8 / "README.md",
    """
# Honda Civic Gen 8 (2006–2011) — `honda:civic:8`

Reference **source** platform for OpenDashCAN adaptations.

## Documented

- F-CAN @ 500 kbps, B-CAN @ ~33.33 kbps (OEM service literature)
- Gauge as F-CAN/B-CAN gateway (OEM literature)

## Community-reported (no encodings)

- Speculative IDs `0x194`, `0x494`, `0x694` (Autosport Labs / forums)

## UNKNOWN

- All signal byte layouts (RPM, speed, fuel, gear, lamps, ignition timing)
- Exact cluster RX set for donor-cluster swap

## Variant note

Reference vehicle: **US Civic R18 automatic** — platform alias `honda:civic:8:r18:auto`
(same protocol package; trim/engine notes only — no separate CAN definitions invented).

Phase-1 Python decoder remains `opendashcan.protocols.honda.civic8` (no-op until verified layouts exist).
""",
)

# ---------------------------------------------------------------------------
# Helper for opendbc-backed target platforms
# ---------------------------------------------------------------------------

OPENDBC_MSGS = """
messages:
  - arbitration_id: "0x158"
    name: ENGINE_DATA
    bus: vehicle_can
    dlc: 8
    sender: pcm
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [__EID__]
    notes: >
      opendbc vehicle-bus ENGINE_DATA. Cluster RX for donor swap NOT PHYSICALLY_VERIFIED.
      Contains XMISSION_SPEED and ENGINE_RPM among other fields (see signals.yaml).
    integrity:
      checksum:
        type: honda_nibble_v1
      counter:
        type: honda_2bit_v1

  - arbitration_id: "0x17C"
    name: POWERTRAIN_DATA
    bus: vehicle_can
    dlc: 8
    sender: pcm
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [__EID__]
    notes: opendbc POWERTRAIN_DATA. Cluster consumption NOT PHYSICALLY_VERIFIED.

  - arbitration_id: "0x309"
    name: CAR_SPEED
    bus: vehicle_can
    dlc: 8
    sender: pcm
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [__EID__]
    notes: opendbc CAR_SPEED (kph scale 0.01). Cluster RX NOT PHYSICALLY_VERIFIED.

  - arbitration_id: "0x191"
    name: GEARBOX
    bus: vehicle_can
    dlc: 8
    sender: pcm
    receivers: [cluster]
    period_ms: UNKNOWN
    confidence: DOCUMENTED
    evidence: [__EID__]
    notes: >
      opendbc GEARBOX. Exact GEAR packing can differ across DBC years —
      treat enums carefully. Cluster RX NOT PHYSICALLY_VERIFIED.
"""

OPENDBC_SIGNALS = """
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
      counter:
        type: honda_2bit_v1
      checksum:
        type: honda_nibble_v1
    source_module: pcm
    confidence: DOCUMENTED
    evidence: [__EID__]
    physical_validation: false
    notes: Vehicle-bus layout from opendbc. Cluster display need INFERRED — not bench-verified.

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
      counter:
        type: honda_2bit_v1
      checksum:
        type: honda_nibble_v1
    source_module: pcm
    confidence: DOCUMENTED
    evidence: [__EID__]
    physical_validation: false
    notes: Also XMISSION_SPEED on ENGINE_DATA 0x158. Cluster RX NOT PHYSICALLY_VERIFIED.

  - signal: transmission.gear
    message:
      arbitration_id: "0x191"
      bus: vehicle_can
      name: GEARBOX
      dlc: 8
    encoding:
      start_bit: UNKNOWN
      length: UNKNOWN
      byte_order: motorola
      signed: false
      scale: UNKNOWN
      offset: UNKNOWN
      unit: null
    transport:
      period_ms: UNKNOWN
    source_module: pcm
    confidence: DOCUMENTED
    evidence: [__EID__]
    physical_validation: false
    notes: Message ID DOCUMENTED in opendbc; field packing varies by DBC year — partial.

  - signal: fuel.level
    message:
      arbitration_id: UNKNOWN
      bus: UNKNOWN
    encoding:
      unit: percent
    confidence: UNKNOWN
    evidence: []
    physical_validation: false

  - signal: powertrain.coolant_temperature
    message:
      arbitration_id: UNKNOWN
      bus: vehicle_can
    encoding:
      unit: C
    confidence: UNKNOWN
    evidence: []
    physical_validation: false

  - signal: vehicle.ignition_state
    message:
      arbitration_id: UNKNOWN
      bus: UNKNOWN
    encoding: {}
    confidence: UNKNOWN
    evidence: []
    physical_validation: false
    notes: Cluster startup / ignition sequencing UNKNOWN pending bench captures.
"""


def opendbc_platform(
    *,
    dir_path: Path,
    platform_id: str,
    model: str,
    generation: int,
    years: tuple[int, int],
    platform_code: str,
    cluster_id: str,
    display_type: str,
    evidence_id: str,
    evidence_title: str,
    evidence_url: str,
    evidence_claim: str,
    aliases: list[str],
    roles: list[str],
    extra_vehicle_notes: list[str],
    readme: str,
    requirements: str,
    cluster_notes: list[str],
) -> None:
    w(
        dir_path / "vehicle.yaml",
        f"""
platform_id: {platform_id}
manufacturer: honda
model: {model}
generation: {generation}
platform: {platform_code}
years:
  start: {years[0]}
  end: {years[1]}
markets: [US]
engines: []
transmissions: []
protocols: [CAN]
roles: {aliases and roles or roles}
aliases:
{chr(10).join(f"  - {a}" for a in aliases)}
status:
  research: active
  physical_validation: incomplete
notes:
{chr(10).join(f"  - {n}" for n in extra_vehicle_notes)}
""",
    )
    # fix roles line - I made a mistake. Let me write roles properly
    w(
        dir_path / "vehicle.yaml",
        f"""
platform_id: {platform_id}
manufacturer: honda
model: {model}
generation: {generation}
platform: {platform_code}
years:
  start: {years[0]}
  end: {years[1]}
markets: [US]
engines: []
transmissions: []
protocols: [CAN]
roles:
{chr(10).join(f"  - {r}" for r in roles)}
aliases:
{chr(10).join(f"  - {a}" for a in aliases)}
status:
  research: active
  physical_validation: incomplete
notes:
{chr(10).join(f"  - {n}" for n in extra_vehicle_notes)}
""",
    )
    w(
        dir_path / "buses.yaml",
        f"""
buses:
  - id: vehicle_can
    manufacturer_name: UNKNOWN
    protocol: CAN
    bitrate: UNKNOWN
    identifier_width: 11
    can_fd: false
    gateway_to: []
    known_modules: [pcm, cluster]
    confidence: DOCUMENTED
    evidence: [{evidence_id}]
    notes: >
      Vehicle powertrain CAN as reflected in commaai/opendbc DBCs.
      Exact OEM bus marketing name / bitrate for this platform not asserted here
      without service-manual citation. Message IDs DOCUMENTED via opendbc.
""",
    )
    w(
        dir_path / "modules.yaml",
        f"""
modules:
  - module_id: pcm
    display_name: Powertrain Control Module
    bus: vehicle_can
    role: powertrain
    confidence: DOCUMENTED
    evidence: [{evidence_id}]
  - module_id: cluster
    display_name: Instrument Cluster
    bus: vehicle_can
    role: cluster
    confidence: INFERRED
    evidence: [{evidence_id}]
    notes: Cluster assumed RX of vehicle-bus PCM traffic — NOT PHYSICALLY_VERIFIED for donor swap.
""",
    )
    w(dir_path / "messages.yaml", OPENDBC_MSGS.replace("__EID__", evidence_id))
    w(dir_path / "signals.yaml", OPENDBC_SIGNALS.replace("__EID__", evidence_id))
    w(
        dir_path / "cluster.yaml",
        f"""
cluster_id: {cluster_id}
platform_id: {platform_id}
manufacturer: honda
vehicle: {model}
generation: {generation}
years:
  start: {years[0]}
  end: {years[1]}
part_numbers: []
display_type: {display_type}
CAN_buses: [vehicle_can]
CAN_FD: false
physical_fit: {{}}
compatibility_status: UNKNOWN
security_dependencies: []
immobilizer_dependencies: []
gateway_dependencies: []
ADAS_dependencies: []
evidence: [{evidence_id}]
notes:
{chr(10).join(f"  - {n}" for n in cluster_notes)}
""",
    )
    w(dir_path / "requirements.yaml", requirements)
    w(
        dir_path / "evidence" / "catalog.yaml",
        f"""
evidence:
  - evidence_id: {evidence_id}
    source_type: OPEN_SOURCE_CODE
    source_url: "{evidence_url}"
    title: "{evidence_title}"
    claim: "{evidence_claim}"
    confidence: DOCUMENTED
    license: MIT
    vehicle: {platform_id}
    bus: vehicle_can
    notes: >
      Vehicle-bus message IDs/layouts from opendbc. Emitting these frames does NOT
      claim physical donor-cluster compatibility. Cluster bring-up remains UNKNOWN.
""",
    )
    w(dir_path / "README.md", readme)


REQ_CIVIC10 = """
requirements:
  - signal: powertrain.engine_rpm
    message: ENGINE_DATA
    arbitration_id: "0x158"
    priority: REQUIRED
    confidence: DOCUMENTED
    evidence: [ev_opendbc_civic10]
    notes: >
      Vehicle-bus RPM DOCUMENTED in opendbc. Cluster need INFERRED (clusters typically
      display tach from PCM traffic) — NOT PHYSICALLY_VERIFIED on a donor cluster.

  - signal: vehicle.speed
    message: CAR_SPEED
    arbitration_id: "0x309"
    priority: REQUIRED
    confidence: DOCUMENTED
    evidence: [ev_opendbc_civic10]
    notes: Vehicle-bus speed DOCUMENTED; cluster RX need INFERRED — not bench-verified.

  - signal: transmission.gear
    message: GEARBOX
    arbitration_id: "0x191"
    priority: OPTIONAL
    confidence: DOCUMENTED
    evidence: [ev_opendbc_civic10]
    notes: Gear packing varies by DBC year — PARTIAL.

  - signal: fuel.level
    message: UNKNOWN
    arbitration_id: UNKNOWN
    priority: UNKNOWN
    confidence: UNKNOWN
    evidence: []
    notes: Fuel message for digital cluster UNKNOWN.

  - signal: vehicle.ignition_state
    message: UNKNOWN
    arbitration_id: UNKNOWN
    priority: REQUIRED
    confidence: UNKNOWN
    evidence: []
    notes: Startup / ignition sequencing UNKNOWN — REQUIRES_BENCH_TEST.

  - signal: powertrain.coolant_temperature
    message: UNKNOWN
    arbitration_id: UNKNOWN
    priority: COSMETIC
    confidence: UNKNOWN
    evidence: []

  - name: heartbeat_or_alive
    signal: UNKNOWN
    message: UNKNOWN
    priority: UNKNOWN
    confidence: UNKNOWN
    evidence: []
    notes: Whether a dedicated heartbeat is required is UNKNOWN.
"""

opendbc_platform(
    dir_path=PROTO / "civic" / "gen10" / "2016_2021",
    platform_id="honda:civic:10",
    model="civic",
    generation=10,
    years=(2016, 2021),
    platform_code="FC/FK",
    cluster_id="honda:civic:10:digital",
    display_type="digital",
    evidence_id="ev_opendbc_civic10",
    evidence_title="commaai/opendbc Honda Civic 10th-gen DBC (MIT)",
    evidence_url="https://github.com/commaai/opendbc",
    evidence_claim="ENGINE_DATA 0x158, POWERTRAIN_DATA 0x17C, CAR_SPEED 0x309, GEARBOX 0x191 present in Civic 10 DBCs.",
    aliases=["honda_civic_10th_gen", "honda-civic10"],
    roles=["target", "source"],
    extra_vehicle_notes=[
        "opendbc MIT vehicle-bus layouts cited for ENGINE_DATA/CAR_SPEED/GEARBOX/POWERTRAIN_DATA.",
        "Cluster RX for donor swap NOT PHYSICALLY_VERIFIED.",
        "Phase-1 encoder: opendashcan.protocols.honda.civic10",
    ],
    readme="""
# Honda Civic Gen 10 (2016–2021) — `honda:civic:10`

Target / donor **digital cluster** platform (`honda:civic:10:digital`).

## Documented (vehicle bus via opendbc MIT)

- `ENGINE_DATA` `0x158` — RPM / xmission speed fields
- `POWERTRAIN_DATA` `0x17C`
- `CAR_SPEED` `0x309`
- `GEARBOX` `0x191`
- Honda 4-bit nibble checksum + 2-bit counter (opendbc safety honda.h)

## NOT PHYSICALLY_VERIFIED

- Whether emitting the above alone wakes / drives a physical 10th-gen digital cluster
- Gateway, ADAS, startup, fuel, lamps, menus

Phase-1 Python encoder remains under `opendashcan.protocols.honda.civic10`.
""",
    requirements=REQ_CIVIC10,
    cluster_notes=[
        "Digital instrument cluster from 10th-gen Civic donor.",
        "Part numbers / connector pinouts UNKNOWN in this repo.",
        "Compatibility status UNKNOWN — documentation-only Phase 3.",
    ],
)

REQ_GENERIC = """
requirements:
  - signal: powertrain.engine_rpm
    message: ENGINE_DATA
    arbitration_id: "0x158"
    priority: REQUIRED
    confidence: DOCUMENTED
    evidence: [__EID__]
    notes: Vehicle-bus RPM DOCUMENTED in opendbc; cluster need INFERRED — not bench-verified.

  - signal: vehicle.speed
    message: CAR_SPEED
    arbitration_id: "0x309"
    priority: REQUIRED
    confidence: DOCUMENTED
    evidence: [__EID__]
    notes: Vehicle-bus speed DOCUMENTED; cluster RX need INFERRED.

  - signal: transmission.gear
    message: GEARBOX
    arbitration_id: "0x191"
    priority: OPTIONAL
    confidence: DOCUMENTED
    evidence: [__EID__]

  - signal: fuel.level
    priority: UNKNOWN
    confidence: UNKNOWN
    evidence: []

  - signal: vehicle.ignition_state
    priority: REQUIRED
    confidence: UNKNOWN
    evidence: []
    notes: Startup sequencing UNKNOWN — REQUIRES_BENCH_TEST.
"""

opendbc_platform(
    dir_path=PROTO / "civic" / "gen11" / "2022_2026",
    platform_id="honda:civic:11",
    model="civic",
    generation=11,
    years=(2022, 2026),
    platform_code="FE/FL",
    cluster_id="honda:civic:11:digital",
    display_type="digital",
    evidence_id="ev_opendbc_civic11",
    evidence_title="commaai/opendbc honda_civic_ex_2022 (MIT)",
    evidence_url="https://github.com/commaai/opendbc",
    evidence_claim="honda_civic_ex_2022 DBC documents ENGINE_DATA and related PCM messages similar to prior Civic generations.",
    aliases=[],
    roles=["target"],
    extra_vehicle_notes=[
        "Provenance: opendbc honda_civic_ex_2022 DBC (MIT).",
        "ENGINE_DATA family similar to Civic 10; treat year-specific packing carefully.",
        "Cluster RX for donor swap NOT PHYSICALLY_VERIFIED.",
    ],
    readme="""
# Honda Civic Gen 11 (2022–2026) — `honda:civic:11`

Secondary target cluster: `honda:civic:11:digital`.

Provenance: **commaai/opendbc** `honda_civic_ex_2022` (MIT). ENGINE_DATA `0x158` and related
PCM messages are DOCUMENTED on the vehicle bus. Cluster consumption for a donor swap is
**NOT PHYSICALLY_VERIFIED**.
""",
    requirements=REQ_GENERIC.replace("__EID__", "ev_opendbc_civic11"),
    cluster_notes=[
        "11th-gen Civic digital cluster — documentation-only.",
        "CAN FD / ADAS dependencies UNKNOWN pending research.",
    ],
)

opendbc_platform(
    dir_path=PROTO / "accord" / "gen10" / "2018_2022",
    platform_id="honda:accord:10",
    model="accord",
    generation=10,
    years=(2018, 2022),
    platform_code="CV",
    cluster_id="honda:accord:10:digital",
    display_type="digital",
    evidence_id="ev_opendbc_accord10",
    evidence_title="commaai/opendbc Honda Accord DBC (MIT)",
    evidence_url="https://github.com/commaai/opendbc",
    evidence_claim="Accord DBCs in opendbc document ENGINE_DATA 0x158 and related powertrain messages.",
    aliases=[],
    roles=["target"],
    extra_vehicle_notes=[
        "opendbc has Accord DBCs documenting ENGINE_DATA family messages.",
        "Cluster RX for donor swap NOT PHYSICALLY_VERIFIED.",
    ],
    readme="""
# Honda Accord Gen 10 (2018–2022) — `honda:accord:10`

Secondary target: `honda:accord:10:digital`.

Vehicle-bus `ENGINE_DATA` / related IDs DOCUMENTED via commaai/opendbc (MIT).
Donor-cluster compatibility **UNKNOWN**.
""",
    requirements=REQ_GENERIC.replace("__EID__", "ev_opendbc_accord10"),
    cluster_notes=["Accord 10 digital cluster — documentation-only; part numbers UNKNOWN."],
)

opendbc_platform(
    dir_path=PROTO / "crv" / "gen5" / "2017_2022",
    platform_id="honda:crv:5",
    model="crv",
    generation=5,
    years=(2017, 2022),
    platform_code="RW",
    cluster_id="honda:crv:5:digital",
    display_type="digital",
    evidence_id="ev_opendbc_crv5",
    evidence_title="commaai/opendbc Honda CR-V DBC (MIT)",
    evidence_url="https://github.com/commaai/opendbc",
    evidence_claim="CR-V DBCs in opendbc document ENGINE_DATA 0x158 and related powertrain messages.",
    aliases=[],
    roles=["target"],
    extra_vehicle_notes=[
        "opendbc CR-V DBCs document ENGINE_DATA family messages.",
        "Cluster RX for donor swap NOT PHYSICALLY_VERIFIED.",
    ],
    readme="""
# Honda CR-V Gen 5 (2017–2022) — `honda:crv:5`

Secondary target: `honda:crv:5:digital`.

Vehicle-bus layouts DOCUMENTED via opendbc (MIT). Physical cluster adaptation **UNKNOWN**.
""",
    requirements=REQ_GENERIC.replace("__EID__", "ev_opendbc_crv5"),
    cluster_notes=["CR-V 5 digital cluster — documentation-only."],
)

# ---------------------------------------------------------------------------
# Stub research platforms
# ---------------------------------------------------------------------------
STUBS = [
    ("civic", "gen9", "2012_2015", "honda:civic:9", 9, (2012, 2015), "FB/FG"),
    ("fit", "gen3", "2015_2020", "honda:fit:3", 3, (2015, 2020), "GK"),
    ("element", "gen1", "2003_2011", "honda:element:1", 1, (2003, 2011), "YH"),
    ("prelude", "gen5", "1997_2001", "honda:prelude:5", 5, (1997, 2001), "BB"),
    ("pilot", "gen3", "2016_2022", "honda:pilot:3", 3, (2016, 2022), "YF"),
    ("odyssey", "gen5", "2018_2025", "honda:odyssey:5", 5, (2018, 2025), "RL"),
    ("ridgeline", "gen2", "2017_2025", "honda:ridgeline:2", 2, (2017, 2025), "YK"),
    ("hrv", "gen2", "2023_2026", "honda:hrv:2", 2, (2023, 2026), "RV"),
]

for model, gen_dir, years_dir, pid, gen, years, code in STUBS:
    base = PROTO / model / gen_dir / years_dir
    w(
        base / "vehicle.yaml",
        f"""
platform_id: {pid}
manufacturer: honda
model: {model}
generation: {gen}
platform: {code}
years:
  start: {years[0]}
  end: {years[1]}
markets: []
engines: []
transmissions: []
protocols: [CAN]
roles: [source]
status:
  research: active
  physical_validation: incomplete
notes:
  - Research stub only. CAN IDs and encodings intentionally UNKNOWN.
  - Do not invent message layouts. Populate only with cited evidence.
""",
    )
    w(
        base / "buses.yaml",
        """
buses:
  - id: unknown_can
    manufacturer_name: UNKNOWN
    protocol: CAN
    bitrate: UNKNOWN
    identifier_width: UNKNOWN
    can_fd: UNKNOWN
    confidence: UNKNOWN
    evidence: []
    notes: Bus topology UNKNOWN pending service-manual / capture research.
""",
    )
    w(
        base / "README.md",
        f"""
# {pid} — research stub

Status: **UNKNOWN** protocol content. Research: **active**.

This package exists so the registry discovers the platform. No CAN IDs or
signal encodings are asserted. Contribute only with cited evidence.
""",
    )

# ---------------------------------------------------------------------------
# Adaptations
# ---------------------------------------------------------------------------
ADAPT = ROOT / "adaptations" / "civic8_r18_auto"

for target, tid, cid in [
    ("civic10_digital", "honda:civic:10", "honda:civic:10:digital"),
    ("civic11_digital", "honda:civic:11", "honda:civic:11:digital"),
    ("accord10_digital", "honda:accord:10", "honda:accord:10:digital"),
    ("crv5_digital", "honda:crv:5", "honda:crv:5:digital"),
]:
    base = ADAPT / target
    w(
        base / "adaptation.yaml",
        f"""
adaptation_id: civic8_r18_auto__{target}
source_vehicle: honda:civic:8:r18:auto
source_platform: honda:civic:8
target_cluster: {cid}
target_platform: {tid}
mode: DOCUMENTATION_ONLY
signals:
  - signal: powertrain.engine_rpm
    source_status: UNKNOWN
    target_status: DOCUMENTED
    translation: BLOCKED_SOURCE
    readiness: BLOCKED_SOURCE
    notes: Source Civic8 RPM encoding UNKNOWN; target vehicle-bus layout DOCUMENTED via opendbc.

  - signal: vehicle.speed
    source_status: UNKNOWN
    target_status: DOCUMENTED
    translation: BLOCKED_SOURCE
    readiness: BLOCKED_SOURCE
    notes: Source speed encoding UNKNOWN.

  - signal: transmission.gear
    source_status: UNKNOWN
    target_status: PARTIAL
    translation: blocked
    readiness: REQUIRES_CAN_CAPTURE
    notes: Source gear UNKNOWN; target GEARBOX ID DOCUMENTED but packing year-dependent.

  - signal: fuel.level
    source_status: UNKNOWN
    target_status: UNKNOWN
    translation: blocked
    readiness: REQUIRES_CAN_CAPTURE

  - signal: vehicle.ignition_state
    source_status: UNKNOWN
    target_status: UNKNOWN
    translation: blocked
    readiness: REQUIRES_BENCH_TEST
    notes: Cluster startup sequencing unknown on both sides without hardware.

physical_compatibility: NOT_VALIDATED
electrical_compatibility: NOT_VALIDATED
protocol_compatibility: INCOMPLETE
""",
    )
    w(
        base / "README.md",
        f"""
# Adaptation: Civic8 R18 Auto → `{cid}`

Documentation-only profile. References `honda:civic:8` + `{tid}` protocol packages —
**no duplicated CAN definitions**.

Overall readiness: **BLOCKED_SOURCE** on source encodings; target
vehicle-bus subset DOCUMENTED via opendbc but cluster RX not physically verified.
""",
    )

print("bootstrap complete")
