# Single-pair probe (Phase 1 extraction) — probe_single_pair_eur_usd_c012

> Exploratory lab output. Not a strategy verdict; does not approve,
> promote, or change any campaign status. CAMPAIGN_012 remains REJECT;
> CAMPAIGN_011 remains the null model.

## Provenance
- data_kind: `real`
- pair: `EUR_USD`
- candidate: `CAMPAIGN_012_regime_switcher_atr_percentile`
- null: `CAMPAIGN_011_random_entry_anchor`
- date coverage: `2021-10-29 01:00:00+00:00` → `2025-05-14 05:00:00+00:00`
- limitations:
  - Per-fold expectancy R values are aggregations of small samples (CAMPAIGN_012 EUR_USD per-fold trade counts range 27-105; CAMPAIGN_011 EUR_USD per-fold range 8-27).
  - Standard error of the mean gap treats the 8 per-fold gap values as IID — a coarse approximation that ignores across-fold correlations from the same underlying market.
  - Dominance shares are computed on raw r_multiple sums; they do not net out the lab's full cost overlay.
  - No campaign verdict is changed by this extraction. CAMPAIGN_012 remains REJECT.

## Per-fold candidate vs null

| fold | C012 expectancy R | C012 trades | C012 PF | C012 ret % | C011 expectancy R | C011 trades | gap R |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | -0.0474 | 88 | 0.866 | -1.067 | -0.1237 | 12 | **+0.0764** |
| 1 | -0.1216 | 105 | 0.669 | -3.176 | +0.0460 | 27 | **-0.1676** |
| 2 | -0.0300 | 50 | 0.915 | -0.377 | +0.0968 | 16 | **-0.1268** |
| 3 | +0.2506 | 37 | 2.051 | +2.359 | +0.2729 | 13 | **-0.0223** |
| 4 | +0.0850 | 39 | 1.303 | +0.836 | -0.0322 | 17 | **+0.1171** |
| 5 | -0.0325 | 56 | 0.886 | -0.466 | -0.3414 | 15 | **+0.3090** |
| 6 | -0.0079 | 77 | 0.970 | -0.161 | -0.1597 | 11 | **+0.1519** |
| 7 | +0.1439 | 27 | 1.753 | +0.981 | -0.2785 | 8 | **+0.4225** |

## Aggregate gap

- C012 EUR_USD: mean = **`+0.0300`** R, median = **`-0.0189`** R, std = `0.1210`, positive folds = **3 / 8**, total trades = 479
- C011 EUR_USD (null): mean = **`-0.0650`** R, median = `-0.0780`, std = `0.2029`, total trades = 119
- **Mean gap R = `+0.0950`** (median gap = `+0.0967`)
- Gap std across folds = `0.2032`; SE of mean gap = `0.0718`; t-stat = `1.323`
- Folds with positive gap (C012 ≥ null): **5 / 8**

## Candidate dominance — where does the R come from?

- Total cumulative R across folds (sum of trade-level R): **`-4.391`**
- Top fold: **fold 3**, cumulative R = `+9.272`
- Top-fold share of |total R|: **`2.112`** (211.2%)
- Top 5 % of trades share of total R: `9.728`
- Top 10 % of trades share of total R: `15.899`

### Per-fold cumulative R contribution

| fold | cum R | signed share of total |
|---:|---:|---:|
| 0 | -4.170 | +0.950 |
| 1 | -12.768 | +2.908 |
| 2 | -1.502 | +0.342 |
| 3 | +9.272 | -2.112 |
| 4 | +3.313 | -0.755 |
| 5 | -1.818 | +0.414 |
| 6 | -0.605 | +0.138 |
| 7 | +3.886 | -0.885 |

## Candidate trade-level distribution

### Side (long vs short)

| side | n | mean R |
|---|---:|---:|
| long | 232 | +0.0122 |
| short | 247 | -0.0292 |

### Exit reason

| reason | n | mean R |
|---|---:|---:|
| eod | 2 | -0.2210 |
| stop | 91 | -1.0000 |
| time | 386 | +0.2255 |

### Entry hour UTC

| hour | n | mean R |
|---:|---:|---:|
| 01 | 54 | +0.1382 |
| 02 | 41 | -0.0688 |
| 05 | 50 | -0.1092 |
| 06 | 32 | +0.0634 |
| 09 | 75 | +0.0634 |
| 10 | 71 | -0.1375 |
| 13 | 70 | -0.1194 |
| 14 | 61 | +0.1972 |
| 17 | 19 | -0.2113 |
| 18 | 6 | -0.0425 |

## Candidate streaks (chronological)

- Max drawdown (cumulative R): `-28.432`
- Longest losing streak: `16` trades
- Longest winning streak: `12` trades

## Notes

- Phase 1 extraction only — no classification yet.
- Phase 2 robustness script consumes this JSON.
- Lab output. Does not approve any strategy or change any campaign verdict.
