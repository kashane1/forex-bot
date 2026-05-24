# Edge-discovery study (real data) — real_pair_baseline

> Exploratory lab output. Not a strategy verdict; does not approve,
> promote, or change any campaign status. CAMPAIGN_010 / 012 / 013 /
> 014 remain REJECT; CAMPAIGN_011 remains the null model.

## Provenance
- data_kind: `real`
- pair universe: `['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD', 'USD_CAD', 'USD_CHF', 'NZD_USD']`
- date coverage: `2020-01-01T00:00:00+00:00` → `2026-05-19T21:00:00+00:00`
- limitations:
  - Material-gap floor is +0.05 R per-pair; this is the lab's universe-wide material threshold per the candidate ranking rules, NOT a significance test.
  - Per-pair mean expectancy R is computed across the 8 walk-forward folds. Folds use rolling test windows, so this is an across-time aggregation per pair.
  - CAMPAIGN_011 supplies the null floor per pair, not a global scalar — same universe, same fold layout, random entries.
  - No campaign verdict is changed by this study. CAMPAIGN_010, 012, 013, 014 remain REJECT and CAMPAIGN_011 remains the null model.

## Null per pair (CAMPAIGN_011 mean expectancy R across 8 folds)

| pair | mean R | median R | std R | n folds positive | total trades | avg spread (pips) |
|---|---:|---:|---:|---:|---:|---:|
| AUD_USD | -0.0415 | -0.0736 | 0.1528 | 2 | 190 | 1.35 |
| EUR_USD | -0.0650 | -0.0780 | 0.2029 | 3 | 119 | 1.45 |
| GBP_USD | +0.0756 | +0.1169 | 0.1847 | 5 | 196 | 1.86 |
| NZD_USD | -0.0986 | -0.0454 | 0.2137 | 3 | 139 | 2.36 |
| USD_CAD | -0.0069 | +0.0454 | 0.1564 | 5 | 182 | 1.90 |
| USD_CHF | +0.0269 | +0.0555 | 0.1437 | 5 | 177 | 1.64 |
| USD_JPY | +0.0000 | -0.0005 | 0.0016 | 3 | 174 | 1.64 |

## Gap-from-null table (one row per pair, columns are candidates)

| pair | null R | C010_session_breakout R | gap C010_session_breakout | C012_regime_switcher_atr_percentile R | gap C012_regime_switcher_atr_percentile | C013_cross_pair_currency_strength_rotation R | gap C013_cross_pair_currency_strength_rotation | C014_calendar_event_window_anomaly R | gap C014_calendar_event_window_anomaly | best campaign | best gap | n above null |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EUR_USD | -0.0650 | -0.0685 | -0.0036 | +0.0300 | +0.0950 | -0.0290 | +0.0360 | -0.2148 | -0.1498 | C012_regime_switcher_atr_percentile | +0.0950 | 1 |
| GBP_USD | +0.0756 | -0.0417 | -0.1172 | -0.0487 | -0.1243 | -0.0151 | -0.0907 | -0.0884 | -0.1640 | C013_cross_pair_currency_strength_rotation | -0.0907 | 0 |
| USD_JPY | +0.0000 | -0.0003 | -0.0003 | +0.0004 | +0.0004 | +0.0000 | -0.0000 | -0.0008 | -0.0008 | C012_regime_switcher_atr_percentile | +0.0004 | 0 |
| AUD_USD | -0.0415 | -0.0737 | -0.0322 | -0.0928 | -0.0514 | -0.0309 | +0.0105 | -0.2781 | -0.2367 | C013_cross_pair_currency_strength_rotation | +0.0105 | 0 |
| USD_CAD | -0.0069 | -0.0617 | -0.0548 | -0.0633 | -0.0564 | -0.0117 | -0.0048 | -0.1171 | -0.1102 | C013_cross_pair_currency_strength_rotation | -0.0048 | 0 |
| USD_CHF | +0.0269 | +0.0198 | -0.0070 | -0.0500 | -0.0769 | -0.0340 | -0.0609 | -0.3073 | -0.3342 | C010_session_breakout | -0.0070 | 0 |
| NZD_USD | -0.0986 | -0.0937 | +0.0050 | -0.1097 | -0.0111 | -0.0803 | +0.0183 | -0.1353 | -0.0367 | C013_cross_pair_currency_strength_rotation | +0.0183 | 0 |

## Roll-up
- Material-gap floor: **`+0.05`** R
- Pairs where ANY candidate cleared the null by the material gap: **`['EUR_USD']`**
- Pairs where ANY candidate had ANY positive gap (even within noise): **`['EUR_USD', 'USD_JPY', 'AUD_USD', 'NZD_USD']`**

## Notes

- If a future real candidate's per-pair mean R clears this table's pairs by the material gap, the candidate has a defensible starting point for a formal pre-commit on those pairs only — broadcast claims ("works on all pairs") remain forbidden by the lab's pair-concentration ranking rule.
- The current real-data answer to 'is there a pair where any of CAMPAIGN_010-014 cleanly beat the random-entry null?' is captured by `pairs_materially_above_null_in_any_candidate`.
