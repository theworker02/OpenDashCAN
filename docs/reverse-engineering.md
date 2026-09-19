# Reverse engineering guidance

Goal: learn which CAN IDs / bits drive cluster displays — **with evidence**, not guesses presented as fact.

## Workflow

1. Capture with a known ground truth (GPS speed, OBD RPM, camera of cluster).
2. Diff idle vs actuated (doors, turn signals, beams).
3. Use `opendashcan analyze` to list **changing IDs** (candidates only).
4. Correlate rates across buses carefully — similar rate ≠ same signal.
5. Document in `evidence.yaml` with confidence + sources.
6. Prefer **SYNTHETIC** labeled fixtures for CI; keep real captures under `captures/` with manifests.

## Do not

- Invent bit layouts from forum rumors.
- Copy incompatible-licensed DBC contents into the repo without license review.
- Mark `VERIFIED` without sources (CI rejects this).
- TX to a car until a future milestone and safety review.

## Civic-specific starting points

See [research/civic8_sources.md](../research/civic8_sources.md) and [research/civic10_sources.md](../research/civic10_sources.md).
