# Cross-Asset H4 Alignment Audit

**Diagnostic only** — `strategy_evidence: false`

## Availability convention

| frequency | observation date | availability timestamp |
|---|---|---|
| daily | `D` | `D + 1 day @ 00:00 UTC` |
| weekly (COT) | report date | `report_date + 3 days @ 00:00 UTC` (conservative) |

## No-lookahead controls

1. H4 alignment uses `align_wide_frame_to_h4` / `align_features_to_h4_with_availability`.
2. Same-day close cannot appear on earlier H4 bars the same calendar day.
3. Forward-fill only from observations whose availability timestamp `<= bar_time`.
4. Stale flags when gap since last source observation exceeds registry `max_staleness_days`.

## Friday / weekend behavior

Friday daily close dated `F` becomes available Saturday `00:00 UTC`. H4 bars on Friday after US cash close still must not use that close until availability timestamp.

## Outputs

- `research/cross_asset_features/h4_aligned_feature_availability.json`
- `research/cross_asset_features/h4_aligned_feature_sample.csv` (compact sample)

## Regenerate

```bash
python scripts/align_cross_asset_features_to_h4.py
```

Requires local H4 SQLite store. No broker order APIs.
