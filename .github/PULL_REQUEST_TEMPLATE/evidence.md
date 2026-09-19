## Evidence / protocol YAML PR

Use this template for protocol YAML, cluster RX notes, evidence catalogs, or capture manifests.

## Summary
<!-- What claim or files does this PR add? -->

## Knowledge level
<!-- Pick one; do not promote without matching evidence -->
- [ ] `VEHICLE_PROTOCOL_DOCUMENTED` (DBC / vehicle-bus only)
- [ ] `CLUSTER_RELEVANT_SIGNAL_DOCUMENTED`
- [ ] `CLUSTER_RX_CONFIRMED`
- [ ] `CLUSTER_TIMING_CONFIRMED` / `CLUSTER_CHECKSUM_CONFIRMED` / `CLUSTER_STARTUP_CONFIRMED`
- [ ] `BENCH_VERIFIED` / `CLUSTER_ENVIRONMENT_COMPLETE`
- [ ] `COMMUNITY_RESEARCH` / `UNKNOWN`

## Evidence / safety
- [ ] No fabricated CAN IDs, scales, checksums, or pinouts
- [ ] Encoding left unknown where not verified
- [ ] DBC alone is **not** labeled `CLUSTER_RX_CONFIRMED` or `BENCH_VERIFIED`
- [ ] Sources cited (captures, public docs, dated community posts)
- [ ] `evidence.yaml` / catalog updated where required
- [ ] Captures: manifest + license; PII scrubbed; see `captures/README.md`
- [ ] Synthetic fixtures labeled `SYNTHETIC`
- [ ] No live TX enabled by default

## Related issue
<!-- e.g. evidence-submission issue URL -->

## Test plan
- [ ] `python tools/validate_evidence.py`
- [ ] `pytest` (if code touched)
- [ ] `ruff check .` / `mypy opendashcan` (if code touched)