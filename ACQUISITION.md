# Acquisition Brief â€” From PyPI Ã¢â‚¬â€ full desktop (CLI + Qt + python-can)

**Date:** 2026-09-22  
**Repository:** https://github.com/theworker02/OpenDashCAN  
**Default branch:** `main`  
**Primary language:** Python  
**Status:** Diligence briefing only. **No acquisition has occurred** by virtue of this file.  
**License:** Proprietary â€” sale, written commercial license, or completed asset transfer required (see root `LICENSE`).  
**Valuation:** Not stated.  
**Contact:** GitHub [@theworker02](https://github.com/theworker02) Â· [thanks.dev/u/gh/theworker02](https://thanks.dev/u/gh/theworker02)

> Cloning or forking this repository does **not** grant production, redistribution, SaaS, OEM, or commercial rights.

---

## 1. Executive thesis

<img src="assets/banner.png" alt="OpenDashCAN official logo" width="720"/> <strong>Installable desktop program (CLI + Qt) for listen-only OBD/CAN sniff, decode, cluster-gap research, and Honda Civic8Ã¢â€ â€™Civic10 adaptation documentation.</strong><br/> <em>Not a website Ã‚Â· Not an ECU flash tool Ã‚Â· LISTEN_ONLY by default</em>

**Why a buyer cares:** From PyPI Ã¢â‚¬â€ full desktop (CLI + Qt + python-can) packages transferable product IP â€” source, docs, in-repo brand assets, and a diligence room under `docs/acquisition/` â€” under a clear proprietary posture so diligence can proceed without mistaking the repo for open source.

---

## 2. Product snapshot

| Item | Detail |
|------|--------|
| Product | From PyPI Ã¢â‚¬â€ full desktop (CLI + Qt + python-can) |
| Repo | `theworker02/OpenDashCAN` |
| Language | Python |
| Open source? | **No** â€” proprietary |
| Rightsholder | theworker02 |
| Diligence pack | `docs/acquisition/` |

### Capability highlights (from current materials)

- Default: `LinkMode.LISTEN_ONLY` / `EncodeMode.NO_OUTPUT`
- No fabricated CAN IDs, scales, checksums, or pinouts
- Vehicle-bus DBC facts stay `VEHICLE_PROTOCOL_DOCUMENTED` Ã¢â‚¬â€ never auto-promoted to `CLUSTER_RX_CONFIRMED`
- Synthetic fixtures are labeled `SYNTHETIC`
- GUI Live tab always shows **LISTEN ONLY Ã¢â‚¬â€ NO TRANSMIT**

---

## 3. Problem / opportunity

Teams evaluating From PyPI Ã¢â‚¬â€ full desktop (CLI + Qt + python-can) typically need either (a) a commercial right to run or embed it, or (b) outright ownership of the Product IP for strategic build-out. Public GitHub visibility without a proprietary license creates false assumptions about free production use. This brief and the linked data room make the commercial path explicit.

---

## 4. What ships today

Honest maturity: treat repository contents, README claims, tests, and release tags as the source of truth. Do not assume production customers, ARR, filed patents, or SLAs unless separately evidenced in diligence.

Typical transferable surfaces:

- Source tree and build/test scripts present in-repo
- Documentation and design notes
- Acquisition / diligence markdown under `docs/acquisition/`
- Branding assets committed to the repository (if any)

---

## 5. Demo / evaluation path (buyer)

Minimal path (no secrets required unless README says otherwise):

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

Extended evaluation: `docs/acquisition/BUYER_EVALUATION.md`. Written NDA / evaluation grants may be required for private materials.

---

## 6. What a transaction typically includes

Subject to definitive schedules:

| Included (typical) | Excluded (typical) |
|--------------------|--------------------|
| Repo materials + asserted original IP | Seller personal accounts / unrelated repos |
| Docs + diligence room at closing | Third-party dependency source under separate licenses |
| In-repo brand marks as assigned | Secrets without rotation plan |
| Know-how captured in docs | Fabricated revenue, user, or adoption metrics |

---

## 7. Suggested deal structures

| Structure | When it fits |
|-----------|--------------|
| Non-exclusive commercial license | Deploy/run under seat or environment terms |
| Exclusive field-of-use license | Buyer wants exclusivity; seller may retain entity |
| Asset / IP assignment | Buyer wants ownership of Materials outright |
| OEM / redistribution | Separate agreement â€” not implied here |

Commercial terms (price, earnouts, escrow) are negotiated under NDA with counsel.

---

## 8. Buyer diligence checklist

- [ ] Confirm Rightsholder identity and authority to sell/license
- [ ] Inventory Materials (`docs/acquisition/ASSET_INVENTORY.md`)
- [ ] Review IP posture (`IP_PROVENANCE.md`) and dependencies (`DEPENDENCY_INVENTORY.md`)
- [ ] Run evaluation script (`BUYER_EVALUATION.md`)
- [ ] Review risks (`RISK_REGISTER.md`)
- [ ] Agree transfer scope (`TRANSFER_MANIFEST.md`) and handoff (`HANDOFF_CHECKLIST.md`)
- [ ] Supersede root `LICENSE` at closing via definitive agreement

---

## 9. Related documents

| Document | Purpose |
|----------|---------|
| `LICENSE` | Proprietary â€” no default grant |
| `docs/acquisition/README.md` | Data-room index |
| `docs/acquisition/EXECUTIVE_SUMMARY.md` | One-page thesis |
| `README.md` | Product overview |
| `SECURITY.md` | Vulnerability reporting |
| `COMMERCIAL.md` | Licensing contact path |
| `.github/FUNDING.yml` | Sponsors / thanks.dev |

---

## 10. Disclaimer

This package is informational and **does not** create a binding offer, grant of rights, or investment advice. Engage counsel for any transaction.

---

*Document version: 2.0.0 / 2026-09-22 Â· Classification: acquisition briefing*
