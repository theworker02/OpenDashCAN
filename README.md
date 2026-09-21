<p align="center">
  <img src="assets/banner.png" alt="OpenDashCAN official logo" width="720"/>
</p>

<h1 align="center">OpenDashCAN</h1>

<p align="center">
  <strong>Installable desktop program (CLI + Qt) for listen-only OBD/CAN sniff, decode, cluster-gap research, and Honda Civic8â†’Civic10 adaptation documentation.</strong><br/>
  <em>Not a website Â· Not an ECU flash tool Â· LISTEN_ONLY by default</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/opendashcan/"><img src="https://img.shields.io/pypi/v/opendashcan.svg" alt="PyPI version"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Proprietary%20(source--available)-blue.svg" alt="MIT License"/></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+"/></a>
  <a href="https://github.com/theworker02/OpenDashCAN/actions/workflows/ci.yml"><img src="https://github.com/theworker02/OpenDashCAN/actions/workflows/ci.yml/badge.svg" alt="CI"/></a>
  <img src="https://img.shields.io/badge/GUI-PySide6-teal.svg" alt="GUI PySide6"/>
  <img src="https://img.shields.io/badge/mode-LISTEN_ONLY-critical.svg" alt="LISTEN_ONLY"/>
  <img src="https://img.shields.io/badge/status-Phase%204%20Documentation-orange.svg" alt="Phase 4"/>
  <a href="docs/"><img src="https://img.shields.io/badge/docs-available-brightgreen.svg" alt="Docs"/></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg" alt="Contributions welcome"/></a>
</p>

> **Disclaimer:** Not affiliated with, endorsed by, or sponsored by Honda Motor Co., Ltd.  
> **HondaÂ®, the Honda logo, and related marks are trademarks and/or copyrighted works of Honda Motor Co., Ltd. All rights reserved.**  
> OpenDashCAN does not claim ownership of those marks and does not redistribute official Honda trademark artwork in this repository. See [`docs/TRADEMARKS.md`](docs/TRADEMARKS.md). This project does **not** claim cluster control / physical compatibility.

---

## What it is

**OpenDashCAN Desktop** stays on your PC. It reads vehicle CAN somehow (USB adapter, listen-only Pi recorder, or offline log), decodes **registered** layouts, and surfaces VehicleState, ID rates, Phaseâ€‘4 cluster gaps, adaptation plans, wiring checklists, and research docs.

```text
OBD/CAN sniff (LISTEN_ONLY) â†’ registered decoder â†’ VehicleState + ID rates + gaps
```

Offline research pipeline (EncodeMode.NO_OUTPUT by default):

```text
Source Honda CAN â†’ Decoder â†’ VehicleState â†’ ClusterEnvironment â†’ Target Encoder â†’ Donor Cluster
```

Reference adaptation: **2009 Civic (8th gen, R18 auto)** â†’ **10th-gen Civic digital cluster**  
(`honda.civic.gen8.us.r18.auto` â†’ `honda.civic.gen10.cluster.digital`).

**Donor vehicle protocol (2016+ Honda)** is substantially documented from MIT [commaai/opendbc](https://github.com/commaai/opendbc) (`VEHICLE_PROTOCOL_DOCUMENTED`). That is **not** cluster RX confirmation â€” donor gauge requirements, timing, and gateway behavior remain incomplete until captures and bench tests exist.

**No real vehicle captures are in this repo yet** â€” only labeled `SYNTHETIC` fixtures for software tests.

---

## Features

| Area | What you get |
|------|----------------|
| **CLI** | `opendashcan` â€” listen, plan, gaps, registry, DBC index, coverage |
| **Qt desktop** | Dark automotive UI â€” Live, Platform, Lookup, Gaps, Adaptation, **Wiring**, Research |
| **Live listen** | Virtual / capture replay / SocketCANÂ·PCANÂ·slcan â€” **LISTEN ONLY â€” NO TRANSMIT** banner |
| **Boot splash** | Honda-themed cluster ignition (not OpenDashCAN logo); trademark notice on splash/About; `--no-splash` / `OPENDASHCAN_NO_SPLASH=1` |
| **DBC** | Import/index from public opendbc â€” never invents encodings; never auto-promotes to cluster RX |
| **Cluster gaps** | Phase 4 eight-axis gap report (DOCUMENTATION_ONLY) |
| **Wiring** | OBD tap pins, conceptual dual-bus (FUTURE/NO TX), harness switch checklist with confidence labels |
| **Evidence** | GitHub issue form â€” do not invent CAN data |

---

## Screenshots

<p align="center">
  <img src="assets/screenshots/01_main_platforms.png" alt="Platforms browser" width="720"/><br/>
  <em>Platforms / clusters browser + platform detail</em>
</p>

<p align="center">
  <img src="assets/screenshots/02_live_listen.png" alt="Live listen tab" width="720"/><br/>
  <em>Live tab â€” virtual/offline listen, ID rates, decoded signals, LISTEN ONLY banner</em>
</p>

<p align="center">
  <img src="assets/screenshots/03_cluster_gaps.png" alt="Cluster gaps" width="720"/><br/>
  <em>Cluster gaps (Phase 4) â€” documentation-only axes</em>
</p>

<p align="center">
  <img src="assets/screenshots/04_adaptation_plan.png" alt="Adaptation plan" width="720"/><br/>
  <em>Adaptation plan Civic8 â†’ Civic10</em>
</p>

<p align="center">
  <img src="assets/screenshots/05_boot_splash.png" alt="Boot splash" width="420"/><br/>
  <em>Honda-themed boot splash (trademark notice shown; official Honda assets not shipped in git)</em>
</p>

<p align="center">
  <img src="assets/screenshots/06_wiring.png" alt="Wiring tab" width="720"/><br/>
  <em>Wiring tab â€” diagrams + harness checklist</em>
</p>

---

## Demo GIFs

<p align="center">
  <img src="assets/demo/boot_splash.gif" alt="Boot splash demo" width="420"/><br/>
  <em>Honda-themed boot splash â€” glow â†’ ready (trademark notice; no official Honda assets in git)</em>
</p>

<p align="center">
  <img src="assets/demo/live_virtual_listen.gif" alt="Live virtual listen demo" width="720"/><br/>
  <em>Live tab playing synthetic capture (LISTEN_ONLY)</em>
</p>

Regenerate assets:

```bash
python tools/round_brand_assets.py          # rounded logo / banner PNGs
python tools/generate_wiring_diagrams.py
python tools/capture_gui_demo.py --with-splash
```

---

## Install & run

**PyPI:** [opendashcan](https://pypi.org/project/opendashcan/) Â· **Release:** [v0.1.0](https://github.com/theworker02/OpenDashCAN/releases/tag/v0.1.0)

```bash
# From PyPI â€” full desktop (CLI + Qt + python-can)
pip install "opendashcan[desktop]"

# From a clone (editable)
pip install -e ".[desktop]"
# or:
pip install -e ".[gui,hw]"

opendashcan info
opendashcan-gui              # splash â†’ main window (Live tab ready)
opendashcan-gui --no-splash  # skip boot animation
opendashcan-listen --virtual
```

**Windows:** after install, `opendashcan` / `opendashcan-gui` are on your Python Scripts PATH. Optional launchers: [`scripts/windows/opendashcan.bat`](scripts/windows/opendashcan.bat), [`scripts/windows/opendashcan-listen.bat`](scripts/windows/opendashcan-listen.bat).

### Live listen (LISTEN_ONLY â€” no TX)

```bash
opendashcan listen --virtual --vehicle honda.civic.gen10.us
opendashcan listen --capture captures/synthetic/idle_scenario.log
opendashcan listen --interface socketcan --channel can0 --bitrate 500000
opendashcan listen --interface pcan --channel PCAN_USBBUS1
opendashcan listen --interface slcan --channel COM3
```

If `python-can` is missing, the CLI/GUI print a clear install hint; **Virtual** and **Play file** still work.

### Research CLI

```bash
opendashcan registry vehicles
opendashcan plan honda.civic.gen8.us.r18.auto honda.civic.gen10.cluster.digital
opendashcan gaps honda.civic.gen10.cluster.digital
opendashcan build-adapter honda.civic.gen8.us.r18.auto honda.civic.gen10.cluster.digital --documentation-only
opendashcan coverage --write
opendashcan clusters
pytest tests/test_gui_smoke.py
```

---

## Wiring & harness

Evidence-safe docs live under [`docs/wiring/`](docs/wiring/). Diagrams: [`assets/wiring/`](assets/wiring/).

| Doc | Topic |
|-----|--------|
| [OBD listen tap](docs/wiring/obd_listen_tap.md) | Pins 4/5/6/14/16 â€” AiM / Racelogic / Pi recorder |
| [Bus roles](docs/wiring/bus_roles.md) | F-CAN / B-CAN / gateway conceptual (pin-level UNKNOWN) |
| [Swap checklist](docs/wiring/cluster_swap_checklist.md) | Power, GND, CAN, ignition, illumination, â€¦ |

<p align="center">
  <img src="assets/wiring/01_obd_listen_path.png" alt="OBD listen path" width="720"/><br/>
  <em>OBD â†’ adapter â†’ OpenDashCAN Desktop (LISTEN_ONLY)</em>
</p>

<p align="center">
  <img src="assets/wiring/02_dual_bus_future.png" alt="Dual-bus future" width="720"/><br/>
  <em>Conceptual dual-bus bridge â€” FUTURE / NO TX default</em>
</p>

<p align="center">
  <img src="assets/wiring/03_harness_interfaces.png" alt="Harness interfaces" width="720"/><br/>
  <em>Harness interfaces with confidence labels</em>
</p>

In the GUI: open the **Wiring** tab for the same diagrams + checklist, with links to [`hardware/can_recorder_rpi/`](hardware/can_recorder_rpi/README.md).

**Not OEM service instructions.** Donor-cluster connector pinouts are **UNKNOWN / REQUIRES_BENCH** until measured.

---

## Hardware (capture path)

Listen-only Raspberry Pi recorder design: [`hardware/can_recorder_rpi/README.md`](hardware/can_recorder_rpi/README.md) (`candump` â†’ copy log â†’ `opendashcan listen --capture â€¦` or Live tab **Play file**).

**Manufacturing (repo only â€” not in the Desktop app):** partner note, production BOM/AVL, open CAD (schematic/PCB/harness/OpenSCAD), assembly + ICT/FCT, factory flash, labels â€” see [`hardware/MANUFACTURING_INDEX.md`](hardware/MANUFACTURING_INDEX.md) and [`hardware/can_recorder_rpi/manufacturing/`](hardware/can_recorder_rpi/manufacturing/).

---

## Safety

- Default: `LinkMode.LISTEN_ONLY` / `EncodeMode.NO_OUTPUT`
- No fabricated CAN IDs, scales, checksums, or pinouts
- Vehicle-bus DBC facts stay `VEHICLE_PROTOCOL_DOCUMENTED` â€” never auto-promoted to `CLUSTER_RX_CONFIRMED`
- Synthetic fixtures are labeled `SYNTHETIC`
- GUI Live tab always shows **LISTEN ONLY â€” NO TRANSMIT**

See [docs/safety.md](docs/safety.md).

---

## Evidence & confidence

| Level | Meaning |
|-------|---------|
| `VERIFIED` / `PHYSICALLY_VERIFIED` | Confirmed with cited sources |
| `DOCUMENTED` / `SUPPORTED_BY_MULTIPLE_SOURCES` | Public docs / opendbc agree |
| `COMMUNITY_REPORTED` | Forum / community only |
| `INFERRED` | Heuristic â€” needs confirmation |
| `UNKNOWN` / `REQUIRES_BENCH` | Default / needs measurement |

**Submit verified evidence** (do not invent CAN data):  
[issue form](https://github.com/theworker02/OpenDashCAN/issues/new?template=evidence_submission.yml) Â· [guide](docs/submitting-evidence.md) Â· [policy](docs/evidence-policy.md)

---

## Project layout (high level)

```text
opendashcan/          # Python package (CLI, registry, decode, GUI, hw listen)
opendashcan/gui/      # Qt desktop (Live, gaps, wiring, splash, â€¦)
docs/wiring/          # Harness / OBD / swap checklist
hardware/                 # Pi recorder + manufacturing package (not in PyPI wheel)
assets/               # Official logo, screenshots, demo GIFs, wiring PNGs
captures/synthetic/   # SYNTHETIC fixtures only
research/             # Evidence reports (DOCUMENTATION_ONLY)
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Prefer small, evidence-labeled PRs. Never invent encodings or claim cluster RX without captures/bench.

---

## License

**Source-available proprietary** — evaluation under [LICENSE](./LICENSE); commercial / production use via [COMMERCIAL.md](./COMMERCIAL.md). See [LICENSE_TRANSITION_NOTICE.md](./LICENSE_TRANSITION_NOTICE.md) and [NOTICE](./NOTICE).

