# Captures

**Current status: no real vehicle CAN captures are in this repository.**

OpenDashCAN is in a **documentation-only** phase. We do not own CAN hardware and have not logged any Civic F-CAN / B-CAN traffic. Readiness labels such as `REQUIRES_CAN_CAPTURE` mean *blocked until captures exist* — not that captures are already available for analysis.

## What is present

| Path | Contents |
|------|----------|
| `synthetic/` | Clearly labeled **generated** fixtures (`idle_scenario.log` / `.asc`) for software tests |
| `synthetic/README.md` | How synthetic files were produced |
| `community/` | Empty placeholder for future contributor uploads (gitignored by default) |

## What is not present

- No Civic 8 source-vehicle logs
- No Civic 10 / 11 / Accord / CR-V donor-cluster bench logs
- No OBD or panda captures from the reference 2009 Civic

Synthetic files must never be treated as real encodings or as proof of cluster compatibility.

## When contributors add captures

1. Include a JSON manifest validated against `schemas/capture_manifest.schema.json`
2. Set `synthetic: false` only for real vehicle/bench traffic
3. Scrub PII
4. Document vehicle, year, trim, bus, bitrate when known
5. Prefer scenario labels (idle, RPM sweep, indicators, PRND, etc.)
6. Open a [Verified evidence submission](https://github.com/theworker02/OpenDashCAN/issues/new?template=evidence_submission.yml) or [Capture submission](https://github.com/theworker02/OpenDashCAN/issues/new?template=capture_submission.yml) issue — see [docs/submitting-evidence.md](../docs/submitting-evidence.md)

See `synthetic/manifest.example.json` for the manifest shape.

## Hardware to obtain captures

Minimal manufacturing design for a listen-only Raspberry Pi recorder:
[`hardware/can_recorder_rpi/README.md`](../hardware/can_recorder_rpi/README.md).

