# Civic8 R18 Auto → Civic10 digital cluster

**Mode:** DOCUMENTATION_ONLY  
**Status:** PARTIAL  
**Adapter id:** `honda.civic.gen8.us.r18.auto__to__honda.civic.gen10.cluster.digital`

## Pipeline

```text
honda.civic.gen8.us (R18 auto)
        → Civic8 decoder
        → VehicleState (taxonomy paths)
        → ClusterEnvironment (Civic10)
        → Civic10 encoder (default NO_OUTPUT)
        → honda.civic.gen10.cluster.digital
```

## What is known

| Side | Fact | Confidence |
|------|------|------------|
| Source buses | F-CAN 500 kbps, B-CAN ~33.33 kbps | DOCUMENTED |
| Source encodings | RPM / speed / gear / fuel byte layouts | **UNKNOWN** |
| Target messages | ENGINE_DATA 0x158, CAR_SPEED 0x309, GEARBOX 0x191, POWERTRAIN_DATA 0x17C | DOCUMENTED (opendbc vehicle-bus) |
| Target cluster RX | Whether donor cluster needs these IDs | **NOT PHYSICALLY_VERIFIED** |
| Checksum | honda_nibble_v1 on documented Civic10-era platforms | DOCUMENTED (opendbc) |

## Blockers

1. Civic8 source signal encodings are UNKNOWN — no invented byte layouts.
2. Donor cluster RX / startup / immobilizer / gateway requirements are UNKNOWN.
3. Adapter status remains **PARTIAL** until captures + bench evidence exist.

## CLI

```bash
opendashcan plan honda.civic.gen8.us.r18.auto honda.civic.gen10.cluster.digital
opendashcan build-adapter honda.civic.gen8.us.r18.auto honda.civic.gen10.cluster.digital --documentation-only
opendashcan coverage --matrix adaptations
```

See also: [adaptations/civic8_r18_auto_to_civic10/adaptation.yaml](../../adaptations/civic8_r18_auto_to_civic10/adaptation.yaml).
