# What you may need to switch (Civic8 → Civic10 style)

**Mode:** `DOCUMENTATION_ONLY` checklist for adaptation research.  
**Not** a how-to for cutting OEM harnesses. **Not** Honda-sponsored.

For a donor digital cluster to live in a source vehicle, researchers typically discuss several **interfaces**. Each row below is labeled with confidence — **do not treat UNKNOWN as “skip it.”**

| Interface | What it means | Civic8→Civic10 status | Confidence |
|-----------|---------------|----------------------|------------|
| Power (+12V / ACC) | Cluster supply rails | Must be fused and matched; exact pins **UNKNOWN** | REQUIRES_BENCH |
| Ground | Chassis / signal grounds | Required; star-point strategy **UNKNOWN** | REQUIRES_BENCH |
| CAN-H / CAN-L | High-speed bus to cluster / gateway | F-CAN role DOCUMENTED; cluster RX set **UNKNOWN** | DOCUMENTED (bus) / UNKNOWN (cluster) |
| Ignition sense | Key/IG wake line | Often required for gauges; pin **UNKNOWN** | UNKNOWN |
| Illumination / dimmer | Night brightness | Common cluster input; encoding/pin **UNKNOWN** | UNKNOWN |
| Speakers / chimes | Warning audio | May be separate from CAN; path **UNKNOWN** | UNKNOWN |
| Immobilizer / gateway | Security / network gateway | Dual-bus / MICU interaction **UNKNOWN** | UNKNOWN / REQUIRES_BENCH |
| Steering-angle / ABS feeds | Some digital clusters expect extra IDs | Donor needs from opendbc are vehicle-bus DOCUMENTED; cluster acceptance **NOT CONFIRMED** | DOCUMENTED (vehicle) / UNKNOWN (RX) |

## Listen-only PC path vs future dual-bus adapter

| Path | Purpose | TX |
|------|---------|----|
| OBD → adapter → OpenDashCAN Desktop | Sniff + decode + gaps research | **No** (`LISTEN_ONLY`) |
| Future source ↔ adapter ↔ donor cluster | Adaptation bridge | Default `EncodeMode.NO_OUTPUT`; TX only under future explicit guard |

## Related

- Adaptation plan: `opendashcan plan honda.civic.gen8.us.r18.auto honda.civic.gen10.cluster.digital`
- GUI **Adaptation** + **Wiring** tabs
- Evidence: [submit form](https://github.com/theworker02/OpenDashCAN/issues/new?template=evidence_submission.yml)
