# ODC-REC-RPI-1A — manufacturing package

**SKU:** `ODC-REC-RPI-1A`  
**Host:** Raspberry Pi Zero 2 W  
**CAN:** 1× MCP2515 @ 16 MHz → SN65HVD230 → OBD (500 kbit/s typical Honda diagnostic)  
**Mode:** LISTEN ONLY / NO TX  

This folder is the **build book** for manufacturers. It is **not** part of the Desktop app install.

| Folder | Contents |
|--------|----------|
| [`bom/`](bom/) | Production BOM, AVL, critical components, costing sheet |
| [`cad/`](cad/) | Open schematic, PCB fab notes, KiCad scaffold, OpenSCAD enclosure, harness drawing |
| [`process/`](process/) | Assembly SOP, ICT, FCT, traveler |
| [`software/`](software/) | Factory image recipe, systemd unit, config fragments |
| [`labels/`](labels/) | Label artwork text + packing list |

Upstream product intent: [`../README.md`](../README.md).  
Partner cover letter: [`../../MANUFACTURING_PARTNER_NOTE.md`](../../MANUFACTURING_PARTNER_NOTE.md).
