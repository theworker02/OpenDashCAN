# Honda Civic Gen 8 (2006–2011) — `honda.civic.gen8.us`

Reference **source** platform for OpenDashCAN adaptations.

## Documented

- F-CAN @ 500 kbps, B-CAN @ ~33.33 kbps (OEM service literature)
- Gauge as F-CAN/B-CAN gateway (OEM literature)

## Community-reported (no encodings)

- Speculative IDs `0x194`, `0x494`, `0x694` (Autosport Labs / forums)

## UNKNOWN

- All signal byte layouts (RPM, speed, fuel, gear, lamps, ignition timing)
- Exact cluster RX set for donor-cluster swap

## Variant note

Reference vehicle: **US Civic R18 automatic** — platform alias `honda.civic.gen8.us.r18.auto`
(same protocol package; trim/engine notes only — no separate CAN definitions invented).

Phase-1 Python decoder remains `opendashcan.protocols.honda.civic8` (no-op until verified layouts exist).
