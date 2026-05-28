# C022 Winner/Loser Feature-Separation — Result

**Status:** diagnostic only. No verdict change, no approval, no tuning, no C024. Findings are hypothesis-generating; no threshold is a parameter.

## Setup

- Winner definition: `profitable_trade = result_r > 0`.
- Trades: 2396 (train 1369, validation 1027).
- Overall win rate: 0.326 (train 0.336, validation 0.3126).
- Effect = |AUC−0.5|; negligible below 0.05. Stable = train & validation AUC on the same side of 0.5.

## Headline

**No structural entry-signal feature separates winners from losers.** The features the C022 thesis is built on — H4 regime (ADX, bias score, EMA slope, distance), H1 pullback (depth, RSI, distance), M15 trigger (reclaim distance, ADX, body) — all sit at AUC ≈ 0.50. The strongest stable signal-quality effect is only |AUC−0.5| = 0.0442 (below the 0.05 floor).

The only stable separators above the negligibility floor are **context**, not entry-signal quality: cost (spread/ATR, |AUC−0.5|=0.0766 — mechanical, since cost reduces net R directly, not an edge), volatility (atr_at_entry, 0.0684), and time-of-day (hour, 0.0739). All are weak (AUC ≲ 0.58).

## Strongest stable separators (conservative cross-split effect)

| feature | min abs(AUC−0.5) | AUC train | AUC val | median winner | median loser |
|---|---|---|---|---|---|
| spread_to_atr_pct | 0.0766 | 0.4234 | 0.4069 | 18.300072 | 21.639747 |
| hour | 0.0739 | 0.5739 | 0.5746 | 13.0 | 11.0 |
| atr_at_entry | 0.0684 | 0.5684 | 0.581 | 0.000892 | 0.000738 |
| h4_close_dist_ema50_atr | 0.0442 | 0.5442 | 0.5548 | 2.657885 | 2.449311 |
| h1_pullback_depth_atr | 0.0371 | 0.5453 | 0.5371 | 1.071659 | 0.91578 |
| spread_pips | 0.014 | 0.486 | 0.4817 | 1.6 | 1.6 |
| m15_reclaim_distance_atr | 0.0065 | 0.4935 | 0.4854 | 0.308252 | 0.326555 |
| m15_adx_at_entry | 0.0041 | 0.5041 | 0.5208 | 23.465143 | 23.296613 |

## All numeric entry features (AUC train / validation)

| feature | family | AUC train | AUC val | stable | quintile win-rate | n_missing |
|---|---|---|---|---|---|---|
| spread_to_atr_pct | cost | 0.4234 | 0.4069 | yes | [0.425, 0.3925, 0.2797, 0.2818, 0.2505] | 0 |
| hour | context_time | 0.5739 | 0.5746 | yes | [0.2727, 0.2569, 0.2945, 0.4694, 0.3796] | 0 |
| atr_at_entry | context_volatility | 0.5684 | 0.581 | yes | [0.2812, 0.215, 0.3445, 0.3946, 0.3946] | 0 |
| h1_pullback_depth_atr | signal_quality | 0.5453 | 0.5371 | yes | [0.3333, 0.2568, 0.2902, 0.3528, 0.3967] | 0 |
| h4_close_dist_ema50_atr | signal_quality | 0.5442 | 0.5548 | yes | [0.2458, 0.3466, 0.334, 0.3236, 0.38] | 0 |
| m15_close_dist_ema50_atr | signal_quality | 0.4708 | 0.5037 | no | [0.3354, 0.3111, 0.3424, 0.3466, 0.2944] | 0 |
| h4_adx_at_entry | signal_quality | 0.5153 | 0.5006 | yes | [0.2958, 0.3486, 0.3319, 0.3208, 0.3326] | 0 |
| h4_bias_score | signal_quality | 0.5152 | 0.4836 | no | None | 0 |
| spread_pips | cost | 0.486 | 0.4817 | yes | [0.336, 0.3387, 0.31, 0.3256, 0.3144] | 0 |
| h1_rsi_at_entry | signal_quality | 0.5092 | 0.5014 | yes | [0.3583, 0.2965, 0.3278, 0.2735, 0.3737] | 0 |
| m15_reclaim_distance_atr | signal_quality | 0.4935 | 0.4854 | yes | [0.3333, 0.3361, 0.3278, 0.3152, 0.3173] | 0 |
| m15_adx_at_entry | signal_quality | 0.5041 | 0.5208 | yes | [0.2979, 0.3048, 0.3695, 0.3507, 0.3069] | 0 |
| h1_close_dist_ema50_atr | signal_quality | 0.5033 | 0.5244 | yes | [0.3271, 0.309, 0.3215, 0.334, 0.3382] | 0 |
| m15_body_atr | signal_quality | 0.4973 | 0.4784 | yes | [0.3375, 0.3278, 0.3257, 0.3236, 0.3152] | 0 |
| h4_ema_slope_atr | signal_quality | 0.4995 | 0.497 | yes | [0.3125, 0.3319, 0.3716, 0.3027, 0.3111] | 0 |

## Categorical win-rate breakdown

### instrument

| value | train n | train win-rate | val n | val win-rate |
|---|---|---|---|---|
| AUD_USD | 166 | 0.3253 | 205 | 0.2976 |
| EUR_USD | 207 | 0.3188 | 67 | 0.209 |
| GBP_USD | 236 | 0.3475 | 74 | 0.2568 |
| NZD_USD | 78 | 0.2821 | 189 | 0.3492 |
| USD_CAD | 275 | 0.3309 | 149 | 0.2685 |
| USD_CHF | 274 | 0.3613 | 170 | 0.3 |
| USD_JPY | 133 | 0.3459 | 173 | 0.4046 |

### side

| value | train n | train win-rate | val n | val win-rate |
|---|---|---|---|---|
| long | 647 | 0.3462 | 516 | 0.3004 |
| short | 722 | 0.3269 | 511 | 0.3249 |

### session_bucket

| value | train n | train win-rate | val n | val win-rate |
|---|---|---|---|---|
| asia | 291 | 0.2955 | 248 | 0.246 |
| late | 11 | 0.3636 | 29 | 0.2414 |
| london | 404 | 0.2574 | 268 | 0.25 |
| london_ny_overlap | 425 | 0.3976 | 349 | 0.3954 |
| new_york | 238 | 0.4076 | 133 | 0.3609 |

### weekday

| value | train n | train win-rate | val n | val win-rate |
|---|---|---|---|---|
| Fri | 256 | 0.2969 | 211 | 0.2512 |
| Mon | 248 | 0.3427 | 179 | 0.3408 |
| Sun | 2 | 0.5 | 4 | 0.75 |
| Thu | 266 | 0.3722 | 206 | 0.3447 |
| Tue | 318 | 0.3836 | 218 | 0.2798 |
| Wed | 279 | 0.276 | 209 | 0.3445 |

### volatility_regime

| value | train n | train win-rate | val n | val win-rate |
|---|---|---|---|---|
| high | 578 | 0.4031 | 223 | 0.3991 |
| low | 295 | 0.2847 | 505 | 0.2515 |
| med | 496 | 0.2883 | 299 | 0.3512 |

## Anti-overfit warning

No threshold selected as a parameter. Any separating feature is hypothesis-generating only. 'Stable' = train & validation AUC on the same side of 0.5; effect = |AUC-0.5|; negligible below 0.05 (~AUC 0.55).

Any apparent separator is a candidate hypothesis only. It must survive a pre-committed, out-of-sample test in a *separate* future sprint before it could justify a C024 entry filter. No threshold here is a campaign parameter.
