# Contributing

Thanks for helping OpenDashCAN stay honest about what is known vs unknown.

## Principles

1. **No fake CAN data** presented as real vehicle traffic.
2. **Unknown stays UNKNOWN** — do not invent signal IDs or layouts.
3. Label confidence: `VERIFIED` | `SUPPORTED_BY_MULTIPLE_SOURCES` | `COMMUNITY_REPORTED` | `INFERRED` | `UNKNOWN`.
4. Mark synthetic fixtures **SYNTHETIC**.
5. Phase 1 is **passive/offline** — do not enable hardware TX by default.

## Submit verified evidence

Prefer the GitHub issue form over inventing data:

- **Form:** [Verified evidence submission](https://github.com/theworker02/OpenDashCAN/issues/new?template=evidence_submission.yml)
- **Guide:** [docs/submitting-evidence.md](docs/submitting-evidence.md)
- **Policy:** [docs/evidence-policy.md](docs/evidence-policy.md)

Captures-only: [Capture submission](https://github.com/theworker02/OpenDashCAN/issues/new?template=capture_submission.yml) · [captures/README.md](captures/README.md)

## Development setup

```bash
pip install -e ".[dev]"
pytest
python tools/validate_evidence.py
ruff check .
mypy opendashcan
```

## Evidence YAML

Protocol packages ship `evidence.yaml`. `VERIFIED` entries **must** include sources (`tools/validate_evidence.py` enforces this).

## Pull requests

Use the default [PR template](.github/PULL_REQUEST_TEMPLATE.md). For protocol YAML / capture PRs, also follow [.github/PULL_REQUEST_TEMPLATE/evidence.md](.github/PULL_REQUEST_TEMPLATE/evidence.md). Prefer small, focused changes. Conventional commits welcome (`feat`, `fix`, `docs`, `test`, `chore`).

## Captures

See `captures/README.md`. Include a manifest and license.
