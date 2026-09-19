# Source: commaai/opendbc

- **URL:** https://github.com/commaai/opendbc
- **License:** MIT
- **Organization:** comma.ai
- **Use in OpenDashCAN:** Vehicle-bus Honda DBC layouts (ENGINE_DATA, CAR_SPEED, GEARBOX, POWERTRAIN_DATA, checksum algorithm).

## Confidence

Message IDs and field layouts cited from opendbc are labeled **DOCUMENTED** /
**SUPPORTED_BY_MULTIPLE_SOURCES** when multiple Civic/Accord/CR-V DBCs agree.

**Not claimed:** Physical donor-cluster RX, gateway, ADAS, or Civic 8/9 encodings.

## Known conflict

`BO_ 401 GEARBOX` packing differs between classic generated Civic DBCs and
`opendbc/dbc/generator/honda/_gearbox_common.dbc` (GEARBOX_CVT / GEARBOX_AUTO).
OpenDashCAN records this in platform `conflicts.yaml` — do not silently merge.

## Provenance chain

```text
opendbc DBC / honda.h
  → CAN message (e.g. 0x158 ENGINE_DATA)
  → signal (e.g. ENGINE_RPM)
  → platform (honda:civic:10 / 11 / accord:10 / crv:5)
  → adaptation profile (references only — no duplicated defs)
```
