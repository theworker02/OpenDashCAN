# Buyer evaluation â€” From PyPI Ã¢â‚¬â€ full desktop (CLI + Qt + python-can)

## Goal

In 15â€“45 minutes, verify the Product builds or runs as documented and that proprietary notices are present.

## Steps

1. Confirm root `LICENSE` is proprietary and `ACQUISITION.md` exists.
2. Skim `README.md` install/run claims.
3. Execute:

```
```text
OBD/CAN sniff (LISTEN_ONLY) Ã¢â€ â€™ registered decoder Ã¢â€ â€™ VehicleState + ID rates + gaps
```
```text
Source Honda CAN Ã¢â€ â€™ Decoder Ã¢â€ â€™ VehicleState Ã¢â€ â€™ ClusterEnvironment Ã¢â€ â€™ Target Encoder Ã¢â€ â€™ Donor Cluster
```
```bash
python tools/round_brand_assets.py          # rounded logo / banner PNGs
python tools/generate_wiring_diagrams.py
python tools/capture_gui_demo.py --with-splash
```
```bash
# From PyPI Ã¢â‚¬â€ full desktop (CLI + Qt + python-can)
pip install "opendashcan[desktop]"

# From a clone (editable)
pip install -e ".[desktop]"
# or:
pip install -e ".[gui,hw]"

opendashcan info
opendashcan-gui              # splash Ã¢â€ â€™ main window (Live tab ready)
opendashcan-gui --no-splash  # skip boot animation
opendashcan-listen --virtual
```
```bash
opendashcan listen --virtual --vehicle honda.civic.gen10.us
opendashcan listen --capture captures/synthetic/idle_scenario.log
opendashcan listen --interface socketcan --channel can0 --bitrate 500000
opendashcan listen --interface pcan --channel PCAN_USBBUS1
opendashcan listen --interface slcan --channel COM3
```
```bash
opendashcan registry vehicles
opendashcan plan honda.civic.gen8.us.r18.auto honda.civic.gen10.cluster.digital
opendashcan gaps honda.civic.gen10.cluster.digital
opendashcan build-adapter honda.civic.gen8.us.r18.auto honda.civic.gen10.cluster.digital --documentation-only
opendashcan coverage --write
opendashcan clusters
pytest tests/test_gui_smoke.py
```

4. Run tests if present (`npm test`, `pytest`, `cargo test`, `go test ./...`, etc.).
5. Record README vs observed behavior gaps in workpapers.

## Pass criteria

- [ ] Clone succeeds
- [ ] Documented happy path works **or** failure is explained
- [ ] Minimal path needs no surprise secrets
- [ ] License notices intact

*Updated: 2026-09-22*
