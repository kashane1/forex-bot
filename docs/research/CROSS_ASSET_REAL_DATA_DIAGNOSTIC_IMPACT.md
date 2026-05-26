# Cross-Asset Real Data Diagnostic Impact

**Diagnostic only** — `strategy_evidence: false`

## Summary

Re-ran `scripts/run_mtf_confluence_diagnostics.py` using normalized cross-asset outputs and availability-aware H4 alignment. **No edge, win-rate, or expectancy claims.**

| metric | before (fixture path) | after (normalized pipeline) |
|---|---|---|
| `cross_asset_status` | `FIXTURE_ONLY` | `REAL_DATA_NORMALIZED` |
| `cross_asset_missing` count | 2,142 | **2,142** (unchanged) |
| contexts evaluated | 6,916 | 6,916 |

## Why `cross_asset_missing` did not decrease

1. **`FRED_API_KEY` absent** in the sprint environment — live FRED fetch blocked (`fred_fetch_blocked_report.json`).
2. **`data/external_features/` empty** — no operator local CSVs.
3. **Normalized CSV built from committed fixtures** spanning only **2022-01-03 → 2022-01-07** (7 rows).
4. H4 research window begins **~2020-01** — availability-aware alignment correctly yields **NaN** for dxy/vix/us10y on early bars → `cross_asset_missing` persists.

This is expected and honestly documented. Full-window FRED ingest (or local CSV drop) is required to reduce `cross_asset_missing`.

## Feature coverage

| feature | normalized rows | H4 coverage (seven-pair union) |
|---|---|---|
| Core daily series | 5–7 fixture rows each | ~0% before 2022-01-04 availability lag |
| Derived (`us_10y_minus_2y`, 1d changes) | computed on fixture window | same |

See `research/cross_asset_features/h4_aligned_feature_availability.json` for per-feature coverage/stale rates on the local H4 store.

## Stale-feature rate

Fixture window is shorter than H4 history → aligned values beyond fixture range are forward-filled from last fixture observation and flagged **stale** per registry thresholds.

## COT status

**DESIGN_ONLY** — parser stub + design doc; no live CFTC ingest.

## Explicit disclaimer

- No strategy approved.
- No CAMPAIGN_018.
- No confluence lift validation.
- No profitability claims.
- Diagnostic data-readiness only.

## Outputs

- `research/confluence_diagnostics/confluence_diagnostic_summary_after_real_cross_asset.json`
- `research/confluence_diagnostics/confluence_reason_code_counts_after_real_cross_asset.csv`

## Recommended next sprint

**`infra-external-data-ingest-blocker-resolution-001`** — obtain `FRED_API_KEY` or operator local CSVs covering 2019+ so normalized features span the H4 research window. Alternative follow-on after successful FRED ingest: **`infra-cot-positioning-feature-ingest-001`**.
