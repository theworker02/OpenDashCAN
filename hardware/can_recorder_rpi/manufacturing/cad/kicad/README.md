# KiCad scaffold — ODC-REC-HAT-A

This folder is intentionally lightweight: generate the full `.kicad_pro` / `.kicad_sch` / `.kicad_pcb` on the CM engineering workstation from the open netlist and outline.

## Recommended workflow (KiCad 8+)

1. Create project `ODC-REC-HAT-A`.
2. Import symbols: MCP2515, SN65HVD230, Abracon crystal, Pi 2×20 footprint (`Connector_PinHeader_2.54mm`).
3. Enter nets from [`../schematic_nets.md`](../schematic_nets.md).
4. Set board outline from [`../pcb_outline.svg`](../pcb_outline.svg) / 65×56.5 mm HAT.
5. Apply DFM rules in [`../pcb_fab_notes.md`](../pcb_fab_notes.md).
6. Export Gerbers + drill + centroid into a release zip named `ODC-REC-HAT-A_revA_gerbers.zip`.

## Listen-only layout note

Do not add a USB-CAN bridge or second MCU TX path on this SKU. If a transceiver “silent” pin exists on an AVL alternate, hard-tie it per datasheet for **receive-only** and document on the schematic sheet.

## ERC/DRC gates before fab

- Crystal load caps present
- CAN ESD footprint present
- Fuse in VIN path
- Silk includes `LISTEN ONLY — NO TX`
