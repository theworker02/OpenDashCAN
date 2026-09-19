# F-CAN / B-CAN / gauge-gateway (conceptual)

**Confidence:** bus **roles and bitrates** are DOCUMENTED from service-literature summaries already in the registry / adaptation report. **Connector pinouts, splice points, and gateway pin maps for a physical cluster swap are UNKNOWN / REQUIRES_BENCH** until measured.

## Bus roles (Civic research context)

| Bus | Typical rate | Role (high level) | Confidence |
|-----|--------------|-------------------|------------|
| F-CAN | ~500 kbit/s | Powertrain / high-speed vehicle CAN; OBD diagnostic often bridges here | DOCUMENTED (service lit / opendbc vehicle-bus) |
| B-CAN | ~33.3 kbit/s (8th-gen class) | Body / comfort — lighting, some cluster-adjacent signals | DOCUMENTED as bus existence; payload maps largely UNKNOWN |
| Gauge / gateway | UNKNOWN | What a **donor digital cluster** actually requires on the wire | UNKNOWN — not auto-promoted from opendbc |

Community research (e.g. CivicX / B-CAN taps) is labeled `COMMUNITY_RESEARCH` in [`research/CLUSTER_CAN_EVIDENCE.md`](../../research/CLUSTER_CAN_EVIDENCE.md) — not physical verification in this repo.

## Conceptual diagram

```mermaid
flowchart TB
  subgraph vehicle [Source vehicle buses]
    FCAN["F-CAN ~500k<br/>DOCUMENTED role"]
    BCAN["B-CAN ~33.3k<br/>DOCUMENTED role"]
    GW["Gateway / MICU<br/>pin map UNKNOWN"]
  end

  subgraph listen [LISTEN_ONLY PC path — today]
    OBD["OBD tap 6/14"]
    PC["OpenDashCAN Desktop"]
  end

  subgraph future [FUTURE dual-bus adapter — NO TX default]
    BR["Bridge / adapter<br/>EncodeMode.NO_OUTPUT"]
    CL["Donor digital cluster<br/>RX set UNKNOWN"]
  end

  FCAN --> GW
  BCAN --> GW
  FCAN -.-> OBD --> PC
  GW -.->|"REQUIRES_BENCH"| BR
  BR -.->|"NO TX default"| CL
```

## What this does **not** claim

- Exact gauge connector pin numbers for Civic 10 digital clusters
- That OBD traffic alone wakes or drives a donor cluster
- Physical compatibility of any harness splice

See also: [`docs/wiring/cluster_swap_checklist.md`](cluster_swap_checklist.md).
