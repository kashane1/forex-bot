# Crypto Family E Diagnostic 1 — Funding Mean Reversion Result

**Sprint:** `crypto-family-e-exploratory-diagnostics-001`
**Type:** Exploratory diagnostic only — no strategy, campaign, front gate, or approval.

**Hypothesis:** Extreme positive (negative) 8h funding predicts negative (positive) forward perp returns as crowded carry unwinds.

**Classification:** `rejected`

Single-asset only (not robust across BTC and ETH) and not net-positive — rejected.

Edges are mean per-entry net signed returns (fraction of notional). Funding cashflow (long pays short when funding>0) enters all-in and 2× stress.

## Horizon 8h

| Split | n | gross | spread-only | all-in | 2× stress | shuffled p | matched p> |
|-------|--:|------:|-----------:|-------:|----------:|-----------:|-----------:|
| BTC_PERP_USD | 1376 | 0.000342 | -0.000058 | -0.001003 | -0.002603 | 0.5040 | 0.2510 |
| ETH_PERP_USD | 1376 | -0.000175 | -0.000775 | -0.001660 | -0.003460 | 0.7660 | 0.5890 |
| pooled | 2752 | 0.000083 | -0.000417 | -0.001332 | -0.003032 | 0.8270 | 0.4180 |

Decile cuts (pooled inputs per-instrument): BTC_PERP_USD {'p10': -1.398069332715317e-05, 'p90': 0.00024175587709973875}, ETH_PERP_USD {'p10': -5.264664590684841e-05, 'p90': 0.00024348650187314973}.
Skipped windows: {'BTC_PERP_USD': 80, 'ETH_PERP_USD': 80}.

## Horizon 24h

| Split | n | gross | spread-only | all-in | 2× stress | shuffled p | matched p> |
|-------|--:|------:|-----------:|-------:|----------:|-----------:|-----------:|
| BTC_PERP_USD | 1344 | 0.000523 | 0.000123 | -0.000378 | -0.001978 | 0.5590 | 0.2790 |
| ETH_PERP_USD | 1344 | -0.001142 | -0.001742 | -0.002097 | -0.003897 | 0.3110 | 0.8550 |
| pooled | 2688 | -0.000309 | -0.000809 | -0.001238 | -0.002938 | 0.6770 | 0.6790 |

Decile cuts (pooled inputs per-instrument): BTC_PERP_USD {'p10': -1.398069332715317e-05, 'p90': 0.00024321540765538142}, ETH_PERP_USD {'p10': -5.247308483565314e-05, 'p90': 0.00024296035939755966}.
Skipped windows: {'BTC_PERP_USD': 80, 'ETH_PERP_USD': 80}.

## Horizon 72h

| Split | n | gross | spread-only | all-in | 2× stress | shuffled p | matched p> |
|-------|--:|------:|-----------:|-------:|----------:|-----------:|-----------:|
| BTC_PERP_USD | 1248 | 0.000590 | 0.000190 | 0.000762 | -0.000838 | 0.7020 | 0.3580 |
| ETH_PERP_USD | 1248 | -0.003566 | -0.004166 | -0.003223 | -0.005023 | 0.0940 | 0.9620 |
| pooled | 2496 | -0.001488 | -0.001988 | -0.001231 | -0.002931 | 0.2570 | 0.8810 |

Decile cuts (pooled inputs per-instrument): BTC_PERP_USD {'p10': -1.2825933599337964e-05, 'p90': 0.00024447820367855337}, ETH_PERP_USD {'p10': -5.146954514042776e-05, 'p90': 0.00024261511310940306}.
Skipped windows: {'BTC_PERP_USD': 80, 'ETH_PERP_USD': 80}.

## Why this is not a strategy

One exploratory conditional-return statistic. No sizing, execution, walk-forward, or portfolio construction. A statistically-real effect is not a tradable edge.

## Front-gate eligibility: no

