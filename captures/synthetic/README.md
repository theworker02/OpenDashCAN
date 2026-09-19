# SYNTHETIC captures only

These files are **generated** from `Civic10Encoder` in `EncodeMode.SYNTHETIC`
using public opendbc vehicle-bus layouts. They are **not** real vehicle or
cluster captures and must never be treated as PHYSICALLY_VERIFIED evidence.

| File | Purpose |
|------|---------|
| `idle_scenario.log` | candump-format synthetic idle (RPM/speed/gear/doors/blinkers/…) |
| `idle_scenario.asc` | Same traffic as Vector ASC for Pi recorder ingest path |
| `manifest.example.json` | Example capture manifest shape |

Regenerate with:

```text
python -c "…"  # or tests that round-trip encoder → decoder
```

Real captures belong under `captures/community/` with `synthetic: false`.
