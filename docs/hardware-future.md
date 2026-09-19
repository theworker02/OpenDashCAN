# Hardware (future)

Phase 1 does **not** require hardware. All Milestone 0.1 work is offline software.

## Planned interface

`opendashcan.hardware.bus.DualBusBridge`:

- Source bus RX (vehicle)
- Target bus TX (cluster) — gated by `TransmitMode`
- Default: **`TransmitMode.DISABLED`**
- Also: `LISTEN_ONLY`, `ENABLED` (future opt-in)

`NullBridge` is a software placeholder.

## Likely adapters (not endorsed / not integrated yet)

USB-CAN adapters (SocketCAN on Linux, vendor APIs on Windows) may be wrapped later. Selection criteria: listen-only support, dual-channel availability, open drivers.

## When hardware arrives

1. Bench harness first.
2. Capture manifests under `captures/`.
3. VERIFIED evidence before enabling TX paths in CI or defaults.
