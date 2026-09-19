# Donor Protocol Acquisition Report

**Date:** 2026-09-19  
**Mode:** DOCUMENTATION_ONLY  
**OpenDBC pin:** `4ab347baefb7473771ada0723c969c50d0c28d01` (MIT)

This report separates **vehicle-bus protocol documentation** from **donor-cluster RX confirmation**.  
Public DBC facts are **not** cluster proof.

---

## Knowledge-level model

| Level | Meaning |
|-------|---------|
| `VEHICLE_PROTOCOL_DOCUMENTED` | Present in public DBC / openpilot vehicle definitions |
| `CLUSTER_RELEVANT_SIGNAL_DOCUMENTED` | Same, and mapped to a cluster-relevant taxonomy path |
| `CLUSTER_RX_CONFIRMED` | Evidence the **cluster consumes** the frame (capture / RE / bench) |
| `CLUSTER_TIMING_CONFIRMED` | Period / scheduling confirmed for cluster |
| `CLUSTER_CHECKSUM_CONFIRMED` | Cluster-accepted checksum/counter confirmed |
| `CLUSTER_STARTUP_CONFIRMED` | Ignition / wake / gateway sequence confirmed |
| `CLUSTER_ENVIRONMENT_COMPLETE` | Full ClusterEnvironment satisfied |
| `BENCH_VERIFIED` | Physical donor-cluster bench test |

**Policy:** DBC import never auto-promotes past `VEHICLE_PROTOCOL_DOCUMENTED` / `CLUSTER_RELEVANT_SIGNAL_DOCUMENTED`.

---

## WHAT WE KNOW FROM OPENDBC

Vendored under `dbc/opendbc/` (LICENSE + NOTICE + PROVENANCE.yaml). Structured indexes: `dbc/opendbc/index/`.

| DBC file | Messages | Signals | Vehicle label |
|----------|----------|---------|---------------|
| `honda_civic_touring_2016_can_generated.dbc` | 37 | 261 | Civic10 Touring 2016 (Nidec) |
| `honda_civic_hatchback_ex_2017_can_generated.dbc` | 45 | 361 | Civic10 Hatch EX 2017 (Bosch) |
| `honda_civic_ex_2022_can_generated.dbc` | 49 | 378 | Civic11 EX 2022 (Bosch) |
| `honda_accord_2018_can_generated.dbc` | 48 | 371 | Accord10 2018 (Bosch) |
| `honda_crv_ex_2017_can_generated.dbc` | 45 | 361 | CR-V5 EX 2017 |
| `honda_crv_ex_2017_body_generated.dbc` | 2 | 4 | CR-V body CAN (BSM only) |
| `honda_crv_touring_2016_can_generated.dbc` | 31 | 227 | CR-V Touring 2016 (Nidec SCM) |
| `honda_fit_ex_2018_can_generated.dbc` | 32 | 235 | Fit3 EX 2018 (Nidec) |
| `honda_insight_ex_2019_can_generated.dbc` | 43 | 351 | Insight3 EX 2019 (Bosch) |
| `honda_odyssey_exl_2018_generated.dbc` | 35 | 252 | Odyssey5 EX-L 2018 |
| + Clarity, Acura ILX/RDX, Fit Hybrid, CR-V Executive | … | … | see `index/catalog.json` |

### Shared vehicle-bus messages (typical PT / F-CAN)

| ID | Name | Notable signals | Knowledge |
|----|------|-----------------|-----------|
| `0x158` | ENGINE_DATA | ENGINE_RPM @23\|16, XMISSION_SPEED | VEHICLE_PROTOCOL_DOCUMENTED |
| `0x17C` | POWERTRAIN_DATA | ENGINE_RPM (dup), PEDAL_GAS, BRAKE_PRESSED | VEHICLE_PROTOCOL_DOCUMENTED |
| `0x309` | CAR_SPEED | CAR_SPEED @7\|16 | VEHICLE_PROTOCOL_DOCUMENTED |
| `0x191` | GEARBOX* | GEAR_SHIFTER (layout conflicts — see below) | VEHICLE_PROTOCOL_DOCUMENTED |
| `0x1A4` | VSA_STATUS | ESP_DISABLED | VEHICLE_PROTOCOL_DOCUMENTED |
| `0x1C2` | EPB_STATUS | EPB_ACTIVE (where present) | VEHICLE_PROTOCOL_DOCUMENTED |
| `0x516` | ODOMETER | ODOMETER @7\|24 | VEHICLE_PROTOCOL_DOCUMENTED |
| `0x37B` | STALK_STATUS_2 | HIGH_BEAMS / LOW_BEAMS | VEHICLE_PROTOCOL_DOCUMENTED |

\* Classic generated DBCs use `BO_ 401 GEARBOX`; newer `_gearbox_common` may redefine packing — `REQUIRES_REVIEW`.

### Blinker layout conflict (documented)

| Platform DBC | SCM_FEEDBACK ID | LEFT/RIGHT bits |
|--------------|-----------------|-----------------|
| Civic Touring 2016, Hatch 2017, Civic 2022, Accord 2018, Insight 2019, Odyssey EX-L 2018, CR-V EX 2017 | `0x326` | @26 / @27 |
| Fit EX 2018, CR-V Touring 2016, Acura ILX 2016 | `0x294` | @5 / @6 |

Keep `conflicts.yaml` accurate — do not assume Civic blinker packing on Fit/CR-V Touring.

### CR-V body DBC

`honda_crv_ex_2017_body_generated.dbc` is **body_can** only: extended-ID BSM left/right status.  
**No** fuel, coolant, or turn-signal encodings. High value for BSM / body research, not cluster gauges.

### Not in public DBC (explicit)

Searched imported Honda/Acura SG_ names — **absent**:

- `fuel.level` — **not in public DBC**
- `powertrain.coolant_temperature` — **not in public DBC** (do not confuse `CRUISE` `0x324`)
- `safety.srs_warning` — **not in public DBC** as clear SRS lamp
- `safety.check_engine` / MIL — **not in public DBC**
- `brakes.abs_warning` — **not in public DBC**

Do **not** label these vaguely as “UNKNOWN protocol” — state **not in public DBC**.

---

## WHAT WE KNOW FROM OPENPILOT

Source: `opendbc/car/honda/values.py` (commaai/opendbc, current tree).

### Architecture (separate from signal packing)

| Family | Examples | Notes |
|--------|----------|-------|
| **HondaNidecPlatformConfig** | Civic 2016–18 Touring, Fit, Odyssey, Ridgeline, ILX, CR-V (older) | Nidec radar / PT patterns |
| **HondaBoschPlatformConfig** | Civic Bosch / 2022, Accord 2018, Insight, CR-V 5G, many newer | Bosch radar / alt radar / radarless flags |
| **HondaBoschCANFDPlatformConfig** | Accord 11G, CR-V 6G, Pilot 4G, … | CAN-FD — `honda_common_canfd_generated` **not yet vendored**; platform stubs are RESEARCH_REQUIRED |

OpenDashCAN registry stubs (mapping only, no invented IDs):

- `honda.accord.gen11.us`, `honda.crv.gen6.us`, `honda.pilot.gen4.us`
- Civic latest remains `honda.civic.gen11.us` on vendored classic `honda_civic_ex_2022`
- HR-V 2023+ stub notes upstream `honda_bosch_radarless_generated` (not vendored)

Bus FW query hints (architecture, not cluster RX):

- **Nidec PT bus** queried as bus `0`
- **Bosch PT bus** queried as bus `1` (`obd_multiplexing=False`)
- Combination meter ECU address listed as `0x18da60f1` (UDS fingerprinting — **not** a cluster CAN ID map)

**Do not assume all Civic10 networks are identical** — Touring 2016 (Nidec) vs Hatch EX 2017 (Bosch) use different generated DBC compositions even when many IDs overlap.

DBC selection is per-fingerprint via `CAR.create_dbc_map()` / platform `radar_dbc_dict(...)`.

---

## WHAT WE KNOW FROM CLUSTER-SPECIFIC REVERSE ENGINEERING

See [`CLUSTER_CAN_EVIDENCE.md`](CLUSTER_CAN_EVIDENCE.md). Summary:

| Claim | Level | Notes |
|-------|-------|-------|
| CivicX 2020 Sport Hatch ↔ Si digital cluster swap exists | COMMUNITY_RESEARCH | Forum thread |
| Author worked `0x158` / `0x17C` with Honda checksum; dataset of 100k+ frames on 2020 Hatch | COMMUNITY_RESEARCH | Does **not** by itself prove which bits drive the tach |
| Author reports “RPM works” after adapter on their vehicle | COMMUNITY_RESEARCH | Treat as **reported physical result**, not OpenDashCAN `CLUSTER_RX_CONFIRMED` / `BENCH_VERIFIED` |
| Access via **F-CAN C** behind radio (2020–2021) | COMMUNITY_RESEARCH | Naming matches Honda service “F-CAN” family |
| Sport mode / ADS error cancel claimed working | COMMUNITY_RESEARCH | Feature-specific; not protocol-complete |

**Hard rule applied:** We do **not** mark `0x158`/`0x17C` as `CLUSTER_RX_CONFIRMED` solely from forum mention. OpenDBC already documents ENGINE_RPM on those IDs as **vehicle-bus**; CivicX supports community interest in those IDs for cluster swaps but lacks reproduced OpenDashCAN capture artifacts.

---

## WHAT MULTIPLE SOURCES AGREE ON

- Honda 2016+ PT buses carry ENGINE_DATA `0x158` and POWERTRAIN_DATA `0x17C` with ENGINE_RPM @23\|16 (opendbc across Civic/Accord/CR-V/Fit/Insight/Odyssey).
- Honda 4-bit nibble checksum + 2-bit counter on many PT messages (opendbc + CivicX checksum discussion + OpenDashCAN `honda_nibble_v1`).
- Blinker arbitration is **not** universal: `0x326` vs `0x294` families (opendbc + conflicts.yaml).
- Civic8/9 lack public DBC layouts comparable to 2016+ opendbc coverage.

---

## WHAT REMAINS UNKNOWN

- Whether any donor digital cluster **requires** these vehicle-bus IDs for correct gauges
- Periods (`period_ms`) for cluster RX scheduling
- Ignition / immobilizer / gateway / ADAS dependencies for swaps
- Fuel level, coolant temp, SRS/MIL/ABS lamp encodings (not in public DBC)
- Civic8/9 byte layouts (still UNKNOWN)

---

## WHAT ACTUALLY REQUIRES A PHYSICAL CAN CAPTURE

1. Source-vehicle (e.g. Civic8) encodings for taxonomy signals  
2. Confirmation of which IDs appear on the **cluster-facing** bus segment (F-CAN C vs OBD vs gatewayed)  
3. Period / counter behavior under real ignition cycles  
4. Correlation of fuel/coolant/warning lamps if they exist outside public DBCs  

---

## WHAT ACTUALLY REQUIRES DONOR-CLUSTER BENCH TESTING

1. Promoting any signal to `CLUSTER_RX_CONFIRMED` / `BENCH_VERIFIED`  
2. Startup sequence / missing-message DTC behavior  
3. Checksum acceptance by the specific donor cluster PCB  
4. Analog→digital or trim-mismatch feature masking (CivicX EEPROM topics)  

---

## Cross-vehicle taxonomy index (opendbc import)

Query: `opendashcan dbc index --signal powertrain.engine_rpm`  
File: `dbc/opendbc/index/cross_vehicle_signal_index.json`

| Taxonomy | In public DBC? | Typical ID |
|----------|----------------|------------|
| powertrain.engine_rpm | yes | `0x158` |
| vehicle.speed | yes | `0x309` / also XMISSION_SPEED on `0x158` |
| transmission.gear | yes | `0x191` (confirm year DBC) |
| lighting.left/right_indicator | yes | `0x326` **or** `0x294` |
| lighting.high_beam | yes | `0x37B` STALK_STATUS_2 |
| brakes.parking_brake | yes (where EPB present) | `0x1C2` |
| stability.vsa_warning | partial (ESP_DISABLED) | `0x1A4` |
| fuel.level | **not in public DBC** | — |
| powertrain.coolant_temperature | **not in public DBC** | — |
| safety.srs_warning / check_engine / brakes.abs_warning | **not in public DBC** | — |

Platforms populated from full DBC indexes: Fit3, Insight3 (new), Odyssey5 — all `VEHICLE_PROTOCOL_DOCUMENTED`.

---

## Cluster candidate comparison (engineering coverage)

| Donor cluster | Documented vehicle msgs (opendbc) | Documented cluster-side msgs | Checksums | Timing | Startup | Gateway | Remaining unknowns |
|---------------|-----------------------------------|------------------------------|-----------|--------|---------|---------|-------------------|
| **Civic10 digital** | Strong (Touring 2016 + Hatch 2017 DBCs) | CivicX COMMUNITY_RESEARCH on `0x158`/`0x17C` only | Vehicle-bus DOCUMENTED; cluster acceptance UNKNOWN | UNKNOWN | UNKNOWN | F-CAN C claim COMMUNITY | Fuel/coolant/warnings; full RX set |
| **Civic11 digital** | Strong (EX 2022 DBC) | None in-repo | Same | UNKNOWN | UNKNOWN | UNKNOWN | Same + Bosch G2 / radarless variants |
| **Accord10 digital** | Strong (2018 DBC) | None in-repo | Same | UNKNOWN | UNKNOWN | UNKNOWN | Same |
| **CR-V5 digital** | Strong (EX 2017 + Touring 2016); body BSM DBC | None in-repo | Same | UNKNOWN | UNKNOWN | Body bus separate | Blinker ID family differs by year DBC |

**Greatest *documented vehicle-protocol* coverage for OpenDashCAN’s reference path:**  
**Civic10** — dual DBC generations (Nidec + Bosch), CivicX community cluster-swap literature, and existing OpenDashCAN encoder/decoder stubs.  
**Greatest *documented protocol breadth including body*:** CR-V5 (PT + body BSM DBC), but **weaker** cluster-specific RE than Civic10.

Neither has `CLUSTER_ENVIRONMENT_COMPLETE` or `BENCH_VERIFIED` in this repo.

---

## Implementation artifacts

| Path | Role |
|------|------|
| `dbc/opendbc/generated/*.dbc` | Vendored MIT DBC subset |
| `dbc/opendbc/index/*.json` | Full structured import + provenance |
| `dbc/opendbc/index/cross_vehicle_signal_index.json` | Cross-vehicle taxonomy |
| `opendashcan/dbc/__init__.py` | Full SG_/VAL_ parser + import |
| `opendashcan/core/donor_knowledge.py` | Knowledge-level enum |
| `tools/import_opendbc_honda.py` | Batch import |
| `tools/populate_fit_insight_odyssey.py` | Platform YAML from indexes |

CLI:

```bash
opendashcan dbc import dbc/opendbc/generated/honda_civic_touring_2016_can_generated.dbc \
  --vehicle honda.civic.gen10.us.touring_2016 --source opendbc --platform honda.civic.gen10.us \
  --output-dir dbc/opendbc/index
opendashcan dbc index --signal powertrain.engine_rpm
```
