# Critical components (ECO required)

Do **not** substitute these without a signed engineering change order:

| Item | Why critical |
|------|----------------|
| MCP2515 + **16.000 MHz** crystal | Device-tree overlay `oscillator=16000000` hard-coded in factory image |
| 3.3 V CAN transceiver | Pi GPIO is 3.3 V; 5 V transceiver will damage the SoC |
| 2 A VIN fuse | Fire / wiring protection for OBD pin 16 feed |
| OBD pinout 4/5/6/14/16 | Wrong pins can short battery to data lines |
| Listen-only software image | Safety property of the SKU |

Crystal load capacitors must be re-validated if the crystal MPN changes (measure frequency on scope / MCP2515 bit timing error).
