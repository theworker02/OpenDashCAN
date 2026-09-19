## Summary
<!-- What does this PR change and why? -->

## Evidence / safety
- [ ] No fabricated CAN IDs, scales, checksums, or pinouts
- [ ] New/changed signals update `evidence.yaml` with confidence + sources
- [ ] `VERIFIED` entries include citations
- [ ] Synthetic fixtures labeled `SYNTHETIC`
- [ ] No live TX enabled by default
- [ ] Protocol / capture PRs: also use [.github/PULL_REQUEST_TEMPLATE/evidence.md](PULL_REQUEST_TEMPLATE/evidence.md) checklist

## Test plan
- [ ] `ruff check .` / `ruff format --check .`
- [ ] `mypy opendashcan`
- [ ] `pytest`
- [ ] `python tools/validate_evidence.py`
