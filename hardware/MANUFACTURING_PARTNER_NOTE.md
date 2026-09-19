# Manufacturing partner note — ODC-REC-RPI-1

**To:** prospective contract manufacturer / PCB assembly / harness partner  
**From:** OpenDashCAN maintainers (`https://github.com/theworker02/OpenDashCAN`)  
**Product:** `ODC-REC-RPI-1A` (phase-1) — listen-only Raspberry Pi OBD/CAN research recorder  
**Revision:** A · **Date:** 2026-09-19 · **License of this design package:** MIT (same as repository) unless a part datasheet restricts redistribution of third-party IP

---

## 1. What we need built

A small automotive-adjacent **research capture appliance**:

1. **PCB HAT** (2-layer FR-4) with MCP2515 + SN65HVD230 (or approved AVL alternate), power front-end (fused 12 V → 5 V), ESD, optional 120 Ω termination jumper.
2. **Raspberry Pi Zero 2 W** stacked via 2×20 header (customer- or CM-supplied SBC per BOM).
3. **OBD-II male pigtail** (J1962), pins **4 / 5 / 6 / 14 / 16** only, 0.5–1.0 m, strain-relieved into enclosure.
4. **Enclosure** (3D-printed ABS/PETG or off-the-shelf), labels, fuse accessible.
5. **Factory-flashed microSD** with listen-only SocketCAN image (see manufacturing/software).

This is **not** an ECU, **not** a cluster controller, and **must not transmit** on the vehicle bus in the shipped configuration.

## 2. Hard requirements (non-negotiable)

| ID | Requirement |
|----|-------------|
| R1 | Default interface bring-up uses `listen-only on` (SocketCAN). |
| R2 | No production firmware/tools that send CAN frames. |
| R3 | Hardware preference: leave MCP2515 TX unused / do not route a drive path that can key the transceiver TXD high for arbitration. |
| R4 | VIN fuse ≤ 2 A; reverse-polarity and TVS on automotive input. |
| R5 | Silkscreen and exterior label include `LISTEN ONLY — NO TX`. |
| R6 | Every unit serialized; FCT log retained ≥ 2 years (or as agreed). |

## 3. Deliverables we provide (this repo)

| Package | Location |
|---------|----------|
| Architecture & electrical intent | `hardware/can_recorder_rpi/README.md` |
| Manufacturing index | `hardware/MANUFACTURING_INDEX.md` |
| Full BOM + AVL + criticals | `hardware/can_recorder_rpi/manufacturing/bom/` |
| Open CAD (schematic SVG, PCB notes, OpenSCAD, harness) | `hardware/can_recorder_rpi/manufacturing/cad/` |
| Assembly / ICT / FCT | `hardware/can_recorder_rpi/manufacturing/process/` |
| Image flash + golden config | `hardware/can_recorder_rpi/manufacturing/software/` |
| Labels & packing | `hardware/can_recorder_rpi/manufacturing/labels/` |

**Gerber / pick-place / IPC-356:** reference design is schematic-complete with PCB fabrication notes. CM may generate production Gerbers from the KiCad project scaffold under `cad/kicad/` (or propose equivalent Altium/OrCAD with ECO approval).

## 4. What we expect from you (CM quote checklist)

Please quote and confirm:

1. NRE for PCB layout DFM (if taking ownership of Gerbers) + stencil.
2. PCB fab: 2-layer, 1.6 mm, HASL or ENIG, green solder mask, white silk, 1 oz Cu preferred.
3. PCBA: SMT + through-hole header; IPC-A-610 Class 2.
4. Cable assembly: OBD pigtail with pinout verification fixture.
5. Mech: print or source enclosure; install strain relief.
6. Programming: flash microSD from provided image; run FCT script.
7. Packaging: anti-static bag + carton + serial label.
8. Lead time for EVT (10–25 pcs), DVT (50–100), PVT (250+).
9. Country of origin / RoHS / REACH declarations for populated PCBA.
10. Change control: no AVL substitutions without written ECO.

## 5. Safety & liability framing (please include in your traveler)

- Research / hobbyist-adjacent capture tool; **not** certified automotive OEM equipment.
- Incorrect OBD connection can damage vehicle electronics — assembly docs must keep pinout unambiguous.
- Do not advertise TX, flashing, or immobilizer functions.
- Not affiliated with Honda Motor Co., Ltd. Do not place Honda trademarks on the product without a separate license (OpenDashCAN does not grant one).

## 6. Contacts & engineering change

- Issues / RFIs: GitHub Issues on `theworker02/OpenDashCAN` with label `hardware`.
- ECO process: open a PR against `hardware/can_recorder_rpi/manufacturing/` with redlines; do not silently change BOM criticals (crystal frequency, transceiver family, fuse rating).

## 7. Acceptance of first article

First-article (FAI) pack must include:

1. Populated PCBA photos (top/bottom).
2. Gerbers + centroid + BOM used (zip).
3. ICT/FCT raw logs for serials FA-001…FA-005.
4. Continuity report for OBD cable.
5. Sample microSD image hash (`sha256`) matching release notes.
6. TX interlock proof: CAN analyzer shows **zero** frames sourced by DUT under FCT.

We will approve EVT only after FAI sign-off.

Thank you — we value partners who treat **listen-only** as a safety property, not a marketing footnote.
