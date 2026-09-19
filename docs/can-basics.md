# CAN basics (short)

Controller Area Network (CAN) is a multi-master bus used in vehicles.

## Frame essentials

- **Arbitration ID** — 11-bit (standard) or 29-bit (extended); priority is numeric (lower ID wins).
- **DLC** — data length code; classic CAN payload up to 8 bytes; CAN FD up to 64.
- **Payload** — raw bytes; meaning is application-specific (DBC / reverse engineering).
- **Bus rate** — e.g. Honda F-CAN often 500 kbps; B-CAN much slower (~33.33 kbps).

## Why clusters are hard

- Multiple networks (powertrain vs body) with **gateways**.
- Rolling **counters** and **checksums** (Honda: `(sum)&0xF` + 2-bit counter on many msgs).
- Timeout behavior: missing messages may blank gauges or set DTCs.

## OpenDashCAN stance

We store frames as `CANFrame` and only assign meaning when evidence supports it. Replay and analysis tools work on **raw IDs/payloads** without claiming decoding.
