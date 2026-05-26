# C008 Cross-Asset Regime Overlay

**Diagnostic only** — `strategy_evidence: false`

Source: `research/c008_post_mortem/c008_cross_asset_regime_overlay.json` — 354 C008 trades joined to full-window FRED features via D+1 availability rule. Fixed descriptive buckets (same thresholds as confluence prototype). No optimization.

## Join coverage

354/354 screening-window trades joined. Full-window FRED layer now available (prior sprint eliminated `cross_asset_missing`).

## Train vs validation regime mix

| bucket | train count | validation count | notes |
|---|---:|---:|---|
| usd_regime=strengthening | 216 | 138 | all trades (DXY >97 threshold era) |
| risk_regime=risk_off | 76 | 0 | train only |
| risk_regime=neutral | 73 | 9 | mostly train |
| risk_regime=risk_on | 67 | **129** | validation dominated |
| rates_bias=flat | 136 | 0 | train era |
| rates_bias=higher | 80 | **138** | validation era |
| yield_curve=positive | 177 | 14 | train |
| yield_curve=inverted | 39 | **124** | validation |

**Descriptive shift:** validation trades occurred during a different macro mix — predominantly risk-on, higher rates, inverted curve — vs train's mixed risk/neutral/off and flatter rates.

## Winners vs losers (all splits)

Winners (104 trades) vs losers (250): both occur under strengthening USD label (fixed threshold artifact). Risk-off headwind appears more in losers' era mix but **cannot** be used to claim a filter improves edge.

## Pair-level validation

All six validation pairs show strengthening USD + higher rates + mostly inverted curve — consistent with 2023–2024 macro, not pair-specific alpha.

## Expectancy by USD regime label

| split | strengthening USD exp R |
|---|---:|
| train | −0.025 |
| validation | +0.161 |

Same fixed bucket label, different outcomes — regime label alone does not explain train/val split; exit anatomy (time vs stop) dominates.

## Rules observed

- No threshold optimization.
- No feature shopping.
- No claim that any feature improves edge.

## Disclaimer

Descriptive overlay only. Not strategy evidence.
