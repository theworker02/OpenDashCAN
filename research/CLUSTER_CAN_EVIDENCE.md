# Cluster CAN evidence log

**Purpose:** Record cluster-facing claims with exact demonstrated facts.  
**Policy:** Forum / community posts default to `COMMUNITY_RESEARCH` / `COMMUNITY_REPORTED`.  
Do **not** promote to `CLUSTER_RX_CONFIRMED`, `CAPTURE_VERIFIED`, `PHYSICALLY_VERIFIED`, or `BENCH_VERIFIED` without in-repo capture or controlled bench evidence.

---

## Evidence EV-CX-001 — CivicX 2020 Si cluster swap (protocol notes)

| Field | Value |
|-------|-------|
| evidence_id | EV-CX-001 |
| source_type | COMMUNITY_RESEARCH |
| confidence | COMMUNITY_REPORTED |
| knowledge_level | UNKNOWN (cluster RX not OpenDashCAN-confirmed) |
| title | 2020 Civic Si Cluster Swap |
| url | https://www.civicx.com/forum/threads/2020-civic-si-cluster-swap.71566/ |
| vehicle_reported | 2020 Honda Civic Sport Hatch (host) + 2020 Civic Si digital cluster (donor) |
| bus_reported | F-CAN C (author: easiest access behind radio on 2020–2021) |
| can_ids_discussed | `0x158`, `0x17C` |
| methodology_reported | Reverse-engineered internal CAN message protocol with help from comma.ai community; VBA macro for checksum manipulation; dataset of **over 100,000 messages** from `0x158` and `0x17C` on a **2020 Honda Civic Hatch** |
| checksum | Author states Honda-style checksum required (“data has to be manipulated pretty heavily for the checksum”); aligns with known opendbc Honda nibble checksum at vehicle-bus level — **cluster acceptance not independently verified here** |
| reported_physical_result | Author later reports Sport Mode working, ADS errors canceled, **“RPM works”** on their vehicle with a prototype adapter; overheating board temporarily lost tach |
| support_scope_claimed | Author: only **6-speed manual** cars with **stock digital** clusters supported at prototype stage; analog→digital not validated by them |
| odometer | Separate programming / reprogramming discussed — not a CAN encoding claim |

### What this source **demonstrates**

1. Community interest and a claimed working **same-generation** digital cluster swap (2020 Hatch ↔ 2020 Si cluster).  
2. Author treated `0x158` / `0x17C` as relevant frames and reverse-engineered **checksum handling** enough to process a large capture.  
3. Author **reports** tach/RPM function after their adapter ran — **anecdotal physical result**.

### What this source does **not** demonstrate

1. Published bit-accurate ENGINE_RPM layout unique to the cluster (opendbc already documents vehicle-bus ENGINE_RPM on these IDs).  
2. That `0x158` alone moves the tach without other frames.  
3. Timing tables, full ClusterEnvironment, or gateway-independent RX.  
4. Reproducible OpenDashCAN `CAN_CAPTURE` / `PHYSICAL_TEST` artifacts.

### OpenDashCAN labeling

| Claim | Label |
|-------|-------|
| `0x158`/`0x17C` exist on Civic PT bus with ENGINE_RPM | `VEHICLE_PROTOCOL_DOCUMENTED` (opendbc) |
| CivicX author used those IDs for swap work | `COMMUNITY_RESEARCH` |
| Tach moves because cluster RX of `0x158` | **Not confirmed** in-repo — requires capture + bench |

---

## Evidence EV-CX-002 — CivicX “Decoding the CAN BUS”

| Field | Value |
|-------|-------|
| evidence_id | EV-CX-002 |
| url | https://www.civicx.com/forum/threads/decoding-the-can-bus.94513/ |
| source_type | COMMUNITY_RESEARCH |
| claim | Community members point to comma.ai panda/cabana and opendbc Honda DBCs for 10th-gen Civic F-CAN decoding |
| knowledge_level | Points to opendbc → use `VEHICLE_PROTOCOL_DOCUMENTED` from DBC, not from the forum post itself |

---

## Evidence EV-BCAN-001 — Honda-Civic-B-CAN

| Field | Value |
|-------|-------|
| evidence_id | EV-BCAN-001 |
| repo | https://github.com/vanillagorillaa/Honda-Civic-B-CAN |
| source_type | OPEN_SOURCE_CODE / COMMUNITY_RESEARCH |
| vehicles | 2016 Civic, 2017 CR-V BCM 36-pin tap claimed |
| claim | Hardware tap of B-CAN (~150 kbps) and optional forward onto F-CAN via panda gateway for visibility of body features (BSI, lights, climate, etc.) |
| cross_ref | Vendored `honda_crv_ex_2017_body_generated.dbc` only defines BSM extended IDs — **not** a full B-CAN lighting DBC |
| cluster relevance | UNKNOWN — body bus ≠ proven cluster gauge bus |

---

## Evidence EV-HCAN-001 — HondaCAN (Accord)

| Field | Value |
|-------|-------|
| evidence_id | EV-HCAN-001 |
| repo | https://github.com/Ldalvik/HondaCAN |
| vehicle | 2016 Honda Accord LX (author-tested) |
| claim | ESP32/Macchina library with vehicle profiles; fingerprinting approach inspired by opendbc |
| cluster relevance | UNKNOWN — not a cluster RX study |

---

## Hypotheses (not facts)

- H1: Donor Civic10/11 digital clusters consume ENGINE_DATA `0x158` for tach — **plausible** given opendbc + CivicX reports; **unconfirmed** as `CLUSTER_RX_CONFIRMED`.  
- H2: F-CAN C is the practical tap for 10th-gen digital clusters behind the radio — COMMUNITY_RESEARCH.  
- H3: Missing ADAS/EPB/TPMS messages cause lamp faults on Si clusters in non-Si cars — COMMUNITY_RESEARCH / feature config, not signal encoding.

---

## Promotion checklist (for future work)

To raise a signal to `CLUSTER_RX_CONFIRMED`:

1. Capture on the **cluster bus segment** with ignition cycle  
2. Correlate signal change ↔ gauge/lamp change  
3. Record ID, DLC, period, counter, checksum  
4. Prefer bench TX of single frames with `PHYSICAL_TEST` evidence filed under `captures/`  

Until then, keep donor protocol as `VEHICLE_PROTOCOL_DOCUMENTED` and cluster environment as incomplete.

---

## Phase 4 classification (Civic10)

| ID | Class | Basis |
|----|-------|-------|
| `0x158` / `0x17C` | `CLUSTER_LIKELY_RX` | opendbc + EV-CX-001 COMMUNITY_RESEARCH — **not** CONFIRMED |
| `0x309`, `0x191`, `0x326`, … | `DISPLAY_RELEVANT` | Taxonomy / display heuristics — **not** CLUSTER_RX |
| Fuel / coolant | ABSENT | Explicit public DBC absence |

See `clusters/civic10/` and `research/CLUSTER_GAP_REPORT.md`.
