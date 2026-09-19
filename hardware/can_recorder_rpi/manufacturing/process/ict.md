# ICT / flying probe — ODC-REC-HAT-A

Minimum net checks after PCBA:

| Check | Method | Pass |
|-------|--------|------|
| VIN_RAW → F1 → VIN_PROT continuity | Probe | < 1 Ω through fuse (fuse installed) |
| Reverse diode orientation | Optical + diode mode | Blocks reverse |
| +5V rail to GND | Resistance power-off | Not shorted |
| +3V3 to GND | Resistance power-off | Not shorted |
| CANH/CANL to GND | Resistance | Not shorted (ESD may read ~MΩ) |
| SPI nets CE0/SCLK/MOSI/MISO/INT | Continuity to header pins | Per netlist |
| Crystal presence | Optical | Y1 + both load caps |

Optional powered ICT: inject 12 V limited to 500 mA; expect +5 V ±0.15 V with Pi **not** attached (or with dummy load 1 A).
