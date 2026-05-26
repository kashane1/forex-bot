# Cross-Asset H4 Alignment Audit — Full Window

**Diagnostic only** — `strategy_evidence: false`

## Context

Full-window FRED ingest **succeeded** with `FRED_API_KEY` configured locally (not printed, not committed). Normalized CSV contains **2,148 daily rows** (2018-01-02 → 2026-05-22). H4 research window **2020-01-01 22:00 UTC → 2026-05-24 21:00 UTC** (~9,954 bars).

## No-lookahead controls (verified in tests)

| rule | implementation |
|---|---|
| Daily obs date `D` available at `D+1 00:00 UTC` | `observation_to_availability_ts` |
| H4 uses `availability_ts <= bar_time` | `align_wide_frame_to_h4` |
| No same-day close leak | regression tests pass |
| Stale flags | `max_staleness_days` from registry; stale flags present |

## Coverage snapshot (real FRED data)

From `research/cross_asset_features/h4_aligned_feature_availability.json`:

| feature | H4 coverage % | stale rate % | missing rate % |
|---|---:|---:|---:|
| broad_usd_index | 100.0 | 0.0 | 0.0 |
| us_2y_yield | 100.0 | 0.0 | 0.0 |
| us_10y_yield | 100.0 | 0.0 | 0.0 |
| vix | 100.0 | 0.0 | 0.0 |
| sp500 | 100.0 | 0.0 | 0.0 |
| oil_wti | 100.0 | 0.01 | 0.0 |
| nasdaq_composite | 100.0 | 0.0 | 0.0 |
| us_10y_minus_2y | 100.0 | 0.0 | 0.0 |
| broad_usd_index_1d_change | 100.0 | 0.0 | 0.0 |
| vix_1d_change | 100.0 | 0.0 | 0.0 |
| sp500_1d_return | 100.0 | 0.0 | 0.0 |
| oil_wti_1d_return | 100.0 | 0.01 | 0.0 |

100% H4 coverage across all years (2020–2026). Stale rates near zero — forward-fill within `max_staleness_days` only.

## Coverage by year

All features at **100%** coverage for 2020, 2021, 2022, 2023, 2024, 2025, 2026.

## Remaining gaps

- Gold: `MANUAL_CSV_REQUIRED` (not in FRED registry)
- COT: `DESIGN_ONLY`

## Regenerate

```bash
python scripts/run_external_data_full_window_pipeline.py
python scripts/align_cross_asset_features_to_h4.py
```

## Disclaimer

No strategy evidence. Alignment mechanics verified; full-window real FRED data ingested.
