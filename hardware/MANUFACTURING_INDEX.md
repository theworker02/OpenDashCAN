# OpenDashCAN hardware — manufacturing package index

**Audience:** contract manufacturers (CM), PCB fab/assembly houses, cable harness shops, and engineering partners evaluating a build of **ODC-REC-RPI-1**.

**Scope:** repository documentation and open CAD only. **Not** shipped inside the OpenDashCAN Desktop Qt application or the `opendashcan` Python wheel (`pyproject.toml` packages `opendashcan*` only).

| Document | Path |
|----------|------|
| Partner cover letter | [`MANUFACTURING_PARTNER_NOTE.md`](MANUFACTURING_PARTNER_NOTE.md) |
| Product design (architecture) | [`can_recorder_rpi/README.md`](can_recorder_rpi/README.md) |
| Manufacturing package (SKU) | [`can_recorder_rpi/manufacturing/`](can_recorder_rpi/manufacturing/) |
| Full BOM + AVL | [`can_recorder_rpi/manufacturing/bom/`](can_recorder_rpi/manufacturing/bom/) |
| Open CAD (schematic, PCB, mech, harness) | [`can_recorder_rpi/manufacturing/cad/`](can_recorder_rpi/manufacturing/cad/) |
| Assembly & QA | [`can_recorder_rpi/manufacturing/process/`](can_recorder_rpi/manufacturing/process/) |
| Factory software flash | [`can_recorder_rpi/manufacturing/software/`](can_recorder_rpi/manufacturing/software/) |
| Labels & packing | [`can_recorder_rpi/manufacturing/labels/`](can_recorder_rpi/manufacturing/labels/) |

**Primary SKU (phase 1):** `ODC-REC-RPI-1A` — Raspberry Pi Zero 2 W + single MCP2515 CAN HAT, listen-only OBD recorder.

**Policy:** hardware and firmware default to **LISTEN ONLY / NO TRANSMIT**. Do not populate or enable TX paths for this SKU.
