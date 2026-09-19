# Public source expansion (Phase 4)

Record positive **and negative** results for remaining cluster gaps.

## Searched / revisited

| Source | Result | Cluster relevance |
|--------|--------|-------------------|
| commaai/opendbc Honda DBCs (vendored) | Positive — vehicle protocol | VEHICLE_PROTOCOL_DOCUMENTED |
| CivicX 2020 Si cluster swap | Positive as COMMUNITY_RESEARCH on 0x158/0x17C | NOT CLUSTER_RX_CONFIRMED |
| CivicX “Decoding the CAN BUS” | Points to opendbc | Use DBC labels, not forum |
| Honda-Civic-B-CAN (GitHub) | Body bus tap claims | UNKNOWN for cluster gauges |
| HondaCAN (Accord, GitHub) | Vehicle profiles | UNKNOWN cluster RX |
| Public OEM service PDFs for fuel/coolant CAN | **Negative** — no public bit layout found in Phase 4 pass | Remain ABSENT / UNKNOWN |
| Academic papers on Honda cluster RX | **Negative** — no citable open encoding found | UNKNOWN |
| Public cluster part-number ↔ CAN map | **Negative / incomplete** | See CIVIC10_CLUSTER_DEEP_DIVE.md |

## Gaps still open

- Fuel / coolant / SRS / MIL / ABS lamp encodings
- Cluster RX confirmation for any ID
- Timing tables at cluster connector
- Startup / ignition sequencing
- Civic8 byte layouts (source)

## Labeling reminder

forum ≠ CAPTURE_VERIFIED; DBC ≠ BENCH_VERIFIED / CLUSTER_RX_CONFIRMED.
