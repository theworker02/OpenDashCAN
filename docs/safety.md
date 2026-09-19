# Safety

OpenDashCAN Desktop defaults to **LISTEN_ONLY** / passive operation.

## Rules

1. **No live TX by default.** Hardware adapters must refuse transmit unless explicitly armed.
2. **Listen-only** when sniffing a vehicle bus (`LinkMode.LISTEN_ONLY`, bitrate typically 500 kbit/s).
3. Use **electrical isolation** and a current-limited setup for any future bench TX.
4. Maintain an **arbitration ID allowlist** for any enabled TX path.
5. Prefer a **second person + kill switch** for bench experiments.
6. Do not road-test unverified cluster translation.
7. Treat airbag, ABS, EPS, and immobilizer traffic as out-of-scope for hobby TX.
8. **Decode only documented / registered layouts** (e.g. `Civic10VehicleDecoder`). Do not invent encodings.
9. Do **not** claim cluster control or physical compatibility from listen/decode alone.

## Software guarantees

- Default `EncodeMode.NO_OUTPUT` — encoders return `[]`
- Default `LinkMode.LISTEN_ONLY` / `TransmitMode.DISABLED`
- CLI `listen` and GUI Live tab never call send APIs for normal use
- CLI `translate` / `replay` write files only
- `NullDualBusAdapter` / `NullBridge` cannot transmit
- Evidence policy rejects unverified “facts” posing as VERIFIED

## Future TX (not enabled)

Transmit remains **future-only**. Any send path must refuse unless **all** of:

1. Environment flag `OPENDASHCAN_ALLOW_TX=1`
2. A **non-empty** arbitration-ID allowlist
3. Explicit bidirectional / ENABLED mode on the adapter

Even then, the listen-only bus wrapper (`opendashcan.hw.listen.ListenOnlyBus`) still refuses TX. Do not enable this for road vehicles without isolation, review, and verified evidence.

## Disclaimer

You are responsible for complying with local law and for any damage to vehicles, property, or persons. This software is provided without warranty (see LICENSE).
