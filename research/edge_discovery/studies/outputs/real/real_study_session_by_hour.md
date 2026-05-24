# Edge-discovery study (real data) — real_session_by_hour

> Exploratory lab output. Not a strategy verdict; does not approve,
> promote, or change any campaign status.

## Provenance
- data_kind: `real`
- pair universe: `['EUR_USD']`
- date coverage: `2020-01-01 22:00:00+00:00` → `2026-05-19 21:00:00+00:00`
- inputs:
  - `h4_sqlite_store` — `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` — rows=`9931` — sha256=`8567fa8aeb516fa3…`
- limitations:
  - Each H4 bar contributes one signal; per-hour samples are large (>1,000 per hour over the full 2020-2026 universe) but each is heavily auto-correlated with its neighbors.
  - This study uses LONG-side forward returns only. A complement run with SHORT side (or two-sided) would be a follow-up.
  - Post-cost = mid-close return minus the lab's EUR_USD-shaped spread + slip overlay; this is not the exact cost model the formal campaigns use for evidence — see research/edge_discovery/costs.py.
  - Lab output only. Does not approve any strategy or change any campaign verdict.

## Aggregate

- Instrument: `EUR_USD`, Granularity: `H4`, Forward window: `4` bars
- Side: `LONG`, signals used: `9927`
- Overall mean post-cost: **`-0.000197`**
- Null mean: **`-0.000191`**, null std: `0.000041`
- Material-band threshold: `1.5` null stds → overall band: **`within_null`**

## Per-UTC-hour breakdown

| hour | n | mean post-cost | std | median | win rate | band |
|---|---:|---:|---:|---:|---:|---|
| UTC_01 | 1072 | -0.000304 | 0.004551 | -0.000262 | 0.468 | materially_below_null |
| UTC_02 | 583 | -0.000065 | 0.004159 | -0.000468 | 0.461 | materially_above_null |
| UTC_05 | 1072 | -0.000295 | 0.004117 | -0.000334 | 0.452 | materially_below_null |
| UTC_06 | 583 | -0.000074 | 0.003759 | -0.000299 | 0.472 | materially_above_null |
| UTC_09 | 1071 | -0.000142 | 0.003396 | -0.000263 | 0.467 | within_null |
| UTC_10 | 583 | -0.000168 | 0.003270 | -0.000262 | 0.463 | within_null |
| UTC_13 | 1071 | -0.000033 | 0.003125 | -0.000022 | 0.497 | materially_above_null |
| UTC_14 | 583 | -0.000132 | 0.003198 | -0.000258 | 0.470 | within_null |
| UTC_17 | 1071 | -0.000257 | 0.003661 | -0.000318 | 0.473 | materially_below_null |
| UTC_18 | 583 | -0.000146 | 0.003658 | -0.000233 | 0.475 | within_null |
| UTC_21 | 1072 | -0.000374 | 0.004473 | -0.000281 | 0.472 | materially_below_null |
| UTC_22 | 583 | -0.000181 | 0.004071 | -0.000378 | 0.461 | within_null |

## Notes

- If a session bin lands `materially_above_null` for many years on a real H4 store, that is worth a deeper look — but never a strategy approval directly from this output.
- A follow-up study should sweep PAIR over the seven majors and emit one row per (pair, hour) so the cross-pair signal is visible.
