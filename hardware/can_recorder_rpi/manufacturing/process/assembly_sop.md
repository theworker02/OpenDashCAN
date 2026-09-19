# Assembly SOP — ODC-REC-RPI-1A

**ESD:** Class 0 handling for Pi and HAT. Ground strap required.

## 1. PCBA

1. Verify bare PCB revision silk `ODC-REC-HAT-A`.
2. SMT reflow per CM profile (SnAgCu).
3. Hand-solder 2×20 header and fuse holder if not selective-soldered.
4. Install 2A mini blade fuse.
5. Visual IPC-A-610 Class 2: no bridges on SOIC, crystal orientation correct.
6. **JP_TERM:** leave jumper **off** (open) for OBD-tap SKUs.

## 2. Cable

1. Build ASM-OBD-1M per [`../cad/harness_obd.svg`](../cad/harness_obd.svg).
2. Continuity: 4→GND, 5→GND, 6→CANH, 14→CANL, 16→VIN.
3. Isolation: VIN must not short to CANH/CANL/GND (<1 MΩ megger optional).
4. Strain-relief crimp or gland into enclosure wall.

## 3. Final assembly

1. Flash microSD ([`../software/`](../software/)); insert into Pi Zero 2 W.
2. Mount Pi on standoffs in base.
3. Mate HAT; torque M2.5 evenly.
4. Connect harness to HAT pads / connector.
5. Fit lid; apply serial + warning labels ([`../labels/`](../labels/)).
6. Bag with desiccant; record serial on traveler.

## 4. Do not

- Enable SocketCAN TX or install `cansend` in production image.
- Populate unused OBD pins.
- Substitute crystal frequency.
