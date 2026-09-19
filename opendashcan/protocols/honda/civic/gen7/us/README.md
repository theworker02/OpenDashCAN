# Honda Civic Gen 7 (≈2001–2005) — `honda.civic.gen7.us`

Research package for the **pre–OBD-CAN** Civic generation. Status: **active** —
diagnostic-bus facts DOCUMENTED / COMMUNITY_REPORTED; **all proprietary CAN
encodings UNKNOWN** (explicit negative findings).

## Documented / community-supported

| Topic | Confidence | Notes |
|-------|------------|-------|
| OBD-II emissions access via **K-line** (DLC pin 7) | DOCUMENTED / COMMUNITY_REPORTED | ISO 9141-2 / KWP2000 family; ~10.4 kbaud |
| OBD-CAN pins 6/14 for emissions | **Not established** for US 2001–2004 | Gen8 AiM sheets start 2006 |
| OpenDBC / public F-CAN layouts | **Absent** | Negative finding recorded in evidence catalog |

## UNKNOWN (do not invent)

- F-CAN / B-CAN bitrates and topologies comparable to gen8+
- Any arbitration IDs or byte layouts for RPM / speed / fuel / gear / lamps
- Cluster RX sets suitable for digital donor-cluster adaptation
- Checksums / counters on proprietary buses

## Boundary sources (not encodings)

- AiM Civic CAN templates: **2006–2011** (gen8) — cited only as the start of Civic OBD-CAN sheets
- Racelogic Civic **2005–2011**: OBD CAN 500 kbps + channel names; year overlap with end of gen7 — **do not** promote as US 2001–2004 proof

## Role in OpenDashCAN

Gen7 is a **research / negative-findings** source platform, not a reference adaptation
source (that remains Civic gen8 R18 auto). SAE J1979 OBD PIDs ≠ Honda cluster protocol.

See `research/honda/civic7.md`.
