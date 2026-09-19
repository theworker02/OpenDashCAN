# Honda Civic 10th Generation (donor cluster target)

**Years (approx.):** 2016–2021  
**Registry ID:** `honda-civic10`  
**Role:** Target cluster encoder  
**Status:** Research placeholder — **encoder returns no frames**

## Vehicle-bus research (opendbc, MIT)

Documented in public opendbc Honda Civic DBCs (vehicle bus — **not** cluster-swap verified):

| ID | Name | Notes |
|----|------|-------|
| 0x158 | ENGINE_DATA | ENGINE_RPM |
| 0x17C | POWERTRAIN_DATA | |
| 0x309 | CAR_SPEED | |
| 0x191 | GEARBOX | |

Checksum: `(sum of bytes) & 0xF`; often 2-bit counter — **SUPPORTED_BY_MULTIPLE_SOURCES** from opendbc.

## Non-verified related projects

- Racelogic channel **names** only
- rusEFI `can_dash_honda` — **not** treated as Civic 10 verified

## Software

```text
opendashcan signals honda-civic10
```

`Civic10ClusterEncoder.encode()` returns `[]` until VERIFIED.

## References

- [research/civic10_sources.md](../../research/civic10_sources.md)
- `opendashcan/protocols/honda/civic10/evidence.yaml`
