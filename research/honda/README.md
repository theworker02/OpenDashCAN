# Honda research index

OpenDashCAN prioritizes **Honda source vehicles** and **Honda OEM digital clusters**.

This tree collects provenance notes. Protocol facts live in
`opendashcan/protocols/honda/**` YAML packages — research notes must not invent CAN.

## Platforms

| Platform ID | Notes |
|-------------|-------|
| `honda.civic.gen7.us` | Pre–OBD-CAN research; K-line DOCUMENTED; encodings UNKNOWN |
| `honda.civic.gen8.us` | Reference source (R18 auto variant); bus params DOCUMENTED; encodings UNKNOWN |
| `honda.civic.gen9.us` | Channel-name evidence (AiM/Racelogic); encodings UNKNOWN |
| `honda.civic.gen10.us` | Primary donor digital cluster target (opendbc DOCUMENTED) |
| `honda.civic.gen11.us` | Latest Civic (2022–2026+); opendbc honda_civic_ex_2022 DOCUMENTED |
| `honda.accord.gen10.us` | Secondary target (opendbc DOCUMENTED) |
| `honda.accord.gen11.us` | Latest Accord (2023–); CAN-FD stub — DBC not vendored |
| `honda.crv.gen5.us` | Secondary target (opendbc DOCUMENTED) |
| `honda.crv.gen6.us` | Latest CR-V (2023–); CAN-FD stub — DBC not vendored |
| `honda.pilot.gen4.us` | Latest Pilot (2023–); CAN-FD stub — DBC not vendored |
| fit / element / prelude / pilot gen3 / odyssey / ridgeline / hrv | Stubs / RESEARCH_REQUIRED |

## Cross-cutting research

- [honda_2009_2022_can_research.md](../honda_2009_2022_can_research.md) — public CAN evidence 2009–2022
- [signal_matrix.csv](../signal_matrix.csv)

## Source catalogs

- [opendbc](../sources/opendbc.md)
- [Service manuals](../sources/service_manuals.md)
- [Community / AiM / Racelogic](../sources/community.md)

## Per-platform notes

- [civic7.md](civic7.md)
- [civic8.md](civic8.md)
- [civic9.md](civic9.md)
- [civic10.md](civic10.md)
- [civic11.md](civic11.md)
- [accord10.md](accord10.md)
- [accord11.md](accord11.md)
- [crv5.md](crv5.md)
- [crv6.md](crv6.md)
- [pilot4.md](pilot4.md)
