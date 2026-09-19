# Honda Civic Gen 8 (2006–2011) — `honda.civic.gen8.us`

Reference **source** platform for OpenDashCAN adaptations.

Discoverable via `opendashcan registry vehicles` and the GUI platform browser.
Aliases: `honda:civic:8`, `honda-civic8`, `honda_civic_8th_gen`,
`honda.civic.gen8.us.r18.auto`.

## Documented

- F-CAN @ 500 kbps, B-CAN @ ~33.33 kbps (OEM service literature)
- Gauge as F-CAN/B-CAN gateway (OEM literature)
- AiM Civic_US / Racelogic 2005–2011: OBD CAN pins 6/14 + **channel names only**

## Community-reported (no encodings)

- Speculative IDs `0x194`, `0x494`, `0x694` (Autosport Labs / forums)

## UNKNOWN

- All signal byte layouts (RPM, speed, fuel, gear, lamps, ignition timing)
- Exact cluster RX set for donor-cluster swap

## Neighbor index

- Gen7: K-line / pre–OBD-CAN research — `honda.civic.gen7.us` / `research/honda/civic7.md`
- Gen8 (this): bus params DOCUMENTED; encodings UNKNOWN — `research/honda/civic8.md`
- Gen9: channel names — `honda.civic.gen9.us`

## Variant note

Reference vehicle: **US Civic R18 automatic** — platform alias `honda.civic.gen8.us.r18.auto`
(same protocol package; trim/engine notes only — no separate CAN definitions invented).

Phase-1 Python decoder remains `opendashcan.protocols.honda.civic8` (no-op until verified layouts exist).
