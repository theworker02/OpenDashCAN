# Honda CAN research: 2009–2022 (public sources only)

**Scope:** Existing public documentation for Honda Civic / related platforms covering
model years overlapping **2009–2022**. No invented IDs, layouts, or checksums.
No real vehicle or cluster CAN captures exist in this repository.

**Date of pass:** 2026-09-19 (updated same day — deep opendbc generator re-check)

## Evidence classes used

| Class | What it can prove | What it cannot prove |
|-------|-------------------|----------------------|
| Honda service literature | Bus names / bitrates / gateway roles | Signal byte packing |
| commaai/opendbc (MIT) | Vehicle-bus message IDs + bitfields for many 2016+ Hondas | Donor-cluster RX, B-CAN body lamps, fuel gauge |
| AiM stock-ECU PDFs | OBD channel **names** + pin 6/14 CAN | Arbitration IDs / scales |
| Racelogic Vehicle CAN PDFs | OBD baud + channel **names** | Arbitration IDs / scales |
| Autosport Labs forums | Speculative IDs (Civic 8) | Anything verified |
| rusEFI `can_dash_honda` | Emulator TX layouts for unspecified dash | OEM Civic 8/10 decode |
| Macchina / EDR papers | Occasional ID mentions (e.g. 0x309 speed on 2012) | Full bit packing |

## Sources searched this pass (raw fetch)

Fetched from `commaai/opendbc` `opendbc/dbc/generator/honda/` (MIT):

- `_honda_common.dbc`, `_bosch_2018.dbc`, `_nidec_common.dbc`, `_gearbox_common.dbc`
- `_nidec_scm_group_a.dbc`, `_nidec_scm_group_b.dbc`
- `_steering_sensors_a|b|c.dbc`, `_community.dbc`
- `honda_civic_touring_2016_can.dbc`, `honda_civic_hatchback_ex_2017_can.dbc`
- `honda_crv_touring_2016_can.dbc`, `honda_bosch_radarless.dbc`, `honda_insight_ex_2019_can.dbc`
- `acura_ilx_2016_can.dbc`

Also searched: AiM/Racelogic Civic PDFs, rusEFI dash source, web for `FUEL_LEVEL` /
`COOLANT` / `ENGINE_TEMPERATURE` SG_ definitions, Macchina Civic 2012 thread.

Local copies (optional): `research/_opendbc_fetch/` (regenerable; not evidence by itself).

## Timeline coverage

### 2009–2011 (Civic Gen 8, late FA/FG)

| Fact | Confidence | Source |
|------|------------|--------|
| F-CAN 500 kbps | DOCUMENTED | Service literature; Racelogic 2005–2011 PDF (OBD 500k) |
| B-CAN ~33.33 kbps | DOCUMENTED | Service literature |
| Gauge as F/B gateway | DOCUMENTED | Service literature |
| OBD pins 6/14 CAN | DOCUMENTED | AiM Civic_US 2006–2011; Racelogic |
| Channels RPM, SpeedVeh, wheel speeds, WaterTemp, FuelLev, … | DOCUMENTED (names) | [AiM Civic 2006–2011](https://www.aimsportsystems.com.au/download/ecu/stock/honda/Honda_Civic_2006-2011_100_eng.pdf) |
| Indicated speed / wheel speeds / yaw | DOCUMENTED (names) | [Racelogic Civic 2005–2011](https://www.racelogic.co.uk/_downloads/vbox/Vehicles/Other/Docs/Honda-Civic%202005-2011.pdf) |
| IDs 0x194 / 0x494 / 0x694 | COMMUNITY_REPORTED | Autosport Labs — **no encodings** |
| rusEFI dash TX (0x1DC tach, 0x158 speed×160, 0x324 CLT byte) | COMMUNITY_REPORTED | rusEFI emulator — **not** OEM Civic8 decode |
| All byte layouts for cluster adaptation | **UNKNOWN** | **Negative finding** — no public OEM DBC |

Package: `opendashcan/protocols/honda/civic/gen8/us/`

### 2012–2015 (Civic Gen 9)

| Fact | Confidence | Source |
|------|------------|--------|
| OBD CAN 500 kbps pins 6/14 | DOCUMENTED | [Racelogic Civic 2011–2015](https://www.racelogic.co.uk/_downloads/vbox/Vehicles/Other/Docs/Honda-Civic%202011-2015.pdf) |
| Channel names (RPM, gear, pedal, wheel speeds, handbrake, …) | DOCUMENTED (names) | Racelogic / AiM PDFs |
| Forum mention: speed ID 0x309, steer 0x153 (EDR paper) | COMMUNITY_REPORTED | [Macchina thread](https://forum.macchina.cc/t/honda-civic-2012-can-identifier/380) — **no bit packing** |
| B-CAN bitrate / full topology | UNKNOWN | Need service manual cite |
| Arbitration IDs / bit packing | **UNKNOWN** | **Negative finding** — no Civic 2012–2015 DBC in opendbc |
| opendbc coverage | None | commaai/opendbc does not ship a Civic 2012–2015 DBC |

Package: `opendashcan/protocols/honda/civic/gen9/us/`

### 2016–2021 (Civic Gen 10) — primary digital-cluster target

Populated from opendbc Honda common + platform generators (MIT):

| Arbitration (hex) | Name | Notable signals | Confidence |
|-------------------|------|-----------------|------------|
| 0x158 | ENGINE_DATA | ENGINE_RPM @23\|16, XMISSION_SPEED | DOCUMENTED |
| 0x17C | POWERTRAIN_DATA | PEDAL_GAS, BRAKE_PRESSED, ACC_STATUS | DOCUMENTED |
| 0x309 | CAR_SPEED | CAR_SPEED @7\|16 ×0.01 kph | DOCUMENTED |
| 0x191 | GEARBOX | classic GEAR_SHIFTER @5\|6 **or** `_gearbox_common` CVT | DOCUMENTED + CONFLICT |
| 0x1A4 | VSA_STATUS | ESP_DISABLED | DOCUMENTED |
| 0x1C2 | EPB_STATUS | EPB_ACTIVE | DOCUMENTED |
| 0x1D0 | WHEEL_SPEEDS | | DOCUMENTED |
| 0x305 | SEATBELT_STATUS | | DOCUMENTED |
| 0x405 | DOORS_STATUS | door/trunk bits | DOCUMENTED |
| 0x374 | STALK_STATUS | HEADLIGHTS_ON @54 | DOCUMENTED |
| 0x37B | STALK_STATUS_2 | high/low beam | DOCUMENTED |
| 0x324 | CRUISE | HUD speeds, **TRIP_FUEL_CONSUMED** (not tank level) | DOCUMENTED |
| 0x516 | ODOMETER | | DOCUMENTED |
| 0x326 | SCM_FEEDBACK | LEFT/RIGHT_BLINKER @26/27 | DOCUMENTED |
| 0x14A | STEERING_SENSORS | STEER_ANGLE @7\|16 ×−0.1 | DOCUMENTED |
| 0x30C | ACC_HUD | ACC_ON | DOCUMENTED |

**Blinker cross-check (this pass):**

| Platform generator | SCM import | Blinker ID | Bits |
|--------------------|------------|------------|------|
| Civic Touring 2016 | `_nidec_scm_group_b` | **0x326** | 26 / 27 |
| Civic Hatchback EX 2017 | `_bosch_2018` | **0x326** | 26 / 27 |
| Insight EX 2019 | `_bosch_2018` | **0x326** | 26 / 27 |
| CR-V Touring 2016 | `_nidec_scm_group_a` | **0x294** | 5 / 6 |
| Acura ILX 2016 | `_nidec_scm_group_a` | **0x294** | 5 / 6 |

Civic 10 encoder/decoder use **0x326 @26/27** (Touring 2016 Nidec-B + Hatch 2017 Bosch).

Integrity: `honda_nibble_v1` + `honda_2bit_v1` from opendbc `honda.h` — DOCUMENTED algorithm, not PHYSICALLY_VERIFIED on a donor cluster.

### Fuel level & coolant — **explicit negative findings**

| Claim | Result | Sources checked |
|-------|--------|-----------------|
| `SG_ FUEL_LEVEL` / tank gauge in opendbc Honda | **Not found** | `_honda_common`, Civic/CR-V/Insight/Bosch generators |
| `SG_ COOLANT` / `ENGINE_TEMPERATURE` bitfield | **Not found** as SG_ | Same; only openpilot `CHFFR_METRIC … 804 ENGINE_TEMPERATURE` **annotation** on CRUISE (no layout) |
| `TRIP_FUEL_CONSUMED` on 0x324 | DOCUMENTED | Trip fuel consumed — **not** fuel tank level |
| AiM `ECU_FUEL_LEV` / `ECU_ENG_T` / `WaterTemp` | Names only | AiM PDFs |
| rusEFI CLT on 0x324 byte0 | Emulator TX | Not OEM Civic decode |

**Still UNKNOWN for cluster adaptation:** fuel level, coolant temperature.

Package: `opendashcan/protocols/honda/civic/gen10/us/`

### 2022 (Civic Gen 11 start)

Bosch radarless / related generators share `_honda_common` + `_bosch_2018` family (SCM 0x326). Exact year DBC must be confirmed before encoding. Gearbox packing CONFLICT with `_gearbox_common`. Cluster RX NOT PHYSICALLY_VERIFIED.

Package: `opendashcan/protocols/honda/civic/gen11/us/`

### Related 2016–2022 targets

| Platform | Years (approx) | opendbc provenance | Blinker note |
|----------|----------------|--------------------|--------------|
| `honda.accord.gen10.us` | 2018–2022 | Bosch family (when present) | Prefer 0x326; confirm year DBC |
| `honda.crv.gen5.us` | 2017–2022 | CR-V Touring 2016 = **Nidec-A 0x294** | CONFLICT vs Bosch 0x326 |

## Explicit non-claims

1. opendbc IDs are **vehicle-bus** research — not proof a donor OEM cluster wakes or displays correctly from those frames alone.
2. AiM / Racelogic **names ≠ encodings**. Proprietary `.REF` / Race Studio templates are not reverse-engineered here.
3. Civic 8/9 remain **PARTIAL / BLOCKED** for adaptation until captures exist.
4. No TX / hardware phase — documentation + offline SYNTHETIC / RESEARCH_DOCUMENTED only (`EncodeMode.NO_OUTPUT` default).
5. No PHYSICALLY_VERIFIED claims (repo has zero real captures).

## Artifacts updated this pass

- Civic10 encoder packing expanded (gear, blinkers, doors, EPB, seatbelts, VSA, odo, powertrain, stalk)
- `Civic10VehicleDecoder` steering 0x14A + stalk headlights 0x374
- CR-V SCM conflict 0x294 vs 0x326
- Synthetic `captures/synthetic/idle_scenario.{log,asc}`
- ASC / candump ingest; CLI `--decode`; listen-only SocketCAN stub
- `research/signal_matrix.csv`, this file, `HONDA_ADAPTATION_REPORT.md`

## Next evidence needed (not fabricated)

1. Civic 8 source-vehicle CAN log with labeled RPM/speed/gear
2. Civic 10 digital cluster bench RX log
3. Year-exact DBC resolution for GEARBOX and SCM on each target VIN
4. Fuel / coolant layouts (service literature or capture — absent from public opendbc)
