# Edge-discovery study — event_window_direction

> Exploratory lab output. Not a strategy verdict; does not approve, 
> promote, or change any campaign status. See 
> `docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md`.

## Setup

- Instrument: `EUR_USD`
- Granularity: `H4`
- Forward window (bars): `6`
- Signals used: `6` (dropped trailing: `0`, dropped missing: `0`)

### Inputs
- `candles_path`: `research/edge_discovery/sample_fixtures/synthetic_EUR_USD_H4.csv`
- `candles_sha256`: `73c94e5a40a035bba907b0563cef795fe35832a32cb7dad529f377892c612b07`
- `events_path`: `research/edge_discovery/sample_fixtures/synthetic_events.csv`
- `events_sha256`: `271641020754eecc195d2951ba0d8fa274ca280d31893ac337298c6832b91e98`
- `side`: `LONG`
- `seeds`: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]`
- `event_classes_in_fixture`: `['CPI', 'FOMC', 'NFP']`

## Pre-cost

| n | mean | std | median | win_rate | p10 | p90 |
|---:|---:|---:|---:|---:|---:|---:|
| 6 | +0.000036 | 0.002946 | +0.000255 | 50.00% | -0.003078 | +0.002930 |

## Post-cost

| n | mean | std | median | win_rate | p10 | p90 |
|---:|---:|---:|---:|---:|---:|---:|
| 6 | -0.000198 | 0.002946 | +0.000022 | 50.00% | -0.003311 | +0.002695 |

## Null comparison (descriptive — not a significance test)

- Null mean (random-entry, sample-matched): `-0.000093`
- Null std across seeds: `0.001105`
- Study mean − null mean: `-0.000105`
- Gap in null stds: `-0.10`
- Band: `within_null`

## By group

| group | n | mean | std | win_rate | sub_pre_mean | sub_post_mean |
|---|---:|---:|---:|---:|---:|---:|
| CPI | 2 | +0.000186 | 0.005653 | 50.00% | +0.000420 | +0.000186 |
| FOMC | 2 | -0.001925 | 0.001253 | 0.00% | -0.001692 | -0.001925 |
| NFP | 2 | +0.001145 | 0.000088 | 100.00% | +0.001378 | +0.001145 |

## Notes

- Synthetic fixture run — not strategy evidence; illustrative only.
- Real-fixture run: point candles_path at the SQLite-derived H4 CSV and events_path at the real NFP/FOMC fixture; no other change.
- Per-class dominance share (n / total): {'CPI': 0.3333333333333333, 'FOMC': 0.3333333333333333, 'NFP': 0.3333333333333333}
- Event classes in fixture with ZERO matched trades: []
- Reminder: post-cost mean must clearly beat the random-entry null (see EDGE_DISCOVERY_CANDIDATE_RANKING_RULES.md); aggregate sign alone does not graduate.

