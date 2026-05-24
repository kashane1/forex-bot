# Edge-discovery study — session_time_of_day

> Exploratory lab output. Not a strategy verdict; does not approve, 
> promote, or change any campaign status. See 
> `docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md`.

## Setup

- Instrument: `EUR_USD`
- Granularity: `H4`
- Forward window (bars): `4`
- Signals used: `476` (dropped trailing: `4`, dropped missing: `0`)

### Inputs
- `candles_path`: `research/edge_discovery/sample_fixtures/synthetic_EUR_USD_H4.csv`
- `candles_sha256`: `73c94e5a40a035bba907b0563cef795fe35832a32cb7dad529f377892c612b07`
- `side`: `LONG`
- `seeds`: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]`

## Pre-cost

| n | mean | std | median | win_rate | p10 | p90 |
|---:|---:|---:|---:|---:|---:|---:|
| 476 | -0.000055 | 0.002022 | -0.000059 | 48.95% | -0.002750 | +0.002495 |

## Post-cost

| n | mean | std | median | win_rate | p10 | p90 |
|---:|---:|---:|---:|---:|---:|---:|
| 476 | -0.000268 | 0.002022 | -0.000273 | 42.86% | -0.002964 | +0.002281 |

## Null comparison (descriptive — not a significance test)

- Null mean (random-entry, sample-matched): `-0.000270`
- Null std across seeds: `0.000091`
- Study mean − null mean: `+0.000001`
- Gap in null stds: `+0.02`
- Band: `within_null`

## By group

| group | n | mean | std | win_rate | sub_pre_mean | sub_post_mean |
|---|---:|---:|---:|---:|---:|---:|
| UTC_02 | 80 | -0.000185 | 0.002027 | 46.25% | +0.000029 | -0.000185 |
| UTC_06 | 79 | -0.000174 | 0.002102 | 41.77% | +0.000039 | -0.000174 |
| UTC_10 | 79 | -0.000284 | 0.002128 | 44.30% | -0.000070 | -0.000284 |
| UTC_14 | 79 | -0.000255 | 0.001960 | 44.30% | -0.000041 | -0.000255 |
| UTC_18 | 79 | -0.000328 | 0.002046 | 40.51% | -0.000115 | -0.000328 |
| UTC_22 | 80 | -0.000385 | 0.001918 | 40.00% | -0.000171 | -0.000385 |

## Notes

- Synthetic fixture run — not strategy evidence; illustrative only.
- Per-session sample size is small in the committed fixture; rerun against a hydrated H4 store for meaningful per-hour n.
- Reading: a session is worth a closer look only if its post-cost mean materially exceeds the per-session null band — not if it is merely 'positive'.

