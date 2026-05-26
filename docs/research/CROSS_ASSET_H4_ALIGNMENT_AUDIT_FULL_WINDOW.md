# Cross-Asset H4 Alignment Audit — Full Window

**Diagnostic only** — `strategy_evidence: false`

## Context

Full-window ingest attempted for H4 research **2020-01-01 22:00 UTC → 2026-05-24 21:00 UTC** (~9,954 bars). FRED fetch **blocked** (`FRED_API_KEY` absent). Normalized CSV **retained from prior fixture window** (7 daily rows, 2022-01) — not full-window real data.

## No-lookahead controls (verified in tests)

| rule | implementation |
|---|---|
| Daily obs date `D` available at `D+1 00:00 UTC` | `observation_to_availability_ts` |
| H4 uses `availability_ts <= bar_time` | `align_wide_frame_to_h4` |
| No same-day close leak | regression tests |
| Stale flags | `max_staleness_days` from registry |

## Coverage snapshot (fixture-backed normalized CSV)

From `research/cross_asset_features/h4_aligned_feature_availability.json`:

| feature | H4 coverage % | stale rate % | missing rate % |
|---|---:|---:|---:|
| broad_usd_index | 68.57 | 99.52 | 31.43 |
| us_2y_yield | 68.57 | 99.52 | 31.43 |
| us_10y_yield | 68.57 | 99.52 | 31.43 |
| vix | 68.57 | 99.52 | 31.43 |
| sp500 | 68.57 | 99.64 | 31.43 |
| oil_wti | 68.57 | 99.64 | 31.43 |

High stale rates reflect fixture window ending 2022-01 while H4 runs to 2026-05.

## Coverage by year

Early years (2020–2021) have **0%** feature coverage on sampled contexts because fixture data starts 2022-01. Full-window FRED data required to fix.

## Remaining gaps

- All required FRED series blocked without API key
- Gold: `MANUAL_CSV_REQUIRED`
- COT: `DESIGN_ONLY`

## Regenerate

```bash
python scripts/align_cross_asset_features_to_h4.py
```

## Disclaimer

No strategy evidence. Alignment mechanics verified; data coverage blocked on auth.
