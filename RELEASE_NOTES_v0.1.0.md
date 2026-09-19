## OpenDashCAN 0.1.0 — first public release

Installable **LISTEN_ONLY** desktop program (CLI + Qt) for Honda OBD/CAN research and Civic8→Civic10 cluster adaptation documentation.

**PyPI:** https://pypi.org/project/opendashcan/

```bash
pip install "opendashcan[desktop]"
opendashcan-gui
```

### Highlights

#### Desktop & CLI
- Qt desktop (`opendashcan-gui`): Live, Platform, Lookup, Gaps, Adaptation, Wiring, Research
- Honda-themed boot splash with trademark disclosure; `--no-splash` supported
- Live listen: virtual / capture replay / SocketCAN · PCAN · slcan — **NO TRANSMIT**
- Entry points: `opendashcan`, `opendashcan-gui`, `opendashcan-listen`

#### Protocol & research
- Civic gen7–gen11 coverage; Accord11 / CR-V6 / Pilot4 CAN-FD stubs
- Donor OpenDBC ingest with vehicle-protocol vs cluster-RX separation
- Phase 4 cluster gaps, lineage, wiring docs + diagrams

#### Manufacturing (repo only — not in the Desktop app)
- Full CM package for `ODC-REC-RPI-1A`: partner note, BOM/AVL, open CAD, assembly, ICT/FCT, factory flash
- See `hardware/MANUFACTURING_INDEX.md`

#### Safety
- `LinkMode.LISTEN_ONLY` / `EncodeMode.NO_OUTPUT` defaults
- No invented CAN IDs, scales, or pinouts
- Not affiliated with Honda Motor Co., Ltd. or comma.ai

### Notes
- Research / software phase — **no working cluster swap claimed**
- No real vehicle captures in-repo (SYNTHETIC fixtures only)
