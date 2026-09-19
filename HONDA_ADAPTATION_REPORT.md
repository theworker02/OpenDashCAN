# Honda Adaptation Report

## Mission

OpenDashCAN is a **Honda OEM instrument-cluster adaptation framework**, not a universal CAN database.

```text
Source Honda → Decoder → VehicleState → ClusterEnvironment → Encoder → Donor Cluster
```

## Reference adaptation

| Field | Value |
|-------|-------|
| Source | `honda.civic.gen8.us.r18.auto` (2006–2011 Civic, R18, automatic) |
| Target | `honda.civic.gen10.cluster.digital` |
| Status | **PARTIAL** |
| Mode | DOCUMENTATION_ONLY |
| Real CAN captures in repo | **None** |

There is no Civic 8 vehicle log and no donor-cluster bench log in this project yet.
Public documentation (service literature, AiM/Racelogic channel lists, opendbc) is the
only evidence base. `REQUIRES_CAN_CAPTURE` / `REQUIRES_BENCH_TEST` readiness states are
forward-looking blockers.

**Donor vehicle protocol (2016+)** is substantially documented via MIT opendbc imports —
see [`research/DONOR_PROTOCOL_REPORT.md`](research/DONOR_PROTOCOL_REPORT.md). That is
**vehicle-bus** knowledge (`VEHICLE_PROTOCOL_DOCUMENTED`), **not** cluster RX confirmation.

Research summary for model years **2009–2022**:
[`research/honda_2009_2022_can_research.md`](research/honda_2009_2022_can_research.md).

## Multi-target (one decoder → many clusters)

Same Civic8 decoder feeds stub/documented encoders for:

- `honda.civic.gen10.cluster.digital` (Civic10 encoder; default NO_OUTPUT)
- `honda.civic.gen11.cluster.digital` (stub NO_OUTPUT)
- `honda.accord.gen10.cluster.digital` (stub NO_OUTPUT)
- `honda.crv.gen5.cluster.digital` (stub NO_OUTPUT)

## Known vs UNKNOWN (keep donor vs cluster distinct)

### Vehicle-bus DOCUMENTED (opendbc MIT — not cluster RX)

- Civic10/11 / Accord10 / CR-V5 / Fit3 / Insight3 / Odyssey5 message **IDs and layouts**
  imported under `dbc/opendbc/` with commit SHA provenance
- `ENGINE_DATA` `0x158`, `POWERTRAIN_DATA` `0x17C`, `CAR_SPEED` `0x309`, gearbox / VSA / EPB / odometer / stalk families
- Civic10 **turn indicators** via SCM_FEEDBACK `0x326` LEFT/RIGHT_BLINKER @26/27 (Touring 2016 / Hatch 2017 / Insight / Accord / Odyssey EX-L)
- Fit EX 2018 / CR-V Touring 2016 blinkers on SCM_FEEDBACK **`0x294` @5/6** — conflict tracked
- Honda 4-bit nibble checksum algorithm (`honda_nibble_v1`) — DOCUMENTED for listed 2016+ platforms
- `Civic10VehicleDecoder` / expanded `Civic10Encoder` (RESEARCH_DOCUMENTED / SYNTHETIC only; default NO_OUTPUT)

### Cluster-side (mostly UNKNOWN / COMMUNITY_RESEARCH)

- Whether donor clusters **require** the opendbc vehicle-bus IDs for correct display — UNKNOWN
- CivicX 2020 Si cluster-swap thread: COMMUNITY_RESEARCH on `0x158`/`0x17C` + reported “RPM works” —
  **not** `CLUSTER_RX_CONFIRMED` in OpenDashCAN (see `research/CLUSTER_CAN_EVIDENCE.md`)
- Connector pinouts, immobilizer / gateway / ADAS dependencies for swaps — UNKNOWN
- Startup / timing / cluster checksum acceptance — UNKNOWN without bench

### Not in public DBC (explicit)

- Fuel tank level (`fuel.level`)
- Coolant temperature (`powertrain.coolant_temperature`)
- Clear SRS / MIL / ABS warning-lamp signals

### Source Civic8/9

- F-CAN 500 kbps / B-CAN ~33.33 kbps — DOCUMENTED (service literature)
- OBD channel **names** — DOCUMENTED (AiM / Racelogic); **byte layouts UNKNOWN** (no public DBC)

### Source Civic7 (≈2001–2005) and latest platforms

- **Civic gen7** (`honda.civic.gen7.us`): OBD emissions path is **ISO 9141-2 / K-line**
  (pin 7) — DOCUMENTED / COMMUNITY_REPORTED. No public F-CAN DBC; AiM Civic CAN sheets
  start 2006. All proprietary encodings UNKNOWN (explicit negatives).
- **Civic gen11** (`honda.civic.gen11.us`): latest Civic vehicle-bus DOCUMENTED via
  vendored `honda_civic_ex_2022`; cluster RX still NOT PHYSICALLY_VERIFIED.
- **Accord11 / CR-V6 / Pilot4**: OpenDBC maps to shared CAN-FD
  `honda_common_canfd_generated` — RESEARCH_REQUIRED stubs until selective DBC import;
  out of scope for classic F-CAN cluster swap.

### Conflicts

- **GEARBOX 0x191 packing:** classic generated DBC vs `_gearbox_common` — REQUIRES_REVIEW
- **SCM_FEEDBACK blinkers:** `0x326` @26/27 vs `0x294` @5/6 (Fit / CR-V Touring / ILX) — REQUIRES_REVIEW
- Speculative community IDs (Autosport Labs) remain COMMUNITY_REPORTED without encodings

## Blockers to COMPLETE adapters

1. **Obtain** source-vehicle CAN captures for Civic8 and decode evidence for taxonomy signals
2. **Obtain** bench / vehicle validation of target cluster RX (promote to `CLUSTER_RX_CONFIRMED`)
3. Resolve GEARBOX / blinker layout per exact year DBC / VIN
4. Integrity / startup sequencing evidence per cluster

Until then, `build-adapter --documentation-only` correctly emits **PARTIAL** or **BLOCKED** status JSON — never fabricated COMPLETE.

## Related reports

- [`research/DONOR_PROTOCOL_REPORT.md`](research/DONOR_PROTOCOL_REPORT.md)
- [`research/DONOR_SOURCES.yaml`](research/DONOR_SOURCES.yaml)
- [`research/CLUSTER_CAN_EVIDENCE.md`](research/CLUSTER_CAN_EVIDENCE.md)
- [`research/HONDA_MESSAGE_LINEAGE.md`](research/HONDA_MESSAGE_LINEAGE.md)
- [`research/CIVIC10_CLUSTER_DEEP_DIVE.md`](research/CIVIC10_CLUSTER_DEEP_DIVE.md)
- [`research/CLUSTER_GAP_REPORT.md`](research/CLUSTER_GAP_REPORT.md)
- [`research/CROSS_PLATFORM_CANDIDATES.md`](research/CROSS_PLATFORM_CANDIDATES.md)

## Phase 4 notes

- Isolated cluster environments live under `clusters/{civic10,civic11,accord10,crv5}/`
- Source Civic8 UNKNOWN → `TRANSLATION=BLOCKED_SOURCE` while Civic10 donor encodings stay DOCUMENTED
- Civic10 completeness (requirement signals): donor encoding documented **10/13** (0.769); cluster RX confirmed **0/13**; timing established **0**; integrity algorithm documented **10/13**; demonstrated (community) **1** (`powertrain.engine_rpm`)
- EncodeMode production default remains **NO_OUTPUT**
- CLI: `opendashcan cluster gaps civic10`, `correlate`, `lineage`, `conflicts`, `generate-trace`
