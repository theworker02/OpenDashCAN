# PCB fabrication notes — ODC-REC-HAT-A

## Board

| Parameter | Spec |
|-----------|------|
| Outline | Raspberry Pi HAT secondary form: **65.0 × 56.5 mm** (Pi Zero compatible stack) |
| Layers | 2 |
| Thickness | 1.6 mm ±10% |
| Copper | 1 oz (35 µm) both sides |
| Finish | HASL lead-free or ENIG |
| Mask / silk | Green / white |
| Min trace/space | 0.15 mm / 0.15 mm (prefer 0.2 mm) |
| Min drill | 0.3 mm finished |

## Placement rules

1. Place U2 (transceiver) and ESD within **15 mm** of OBD cable entry / CAN connector pads.
2. Route CANH/CANL as a **parallel differential pair**, equal length ±2 mm, away from DC-DC switch node.
3. Keep crystal Y1 adjacent to U1; guard GND pour; short stubs.
4. Put JP_TERM and R_TERM near CAN entry; silkscreen `TERM ON` / default open documented on assembly print.
5. Fuse holder accessible without desoldering Pi.
6. Mark polarity for VIN and diode orientation on silk.
7. Silk text: `ODC-REC-HAT-A` · `LISTEN ONLY — NO TX` · `FUSE 2A`.

## Stacking

- 2×20 2.54 mm female header, sufficient height for Pi Zero 2 W + microSD clearance.
- 4× M2.5 mounting holes per Pi HAT mechanical (use Pi Zero hole pattern if using Zero-only).

## Outputs CM must return

- Gerbers (RS-274X) + Excellon drills
- Centroid / pick-place CSV
- IPC-356 netlist (optional)
- Stackup certificate
- Electrical test report (flying probe)

## Reference

Outline drawing: [`pcb_outline.svg`](pcb_outline.svg). Netlist: [`schematic_nets.md`](schematic_nets.md).
