# CAMPAIGN_028 — relative-value spread reversion front-gate screen

> Exploratory edge-discovery lab output. Train-only. Not a strategy verdict; 
> does not approve, promote, or change any campaign status. 
> See `docs/research/CAMPAIGN_028_NEW_THESIS_BRIEF.md`.

## Setup

- Train window: `2020-01-01` → `2022-12-31`
- Lookback: `60`  Threshold |z|: `2.0`  Hold (bars): `12`
- Financing stress: `True`  Candidate spreads: `21`

## Per-spread screen (sorted by post-cost mean)

| spread | beta | n | half-life | spread/ATR | cost flags | pre-cost | post-cost | null band | gap σ | filter adds edge |
|---|---:|---:|---:|---:|---|---:|---:|---|---:|:--:|
| USD_CAD-USD_CHF | +0.684 | 670 | 423.4 | 0.217 | COST_FEASIBLE | +0.001409 | +0.000898 | materially_above_null | +21.83 | yes |
| USD_CAD-USD_JPY | +0.047 | 705 | 529.8 | 0.111 | COST_FEASIBLE | +0.000758 | +0.000491 | materially_above_null | +10.53 | yes |
| AUD_USD-USD_CAD | -1.392 | 651 | 295.5 | 0.323 | COST_HOSTILE | +0.001126 | +0.000376 | materially_above_null | +23.39 | yes |
| GBP_USD-USD_CAD | -1.168 | 689 | 421.9 | 0.205 | COST_FEASIBLE | +0.000944 | +0.000370 | materially_above_null | +9.96 | yes |
| GBP_USD-NZD_USD | +0.875 | 692 | 126.4 | 0.263 | COST_HOSTILE | +0.000880 | +0.000224 | materially_above_null | +11.59 | yes |
| AUD_USD-GBP_USD | +0.820 | 709 | 292.5 | 0.237 | COST_FEASIBLE | +0.000785 | +0.000146 | materially_above_null | +17.12 | yes |
| EUR_USD-USD_CAD | -0.801 | 654 | 1194.8 | 0.232 | COST_FEASIBLE | +0.000393 | -0.000093 | materially_above_null | +6.99 | yes |
| EUR_USD-USD_JPY | -0.519 | 744 | 332.0 | 0.197 | COST_FEASIBLE | +0.000161 | -0.000341 | materially_above_null | +3.59 | yes |
| NZD_USD-USD_CAD | -1.383 | 767 | 401.8 | 0.306 | COST_HOSTILE | +0.000365 | -0.000402 | materially_above_null | +12.79 | yes |
| GBP_USD-USD_CHF | -1.515 | 733 | 269.7 | 0.247 | COST_FEASIBLE | +0.000421 | -0.000447 | materially_above_null | +5.51 | yes |
| EUR_USD-GBP_USD | +0.914 | 682 | 282.5 | 0.247 | COST_FEASIBLE | -0.000043 | -0.000591 | within_null | -0.98 | no |
| EUR_USD-NZD_USD | +0.816 | 708 | 315.8 | 0.286 | COST_HOSTILE | -0.000060 | -0.000695 | slightly_below_null | -1.81 | no |
| GBP_USD-USD_JPY | -0.420 | 736 | 404.0 | 0.134 | COST_FEASIBLE | -0.000247 | -0.000705 | materially_below_null | -2.66 | no |
| USD_CHF-USD_JPY | +0.186 | 756 | 248.8 | 0.191 | COST_FEASIBLE | -0.000292 | -0.000753 | materially_below_null | -9.33 | no |
| AUD_USD-NZD_USD | +0.877 | 704 | 316.4 | 0.517 | COST_HOSTILE | -0.000090 | -0.000867 | slightly_below_null | -1.75 | no |
| NZD_USD-USD_JPY | -0.376 | 787 | 452.5 | 0.172 | COST_FEASIBLE | -0.000771 | -0.001351 | materially_below_null | -15.00 | no |
| EUR_USD-USD_CHF | -1.686 | 775 | 287.2 | 0.339 | COST_HOSTILE | -0.000445 | -0.001382 | materially_below_null | -6.20 | no |
| NZD_USD-USD_CHF | -1.730 | 740 | 165.7 | 0.290 | COST_HOSTILE | -0.000308 | -0.001398 | materially_below_null | -2.70 | no |
| AUD_USD-USD_CHF | -1.520 | 757 | 219.2 | 0.275 | COST_HOSTILE | -0.000565 | -0.001555 | materially_below_null | -9.10 | no |
| AUD_USD-EUR_USD | +0.728 | 740 | 374.1 | 0.227 | COST_FEASIBLE | -0.001183 | -0.001798 | materially_below_null | -79.18 | no |
| AUD_USD-USD_JPY | -0.238 | 760 | 477.0 | 0.146 | COST_FEASIBLE | -0.001543 | -0.002046 | materially_below_null | -41.73 | no |

## Best-of-N matrix sanity (selection-noise check)

- Variants screened: `21`
- Best: `USD_CAD-USD_CHF` = `+0.000898` (median `-0.000591`)
- Null reference: `0.0`  best vs null: `0.0008976467165089581`
- Expected best-of-N under noise: `+0.001548` (p95 `+0.002283`)
- Deflated improvement: `-0.000650`
- P(best ≤ noise max): `0.949`
- Flags: `LIKELY_SELECTION_NOISE`

## Reading this (front-gate decision logic)

- A spread is a live candidate only if it is `COST_FEASIBLE`, its post-cost 
  mean is `materially_above_null`, and `filter adds edge = yes`.
- The whole thesis advances to a precommit scaffold only if the best spread is 
  `ROBUST_MATRIX_SIGNAL` (not `LIKELY_SELECTION_NOISE`) across the candidate set.
- Any other outcome → CAMPAIGN_028 is written up as a documented rejection, 
  freeze intact, exactly as C026 closed the timeframe ladder.

