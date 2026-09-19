# Architecture

## Pipeline

```text
┌─────────────┐    ┌────────────────┐    ┌──────────────┐    ┌────────────────┐    ┌─────────────┐
│ Source CAN  │ →  │ Source Decoder │ →  │ VehicleState │ →  │ Target Encoder │ →  │ Target CAN  │
└─────────────┘    └────────────────┘    └──────────────┘    └────────────────┘    └─────────────┘
```

The **Translator** wires a `VehicleDecoder` to a `ClusterEncoder`. It never imports Honda-specific arbitration IDs. Vehicle knowledge lives under `opendashcan/protocols/`.

## VehicleState

Each signal is a `SignalValue[T]` with:

- `value`, `timestamp`, `source`
- `confidence` (evidence level)
- `validity` (valid / stale / invalid / unknown)
- optional `unit`, `notes`, `evidence_refs`

## Frames

`CANFrame` models classic CAN now and reserves fields for CAN FD (`is_fd`, `bitrate_switch`, `error_state_indicator`).

## Startup sequencer

`ClusterStartupSequencer` models coarse phases:

`OFF → POWERED → INITIALIZING → ACTIVE` (or `FAULT`)

Real cluster init schedules are largely UNKNOWN; this is a skeleton for future hardware backends.

## Replay & analysis

Phase 1 operates on files: candump, CSV, JSON. Analysis helpers summarize IDs, diff captures, and correlate bytes to external series for discovery — results are INFERRED until verified.

## Hardware

`DualBusAdapter` abstracts future ESP32/STM32/socketcan bridges. TX is refused unless `tx_enabled` and `LinkMode.BIDIRECTIONAL` are set, with optional ID allowlists.
