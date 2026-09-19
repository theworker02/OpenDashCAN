# Honda Civic 8th gen (FA/FG, ~2006–2011)

## Role in OpenDashCAN

**Source vehicle** — decode F-CAN (and later B-CAN) into `VehicleState`.

## Known (documented)

- Platform codes FA/FG (region-dependent)
- F-CAN commonly **500 kbit/s**; B-CAN commonly **33.33 kbit/s** (service literature)
- Instrument cluster often behind a gateway

## Community-reported (not verified encodings)

Autosport Labs forum discussion cites speculative IDs including:

- `0x194`
- `0x494`
- `0x694`

OpenDashCAN tracks these as watch IDs only. **No scales or byte layouts are applied.**

## Unknown

RPM/speed/temp/fuel/gear/turn signals/lamps/doors encodings on F-CAN; checksum algorithm; cluster-gateway specifics for this generation.

## Evidence file

`opendashcan/protocols/honda/civic8/evidence.yaml`
