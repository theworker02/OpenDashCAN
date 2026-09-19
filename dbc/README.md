# DBC files

## `opendbc/`

Vendored **MIT-licensed** subset of [commaai/opendbc](https://github.com/commaai/opendbc) Honda/Acura generated DBCs.

| File | Role |
|------|------|
| `LICENSE` / `NOTICE` / `PROVENANCE.yaml` | License + pinned commit SHA |
| `generated/*.dbc` | Selective raw downloads (not a full clone) |
| `generator/` | Small upstream fragments for cross-check |
| `index/*.json` | Structured import (messages, signals, enums, provenance) |
| `index/cross_vehicle_signal_index.json` | Taxonomy → implementations across vehicles |

**Knowledge level:** imports are `VEHICLE_PROTOCOL_DOCUMENTED` only.  
They never auto-promote to `CLUSTER_RX_CONFIRMED` / `PHYSICALLY_VERIFIED`.

## Tools

```bash
python tools/import_opendbc_honda.py
opendashcan dbc import dbc/opendbc/generated/honda_civic_touring_2016_can_generated.dbc \
  --vehicle honda.civic.gen10.us.touring_2016 --source opendbc \
  --platform honda.civic.gen10.us --output-dir dbc/opendbc/index
opendashcan dbc index --signal powertrain.engine_rpm
opendashcan dbc export honda.civic.gen10.us
python tools/dbc_import.py path/to/file.dbc -o dist/catalog.json
```

## Policy

- Prefer linking + structured import over dumping unattributed trees
- Prefer selective download over cloning the entire opendbc history
- Fuel / coolant absent from public Honda DBCs must be stated as **not in public DBC**
