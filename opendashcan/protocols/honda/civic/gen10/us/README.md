# Honda Civic Gen 10 (2016–2021) — `honda.civic.gen10.us`

Target / donor **digital cluster** platform (`honda.civic.gen10.cluster.digital`).

## Documented (vehicle bus via opendbc MIT)

- `ENGINE_DATA` `0x158` — RPM / xmission speed fields
- `POWERTRAIN_DATA` `0x17C`
- `CAR_SPEED` `0x309`
- `GEARBOX` `0x191`
- Honda 4-bit nibble checksum + 2-bit counter (opendbc safety honda.h)

## NOT PHYSICALLY_VERIFIED

- Whether emitting the above alone wakes / drives a physical 10th-gen digital cluster
- Gateway, ADAS, startup, fuel, lamps, menus

Phase-1 Python encoder remains under `opendashcan.protocols.honda.civic10`.
