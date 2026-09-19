# Evidence policy

To **submit** verified observations, use the [Verified evidence submission](https://github.com/theworker02/OpenDashCAN/issues/new?template=evidence_submission.yml) form and read [submitting-evidence.md](submitting-evidence.md).

Every signal / message claim uses one of:

| Level | Meaning |
|-------|---------|
| **VERIFIED** | Bench or in-vehicle confirmed with cited sources (logs, photos, PRs). **Requires sources.** |
| **SUPPORTED_BY_MULTIPLE_SOURCES** | Independent public sources agree (e.g. MIT opendbc + docs). Still may not prove *cluster* behavior. |
| **COMMUNITY_REPORTED** | Forums / wikis / vendor blogs — IDs or names only; layouts often missing. |
| **INFERRED** | Reasoned guess — must be labeled; never sold as known. |
| **UNKNOWN** | Default. **Unknown stays unknown.** |

## Rules

1. No fake CAN data presented as real.
2. Synthetic test data must be marked **SYNTHETIC**.
3. `tools/validate_evidence.py` rejects `VERIFIED` without sources.
4. Encoders must not emit fabricated “real” cluster frames; return `[]` or SYNTHETIC-only research frames.
5. Document caveats when vehicle-bus DBC knowledge is used for a **donor cluster** hypothesis.
