# Process — assembly & test

| Doc | Purpose |
|-----|---------|
| [`assembly_sop.md`](assembly_sop.md) | Step-by-step build |
| [`ict.md`](ict.md) | In-circuit / flying-probe checks |
| [`fct.md`](fct.md) | Functional test + TX interlock |
| [`traveler.csv`](traveler.csv) | Shop-floor traveler fields |

All tests assume **LISTEN ONLY**. Fail the unit if any TX frames are observed.
