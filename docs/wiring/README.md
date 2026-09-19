# Wiring & harness (DOCUMENTATION_ONLY)

**Not OEM service instructions.** Not affiliated with, endorsed by, or sponsored by Honda Motor Co., Ltd.

This folder documents **listen-only** PC capture paths and **conceptual** harness interfaces for Civic8→Civic10-style cluster research. Pin-level donor-cluster connectors remain **UNKNOWN / REQUIRES_BENCH** unless a cited capture or service extract exists.

| Document | Contents |
|----------|----------|
| [OBD-II listen tap](obd_listen_tap.md) | Pins 4/5/6/14/16 — AiM / Racelogic / Pi recorder |
| [Bus roles](bus_roles.md) | F-CAN / B-CAN / gauge-gateway conceptual (UNKNOWN at pin level) |
| [Cluster swap checklist](cluster_swap_checklist.md) | What you *may* need to switch — confidence labels |
| [Hardware Pi recorder](../../hardware/can_recorder_rpi/README.md) | Manufacturing design for listen-only capture |

Diagram assets (PNG): [`assets/wiring/`](../../assets/wiring/).

Desktop GUI: **Wiring** tab in `opendashcan-gui`.
