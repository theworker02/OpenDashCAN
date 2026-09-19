# Research report — Milestone 0.1

First project goal: adapt a **10th-gen Civic digital cluster** to an **8th-gen Civic** via CAN translation. This report states what is known vs unknown. **No claim that a cluster swap works.**

## Categories

### CONFIRMED BOTH SIDES

*None yet.* No signal has VERIFIED decode on Civic 8 **and** VERIFIED encode/consume on Civic 10 cluster hardware in this project.

### SOURCE ONLY (Civic 8)

| Item | Confidence | Notes |
|------|------------|-------|
| F-CAN @ 500 kbps | SUPPORTED_BY_MULTIPLE_SOURCES | Service manuals / repair literature |
| B-CAN @ ~33.33 kbps | SUPPORTED_BY_MULTIPLE_SOURCES | Service manuals |
| Cluster as F/B gateway | SUPPORTED_BY_MULTIPLE_SOURCES | Architecture; message set UNKNOWN |
| IDs 0x694 / 0x494 / 0x194 | COMMUNITY_REPORTED | Autosport Labs speculation; **no layouts** |

### TARGET ONLY (Civic 10 / vehicle bus)

| Item | Confidence | Notes |
|------|------------|-------|
| 0x158 ENGINE_DATA / ENGINE_RPM | SUPPORTED_BY_MULTIPLE_SOURCES | opendbc vehicle bus |
| 0x17C POWERTRAIN_DATA | SUPPORTED_BY_MULTIPLE_SOURCES | opendbc |
| 0x309 CAR_SPEED | SUPPORTED_BY_MULTIPLE_SOURCES | opendbc |
| 0x191 GEARBOX | SUPPORTED_BY_MULTIPLE_SOURCES | opendbc |
| Honda `(sum)&0xF` checksum + 2-bit counter | SUPPORTED_BY_MULTIPLE_SOURCES | opendbc conventions |

**Caveat:** Target knowledge is primarily **vehicle-bus** DBC evidence. Cluster **consumption** for a donor swap is **not** bench-verified.

### PARTIALLY UNDERSTOOD

| Item | Notes |
|------|-------|
| Dual-network Honda topology | Rates known; gateway behavior for cluster-out UNKNOWN |
| Checksum algorithm | Known algorithm; per-message applicability must be evidenced |
| rusEFI / Racelogic mentions | Names or other platforms — not Civic10 cluster proof |

### UNKNOWN

- Byte layouts for Civic 8 speed / RPM / lamps / doors / fuel / coolant
- Which messages a standalone Civic 10 cluster **requires**
- Ignition / power sequencing for donor cluster wake
- Timeout and DTC behavior with partial bus simulation
- B-CAN participation requirements for the donor cluster

## What captures we need next

1. Civic 8 F-CAN + B-CAN: idle, rev, drive (GPS), doors, lamps, key cycle  
2. Civic 10 stock vehicle: cluster-facing traffic inventory  
3. Civic 10 cluster on bench: minimal ID set to light gauges  
4. Manifested, licensed community captures under `captures/community/`

## Software status

Pipeline exists (replay → decode → state → encode → analyze). Decoders/encoders are **honest placeholders**. See [architecture.md](architecture.md) and [evidence-policy.md](evidence-policy.md).
