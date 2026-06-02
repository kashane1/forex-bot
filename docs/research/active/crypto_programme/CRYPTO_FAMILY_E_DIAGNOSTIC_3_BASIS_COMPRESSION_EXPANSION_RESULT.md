# Crypto Family E Diagnostic 3 — Basis Compression / Expansion Result

**Sprint:** `crypto-family-e-exploratory-diagnostics-001`
**Type:** Exploratory diagnostic only — no strategy, campaign, front gate, or approval.

**Hypothesis:** 

**Classification:** `rejected`

No effect distinguishable from the matched null; rejected.

Edges are mean per-entry net signed returns (fraction of notional). Funding cashflow (long pays short when funding>0) enters all-in and 2× stress.

## Horizon 4h

| Split | n | gross | spread-only | all-in | 2× stress | shuffled p | matched p> |
|-------|--:|------:|-----------:|-------:|----------:|-----------:|-----------:|
| BTC_PERP_USD | 11174 | 0.000165 | -0.000235 | -0.001414 | -0.003014 | 0.1730 | 0.0990 |
| ETH_PERP_USD | 11174 | 0.000312 | -0.000288 | -0.001462 | -0.003262 | 0.0490 | 0.0310 |
| pooled | 22348 | 0.000238 | -0.000262 | -0.001438 | -0.003138 | 0.0170 | 0.0090 |

Decile cuts (pooled inputs per-instrument): BTC_PERP_USD {'p10': -56.1358719465361, 'p90': 62.129466000883106}, ETH_PERP_USD {'p10': -77.3887329422275, 'p90': 82.01971987952385}.
Skipped windows: {'BTC_PERP_USD': 321, 'ETH_PERP_USD': 321}.

## Horizon 24h

| Split | n | gross | spread-only | all-in | 2× stress | shuffled p | matched p> |
|-------|--:|------:|-----------:|-------:|----------:|-----------:|-----------:|
| BTC_PERP_USD | 10854 | -0.000125 | -0.000525 | -0.001616 | -0.003216 | 0.7010 | 0.6640 |
| ETH_PERP_USD | 10854 | 0.000398 | -0.000202 | -0.001278 | -0.003078 | 0.3140 | 0.1630 |
| pooled | 21708 | 0.000137 | -0.000363 | -0.001447 | -0.003147 | 0.5820 | 0.3000 |

Decile cuts (pooled inputs per-instrument): BTC_PERP_USD {'p10': -55.800636873804685, 'p90': 61.92995328600589}, ETH_PERP_USD {'p10': -77.02638716256715, 'p90': 81.69091462458202}.
Skipped windows: {'BTC_PERP_USD': 321, 'ETH_PERP_USD': 321}.

Expansion/momentum variant (opposite signs) reported in the JSON artifact `diagnostic_3_basis_compression_expansion.json` under `expansion`.

## Why this is not a strategy

One exploratory conditional-return statistic. No sizing, execution, walk-forward, or portfolio construction. A statistically-real effect is not a tradable edge.

## Front-gate eligibility: no

