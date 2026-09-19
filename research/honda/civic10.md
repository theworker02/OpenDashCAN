# Honda Civic Gen 10 (`honda.civic.gen10.us`)

Years ~2016–2021. Primary **digital cluster** target: `honda.civic.gen10.cluster.digital`.

## Documented (opendbc MIT)

- ENGINE_DATA `0x158`, POWERTRAIN_DATA `0x17C`, CAR_SPEED `0x309`, GEARBOX `0x191`
- DOORS `0x405`, SEATBELT `0x305`, EPB `0x1C2`, STALK `0x374`/`0x37B`, ODOMETER `0x516`
- **SCM_FEEDBACK `0x326`** — LEFT_BLINKER / RIGHT_BLINKER (Civic hatchback EX 2017 DBC)
- STEERING_SENSORS `0x14A`, ACC_HUD `0x30C`
- Honda nibble checksum + 2-bit counter (`honda_nibble_v1` / `honda_2bit_v1`)

Software: `Civic10VehicleDecoder` translates these into `VehicleState` (DOCUMENTED only).

## Conflicts

- GEARBOX `0x191` classic layout vs `_gearbox_common` CVT/AUTO — `conflicts.yaml`

## Still UNKNOWN in common DBC

- Fuel level, coolant temperature (CRUISE trip-fuel is not coolant)

## Not physically verified

- Donor cluster consumption of those frames alone
- Startup, gateway, ADAS, immobilizer

See protocol package + `research/honda_2009_2022_can_research.md`.
