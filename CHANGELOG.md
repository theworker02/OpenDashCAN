# Changelog

All notable changes to OpenDashCAN will be documented here.

## [0.1.0] — 2026-09-19

First public release: installable **LISTEN_ONLY** desktop program (CLI + Qt) for Honda OBD/CAN research and Civic8→Civic10 cluster adaptation documentation.

### Desktop & CLI

- **Qt desktop** (`opendashcan-gui`): Live, Platform, Lookup, Gaps, Adaptation, Wiring, Research tabs; dark automotive UI
- **Honda-themed boot splash** (cluster ignition homage) with trademark disclosure; optional local `honda_logo.png` (gitignored); `--no-splash` / `OPENDASHCAN_NO_SPLASH=1`
- **Live listen**: virtual / capture replay / SocketCAN · PCAN · slcan — **LISTEN ONLY — NO TRANSMIT**
- **CLI**: `opendashcan` — info, listen, registry, plan, gaps, coverage, DBC index, validate, analyze
- Entry points: `opendashcan`, `opendashcan-gui`, `opendashcan-listen`
- Optional extras: `[gui]`, `[hw]`, `[desktop]`, `[dev]`

### Protocol & research

- Honda Civic **gen7** research package (K-line / pre–OBD-CAN negatives; encodings UNKNOWN)
- Civic **gen8** strengthened discoverability; gen9/10 vehicle + cluster packages
- Civic **gen11** notes (OpenDBC `honda_civic_ex_2022`); Accord11 / CR-V6 / Pilot4 CAN-FD **RESEARCH_REQUIRED** stubs
- Donor OpenDBC ingest with **vehicle-protocol vs cluster-RX** separation (`VEHICLE_PROTOCOL_DOCUMENTED` ≠ `CLUSTER_RX_CONFIRMED`)
- Phase 4 cluster environments, eight-axis gaps, lineage, correlate / generate-trace tooling
- Civic10 decoder/encoder + bitpack helpers (evidence-cited; NO_OUTPUT default)
- Wiring docs: OBD listen tap, bus roles, harness swap checklist + diagram assets

### Evidence & safety

- Confidence / donor_knowledge ladders; no invented CAN IDs, scales, or pinouts
- GitHub evidence issue form + submitting-evidence guide
- `EncodeMode.NO_OUTPUT` / `LinkMode.LISTEN_ONLY` defaults; TX-disabled hardware bridge
- Trademark disclosure: [`docs/TRADEMARKS.md`](docs/TRADEMARKS.md)

### Brand & media

- Rounded project logo / banner (transparent corners); GUI window icon uses clipped pixmap
- Screenshots and demo GIFs (including Honda-themed boot splash)

### Notes

- Research / software phase — **no working cluster swap claimed**
- No real vehicle captures in-repo (SYNTHETIC fixtures only)
- Not affiliated with Honda Motor Co., Ltd. or comma.ai
