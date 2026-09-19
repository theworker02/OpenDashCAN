# Honda Civic Gen 11 (`honda.civic.gen11.us`)

Years ~2022–2026 (current Civic generation in OpenDashCAN). Secondary target:
`honda.civic.gen11.cluster.digital`.

## Provenance (vendored)

commaai/opendbc **`honda_civic_ex_2022`** (MIT) under `dbc/opendbc/` — vehicle-bus
message IDs/layouts DOCUMENTED (`VEHICLE_PROTOCOL_DOCUMENTED`). ENGINE_DATA family
similar to prior Civic generations; treat year-specific packing carefully.

## Latest coverage notes

- Openpilot/opendbc `HONDA_CIVIC_2022` car docs list Civic / Hatch **2022–26** and
  Hybrid **2025–26** as upstream-supported platforms.
- Upstream DBC selection may evolve (e.g. `honda_bosch_radarless_generated`); this
  package remains pinned to the **vendored** `honda_civic_ex_2022` import — do not
  invent alternate IDs without a new selective DBC import.
- Cluster RX for donor swap: **NOT PHYSICALLY_VERIFIED**.

## Beyond Civic gen11 (sibling “highest” platforms)

| Platform | OpenDBC mapping (upstream) | This repo |
|----------|----------------------------|-----------|
| Accord gen11 (2023–) | `honda_common_canfd_generated` (CAN-FD) | RESEARCH_REQUIRED stub |
| CR-V gen6 (2023–) | same CAN-FD common DBC | RESEARCH_REQUIRED stub |
| Pilot gen4 (2023–) | same CAN-FD common DBC | RESEARCH_REQUIRED stub |
| HR-V gen2 (2023–) | `honda_bosch_radarless_generated` | stub; DBC not vendored |

CAN-FD platforms are out of scope for classic F-CAN cluster-swap workflows until
selectively imported and reviewed.
