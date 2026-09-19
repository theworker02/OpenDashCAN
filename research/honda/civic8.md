# Honda Civic Gen 8 (`honda.civic.gen8.us`)

Years ~2006–2011 (includes 2009–2011 in the 2009–2022 research window).
Reference adaptation source: US R18 automatic (`honda.civic.gen8.us.r18.auto`).

Registry / GUI aliases: `honda:civic:8`, `honda-civic8`, `honda_civic_8th_gen`,
`honda.civic.gen8.us.r18.auto`. Discoverable via `opendashcan registry vehicles`.

## Documented

- F-CAN 500 kbps, B-CAN ~33.33 kbps, gauge gateway (OEM literature)
- OBD-II CAN pins 6/14 (AiM Civic_US; Racelogic 2005–2011)
- **Channel names only** from AiM / Racelogic (RPM, SpeedVeh, wheel speeds, WaterTemp, …)

## Community

- Speculative IDs `0x194` / `0x494` / `0x694` — COMMUNITY_REPORTED, **no encodings**

## Unknown

- All powertrain/body **byte layouts** needed for cluster adaptation
- Checksum / counter algorithm on Civic 8 F-CAN

## Index vs neighbors

| Gen | Diagnostic / bus headline |
|-----|---------------------------|
| [gen7](civic7.md) | ISO 9141-2 K-line; no public F-CAN DBC |
| **gen8 (this)** | F-CAN/B-CAN bitrates DOCUMENTED; encodings UNKNOWN |
| [gen9](civic9.md) | OBD CAN 500 kbps + channel names; encodings UNKNOWN |

Protocol package: `opendashcan/protocols/honda/civic/gen8/us/`.
Also see `research/civic8_sources.md` and `research/honda_2009_2022_can_research.md`.
