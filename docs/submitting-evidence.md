# Submitting verified evidence

OpenDashCAN only accepts **honest** CAN / cluster claims. Unknown stays unknown. Do not invent arbitration IDs, bit layouts, scales, checksums, or pinouts.

This page explains how to submit evidence via the GitHub issue form, what standards apply, and when to open a PR instead.

## Open the submission form

1. Go to **Issues → New issue** on the repo, or use this link:

   **https://github.com/theworker02/OpenDashCAN/issues/new?template=evidence_submission.yml**

2. Choose **Verified evidence submission**.
3. Fill every required field. Leave encoding blank when you do not know it.
4. Complete the license and evidence checklists.

For raw capture file links only (manifest + how to obtain files), you can also use:

**https://github.com/theworker02/OpenDashCAN/issues/new?template=capture_submission.yml**

## Evidence standards

| Rule | Meaning |
|------|---------|
| Do not invent | No guessed IDs, scales, checksums, or pinouts presented as fact |
| DBC ≠ cluster RX | Vehicle-bus / opendbc documentation is `VEHICLE_PROTOCOL_DOCUMENTED`, not `CLUSTER_RX_CONFIRMED` |
| Unknown stays unknown | Blank encoding is better than a wrong layout |
| Cite sources | Captures, photos, public PRs, dated forum posts — not “I think” |
| No proprietary dumps | No leaked OEM manuals or dumps you cannot redistribute |

Full policy: [evidence-policy.md](evidence-policy.md).

### Confidence ladder (DonorKnowledge)

Claims map to knowledge levels in `opendashcan/core/donor_knowledge.py`. Maintainers **do not auto-promote** levels.

| Level | Brief meaning |
|-------|----------------|
| `VEHICLE_PROTOCOL_DOCUMENTED` | Public vehicle-bus / DBC layout; not proof the cluster RX's it |
| `CLUSTER_RELEVANT_SIGNAL_DOCUMENTED` | Vehicle-bus signal clusters often need; still not RX-confirmed |
| `CLUSTER_RX_CONFIRMED` | Evidence the donor cluster consumes / displays this message |
| `CLUSTER_TIMING_CONFIRMED` | Period / timeout verified on the wire or bench |
| `CLUSTER_CHECKSUM_CONFIRMED` | Checksum / counter verified for cluster acceptance |
| `CLUSTER_STARTUP_CONFIRMED` | Wake / ignition / gateway sequence verified |
| `CLUSTER_ENVIRONMENT_COMPLETE` | Full cluster environment documented (rare; high bar) |
| `BENCH_VERIFIED` | Bench or in-vehicle confirmation with cited capture/photos |
| `COMMUNITY_RESEARCH` | Forum / swap notes — useful leads, not confirmation |
| `UNKNOWN` | Observed or reported but not classifiable yet |

Orthogonal confidence labels (`VERIFIED`, `COMMUNITY_REPORTED`, `INFERRED`, etc.) are described in [evidence-policy.md](evidence-policy.md).

## Captures and manifests

If you have log files:

1. Read [captures/README.md](../captures/README.md).
2. Prepare a JSON manifest against [`schemas/capture_manifest.schema.json`](../schemas/capture_manifest.schema.json).
3. Scrub PII (VIN ASCII, locations, accounts).
4. Prefer linking files (gist, release asset, cloud link) in the issue; the repo may keep community captures out of git by default.
5. Mark synthetic fixtures `SYNTHETIC` — never as vehicle truth.

Example shape: `captures/synthetic/manifest.example.json`.

## Optional PR path (YAML / captures)

Use an issue first when you have observations but not ready-to-merge files. Open a PR when you can land:

- Protocol package updates under `opendashcan/protocols/…` (`messages.yaml`, `signals.yaml`, `evidence.yaml` / evidence catalog)
- Cluster requirement / RX notes under `clusters/…`
- Capture manifests + documented access under `captures/` (follow that README)

For protocol / evidence YAML PRs, use the evidence PR template:

`.github/PULL_REQUEST_TEMPLATE/evidence.md`

(when opening the PR, choose that template if your GitHub UI offers multiple templates, or copy its checklist into the description).

PR rules of thumb:

- Update evidence / knowledge fields with sources — never invent to pass validation
- Run `python tools/validate_evidence.py`
- Do not claim `CLUSTER_RX_CONFIRMED` or `BENCH_VERIFIED` from DBC alone

## What happens after you submit

Maintainers triage the `evidence-submission` label, may ask clarifying questions, and may open or request a follow-up PR. Filing an issue does **not** lower the bar for repo labels — physical verification stays physical verification.

## Related docs

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [docs/evidence-policy.md](evidence-policy.md)
- [captures/README.md](../captures/README.md)
- [docs/safety.md](safety.md)
