# Civic 10th-gen sources

| ID | Source | Notes |
|----|--------|-------|
| commaai_opendbc_civic10 | [commaai/opendbc](https://github.com/commaai/opendbc) MIT | Civic DBC messages ENGINE_DATA 0x158, POWERTRAIN_DATA 0x17C, CAR_SPEED 0x309, GEARBOX 0x191 |
| commaai_opendbc_honda_checksum | opendbc `opendbc/safety/modes/honda.h` | 4-bit checksum algorithm (VERIFIED) |
| racelogic_civic_can_channels | Racelogic 2016–2021 Civic CAN channel list | Signal **names** only — no byte layouts |
| civicx_forum_opendbc | CivicX forum discussions | Points to opendbc; not primary evidence |
| rusefi_honda_dash | rusEFI `can_dash_honda.cpp` | Different platform risk — do not treat as Civic10 verified |

Prefer citing opendbc URLs rather than vendoring generated DBC files unless license review is complete. Place redistributable DBCs under `dbc/source/` only when clearly MIT/compatible.
