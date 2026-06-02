# Crypto Family E Diagnostic 6 — Cross-Asset Confirmation Result

**Sprint:** `crypto-family-e-exploratory-diagnostics-001`
**Type:** Exploratory diagnostic only — no strategy, campaign, front gate, or approval.

**Hypothesis:** BTC/ETH funding agreement strengthens a directional (reversion) signal; disagreement predicts relative-value reversion of the extreme asset.

**Classification:** `rejected`

best cell = agreement_directional h8: gross=4.84e-05, all_in=-1.27e-03, Holm-adj shuffled p=1.000 (does not clear after multiple comparisons).

Agreement = both BTC & ETH funding in the same extreme decile (faded both legs, single-leg cost). Disagreement = one extreme, one neutral (relative-value, paired two-leg cost). Wrong-pairing swaps BTC/ETH returns as a control.

## Horizon 8h (n common windows = 6873)

| Cohort | n legs | gross | all-in | 2× stress | shuffled p |
|--------|-------:|------:|-------:|----------:|-----------:|
| agreement (directional) | 1480 | 0.000048 | -0.001273 | -0.002973 | 0.9530 |
| disagreement (RV) | 2504 | -0.000191 | -0.001836 | -0.003536 | 0.6540 |
| wrong-pairing (control) | 1480 | 0.000048 | -0.001273 | -0.002973 | 0.9550 |

## Horizon 24h (n common windows = 6713)

| Cohort | n legs | gross | all-in | 2× stress | shuffled p |
|--------|-------:|------:|-------:|----------:|-----------:|
| agreement (directional) | 1452 | 0.000901 | 0.000223 | -0.001477 | 0.5140 |
| disagreement (RV) | 2432 | -0.000051 | -0.001617 | -0.003317 | 0.9310 |
| wrong-pairing (control) | 1452 | 0.000901 | 0.000223 | -0.001477 | 0.5150 |

## Why this is not a strategy

Exploratory; explicitly inherits Family B's paired-cost caution.

