# OpenDashCAN CAN Recorder Module — Minimal Manufacturing Design

**Product:** `ODC-REC-RPI-1` — listen-only Raspberry Pi CAN recorder for Honda F-CAN / OBD research.

**Purpose:** Capture real vehicle / bench CAN logs so OpenDashCAN can promote signals from DOCUMENTED → CAPTURE_VERIFIED. Default firmware/policy is **RX only** (no TX).

**Status:** Design package only — not a released commercial product. Automotive connection requires a trained technician. Incorrect wiring can damage the vehicle or Pi.

---

## 1. Architecture

```text
                    ┌─────────────────────────────────────┐
  OBD-II / DB9 ──►  │ ISO 11898 transceiver (SN65HVD230)  │
  CAN-H / CAN-L     │        (3.3 V CAN PHY)              │
                    └──────────────┬──────────────────────┘
                                   │ TXD/RXD (TX line tied inactive /
                                   │   or transceiver silent mode)
                    ┌──────────────▼──────────────────────┐
                    │ MCP2515 CAN controller + 16 MHz XTAL │
                    │ SPI + INT → Raspberry Pi GPIO        │
                    └──────────────┬──────────────────────┘
                                   │ SPI0
                    ┌──────────────▼──────────────────────┐
                    │ Raspberry Pi Zero 2 W / Pi 4         │
                    │ SocketCAN can0 @ 500 kbit/s          │
                    │ candump → ASC/CSV + capture manifest │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │ Automotive DC-DC 12 V → 5 V (2–3 A) │
                    │ Fuse, reverse polarity, TVS          │
                    └─────────────────────────────────────┘
```

Listen-only policy options (pick one for the build):

1. **Software:** SocketCAN up without TX apps; OpenDashCAN hardware layer keeps `LinkMode.LISTEN_ONLY`.
2. **Hardware (preferred for manufacturing):** omit TX path or hold MCP2515 TXREQ unused; optional silent-mode transceiver footprint.

## 2. Variants

| SKU | Host | CAN channels | Notes |
|-----|------|--------------|-------|
| ODC-REC-RPI-1A | Pi Zero 2 W | 1× MCP2515 | Minimal OBD logger |
| ODC-REC-RPI-1B | Pi 4 (2 GB) | 1× MCP2515 | More storage / USB |
| ODC-REC-RPI-2 | Pi 4 | 2× MCP2515 | Future F-CAN + B-CAN (33.3 k) |

Phase-1 manufacturing target: **1A**.

## 3. Electrical design (minimal HAT)

### 3.1 Power

| Net | Spec |
|-----|------|
| VIN | Vehicle 12 V (OBD pin 16) or dedicated fused tap |
| Range | 9–16 V continuous; survive 18 V load dump with TVS |
| Fuse | 2 A mini blade on VIN |
| Reverse | Series Schottky or ideal-diode |
| DC-DC | Buck 5 V / ≥2.5 A (Pi Zero 2 W peak) |
| 3V3 | From Pi rail for MCP2515 + SN65HVD230 |

Do **not** power the Pi solely from OBD pin 16 without a proper buck — USB-C PD bricks are fine for bench-only builds.

### 3.2 CAN PHY

| Part | Role |
|------|------|
| MCP2515-I/SO | CAN 2.0B controller, SPI |
| 16.000 MHz crystal + load caps | MCP2515 oscillator (match dtoverlay `oscillator=16000000`) |
| SN65HVD230D | 3.3 V high-speed transceiver |
| 120 Ω | Termination — **jumpered OFF** when tapping mid-bus / OBD (vehicle already terminated) |
| Common-mode choke + 100 pF CM | Optional EMI |
| ESD diodes (e.g. PESD1CAN) | CAN-H / CAN-L to GND |

### 3.3 OBD-II pinout (vehicle side)

| Pin | Function | Recorder |
|-----|----------|----------|
| 4 | Chassis GND | GND |
| 5 | Signal GND | GND (tie to 4) |
| 6 | CAN-H | CANH |
| 14 | CAN-L | CANL |
| 16 | Battery + | VIN (fused) |

Honda Civic OBD diagnostic CAN is typically **500 kbit/s** (matches Racelogic / AiM docs for Civic OBD).

### 3.4 Pi SPI wiring (1A)

| MCP2515 | Pi BCM |
|---------|--------|
| /CS | CE0 (GPIO8) |
| SCK | GPIO11 |
| SI | GPIO10 (MOSI) |
| SO | GPIO9 (MISO) |
| INT | GPIO25 |
| RESET | 3V3 via 10 k pull-up (optional RC) |

## 4. Mechanical / enclosure

- 3D-printed or off-the-shelf ABS box ≥ 90×60×30 mm (Zero 2 W + HAT)
- Cable exit: OBD male pigtail 0.5–1.0 m, strain relief
- Mount: Velcro / zip-tie loop under dash (non-permanent)
- Label: `LISTEN ONLY — NO TX`, SKU, serial, fuse rating
- LED: power (green), CAN activity (yellow via MCP2515 RX interrupt GPIO or software)

## 5. BOM (prototype qty 1)

See [`bom.csv`](bom.csv). Approximate prototype cost USD ~70–110 depending on Pi stock.

## 6. PCB / fab notes

- 2-layer FR-4, 1.6 mm, ENIG optional
- Pi HAT outline (65×56.5 mm) with 2.54 mm stacking header
- Keep CAN differential pair short and parallel; 120 Ω footprint near connector
- Silkscreen: `TERM` jumper, `VIN polarity`, `LISTEN ONLY`
- Gerber + pick-place + BOM generated from KiCad project (future `pcb/` folder)

**No Gerbers in this pass** — schematic-level manufacturing design only.

## 7. Software image (factory flash)

1. Raspberry Pi OS Lite (64-bit)
2. `/boot/config.txt`:

```text
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25
```

3. Bring-up:

```bash
sudo ip link set can0 up type can bitrate 500000 listen-only on
candump -L can0 > /captures/session.asc
```

4. OpenDashCAN capture manifest (`schemas/capture_manifest.schema.json`) written beside the log.
5. Default user service: `odc-recorder.service` — starts listen-only dump on boot; **never** enables TX.

## 8. Manufacturing test plan

| Step | Pass criteria |
|------|---------------|
| Power | 12 V in → 5 V ±0.15 V @ 1 A load |
| SPI probe | `dmesg` shows mcp2515 / can0 |
| Loopback (bench) | Two recorders or CAN simulator; frames received |
| Vehicle smoke | OBD connected, ignition ON, `candump` shows IDs (e.g. 0x158) within 5 s |
| TX interlock | Confirm no frames leave recorder (CAN analyzer) |

## 9. Safety / compliance

- Listen-only by design for research fleet
- Do not splice into airbag / EPS high-integrity buses without isolation plan
- Fuse at VIN; disconnect before service
- FCC/CE not claimed for prototype DIY builds
- Liability: research tool, not certified automotive equipment

## 10. OpenDashCAN Desktop integration (how frames get to the PC)

This recorder is a **frame source** for OpenDashCAN Desktop on a PC — not an in-car flash tool.

Typical path:

1. Pi: `candump -L can0 > /captures/session.log` (listen-only interface)
2. Copy the log to the PC (USB / SCP / share)
3. Decode on the PC:

```bash
pip install -e ".[gui,hw]"
opendashcan listen --capture path/to/session.log --vehicle honda.civic.gen10.us
opendashcan-gui   # Live tab → Browse… → Play file
```

Or point a PC SocketCAN/PCAN/slcan adapter at the same OBD tap and run `opendashcan listen --interface …` (still LISTEN_ONLY).

Captured ASC/CSV may also land under `captures/community/` + manifest → feed `Civic10VehicleDecoder` / future Civic8 decode → promote confidence when validated.

Related software:

- `opendashcan listen` / GUI **Live** tab — PC-side sniff + decode
- `opendashcan/hw/listen.py` — python-can listen-only open
- `opendashcan/hardware/interfaces.py` (`LinkMode.LISTEN_ONLY`)
