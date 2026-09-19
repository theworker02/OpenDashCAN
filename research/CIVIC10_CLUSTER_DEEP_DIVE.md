# Civic 10th-gen (2016–2021) cluster deep dive

**Status:** DOCUMENTATION_ONLY — vehicle-bus strong; cluster RX mostly UNKNOWN.  
**Do not treat this as a swap guide.**

## Scope

| Item | Coverage |
|------|----------|
| Years | 2016–2021 (10th gen / FC/FK) |
| Markets | US primary (opendbc Touring 2016 / Hatch EX 2017) |
| Trims of interest | LX/EX/EX-L/Touring, Hatch, Si, Type R (Type R cluster UNKNOWN) |
| Facelift | 2019–2021 cosmetic/ADAS refresh — **no public evidence** that gauge CAN IDs changed for RPM/speed; treat as same vehicle-bus family until capture proves otherwise |

## Profiles (split only when evidence requires)

| Profile id | When to use | Evidence |
|------------|-------------|----------|
| `civic10_base_2016_2021` | Default | Shared opendbc ENGINE_DATA / CAR_SPEED family |
| `civic10_touring` | Touring digital cluster donor | `honda_civic_touring_2016_can_generated.dbc` |
| `civic10_hatch_ex_2017` | Hatch EX donor | Hatch 2017 DBC — lineage may diverge on some msgs |
| `civic10_si` | Si digital cluster | CivicX COMMUNITY_RESEARCH (same-gen swap notes); ADAS/EPB extras UNKNOWN |

**Do not invent** separate encodings for pre/post facelift without DBC or capture diffs.

## Strongest public donor model (vehicle bus)

From vendored opendbc (MIT) + registry YAML:

| Function | ID | Message | Layout | Knowledge |
|----------|-----|---------|--------|-----------|
| Tach / RPM | `0x158` | ENGINE_DATA | ENGINE_RPM @23\|16 scale 1 | VEHICLE_PROTOCOL_DOCUMENTED; CLUSTER_LIKELY_RX (CivicX) |
| RPM alt | `0x17C` | POWERTRAIN_DATA | ENGINE_RPM also present | VEHICLE_PROTOCOL_DOCUMENTED; CLUSTER_LIKELY_RX |
| Speed | `0x309` | CAR_SPEED | CAR_SPEED @7\|16 scale 0.01 | DISPLAY_RELEVANT (not RX confirmed) |
| Gear | `0x191` | GEARBOX | packing **conflicts** by DBC year | PARTIAL / REQUIRES_REVIEW |
| Blinkers | `0x326` | SCM_FEEDBACK | @26/@27 on Touring/Hatch | DISPLAY_RELEVANT; conflict vs `0x294` on some platforms |
| Odometer | `0x516` | ODOMETER | opendbc | DISPLAY_RELEVANT |
| EPB | `0x1C2` | EPB_STATUS | trim-dependent | DISPLAY_RELEVANT |
| VSA | `0x1A4` | VSA_STATUS | ESP_DISABLED | DISPLAY_RELEVANT |

Integrity: `honda_nibble_v1` + `honda_2bit_v1` on vehicle bus — **cluster acceptance UNKNOWN**.

## Explicit absences

- `fuel.level`
- `powertrain.coolant_temperature`
- Clear SRS / MIL / ABS warning lamp signals in public DBC

## Community research (not confirmation)

See [`CLUSTER_CAN_EVIDENCE.md`](CLUSTER_CAN_EVIDENCE.md) EV-CX-001 / EV-CX-002.

- `0x158` / `0x17C` discussed for Si cluster swap — **COMMUNITY_RESEARCH**
- Reported “RPM works” — anecdotal; **not** `CLUSTER_RX_CONFIRMED` / `BENCH_VERIFIED`

## Part numbers

Public mapping of instrument-cluster part number → required CAN set is **incomplete** in-repo.

| Part / keyword | Notes | Status |
|----------------|-------|--------|
| Si digital cluster (2020) | Discussed on CivicX | COMMUNITY_RESEARCH — no OEM PN ↔ ID table |
| Touring digital | Donor often referenced generically | UNKNOWN PN list |
| Analog base clusters | Out of scope for digital ClusterEnvironment | — |

Contributions should cite OEM PN + photo + capture before adding rows.

## Startup / timing / gateway

All **UNKNOWN** without bench:

- Ignition / wake order
- Heartbeat requirement
- Gateway / immobilizer / ADAS lamp dependencies (Si especially)

## What remains for ClusterEnvironment

1. Confirm RX of `0x158` (and whether `0x17C` is required) at cluster connector  
2. Measure `period_ms` on the cluster tap  
3. Verify checksum rejection behavior on the cluster  
4. Document fuel/coolant/warning lamps or prove they are not CAN-driven on this cluster  
5. Capture trim-specific diffs (Si vs Touring vs Hatch)

## Adaptation note (Civic8 → Civic10)

Source Civic8 encodings are largely **UNKNOWN**. That yields `TRANSLATION=BLOCKED_SOURCE` while target donor layouts remain **DOCUMENTED**. Source UNKNOWN must not erase target documentation.
