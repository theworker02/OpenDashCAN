# Honda Civic Gen 11 (2022–2026) — `honda.civic.gen11.us`

Latest Civic generation in OpenDashCAN. Secondary target cluster:
`honda.civic.gen11.cluster.digital`.

## Documented (vehicle bus)

Provenance: vendored **commaai/opendbc** `honda_civic_ex_2022` (MIT). ENGINE_DATA `0x158`
and related PCM messages are DOCUMENTED. Registry aliases: `honda:civic:11`, `honda-civic11`.

## UNKNOWN / caveats

- Cluster consumption for a donor swap is **NOT PHYSICALLY_VERIFIED**
- Upstream may use `honda_bosch_radarless_generated` for some MY fingerprints — do not
  invent alternate IDs without a new selective import
- Accord11 / CR-V6 / Pilot4 (CAN-FD) are separate RESEARCH_REQUIRED stubs

See `research/honda/civic11.md`.
