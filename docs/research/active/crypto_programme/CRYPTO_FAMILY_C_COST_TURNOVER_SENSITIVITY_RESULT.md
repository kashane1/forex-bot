# Crypto Family C Cost and Turnover Sensitivity Result

Frozen costs: `CRYPTO_COST_MODEL_001.md`. Diagnostic momentum proxy only.

| Instrument | TF | Gross bps | Spread-only bps | All-in bps | 2× stress bps | All-in hurdle |
|------------|-----|----------:|----------------:|-----------:|--------------:|--------------:|
| BTC_USD | M15 | -0.01 | -10.01 | -134.01 | -228.01 | 134 |
| BTC_USD | H1 | 0.06 | -9.94 | -133.94 | -227.94 | 134 |
| BTC_USD | H4 | -0.75 | -10.75 | -130.75 | -220.75 | 130 |
| BTC_USD | D1 | -8.38 | -18.38 | -138.38 | -228.38 | 130 |
| ETH_USD | M15 | 0.20 | -15.80 | -139.80 | -239.80 | 140 |
| ETH_USD | H1 | 0.29 | -15.71 | -139.71 | -239.71 | 140 |
| ETH_USD | H4 | -0.89 | -16.89 | -136.89 | -232.89 | 136 |
| ETH_USD | D1 | -3.39 | -19.39 | -139.39 | -235.39 | 136 |

## Momentum proxy Sharpe (annualized)

### BTC_USD
| TF | Gross | Spread-only | All-in | 2× stress |
|----|------:|------------:|-------:|----------:|
| M15 | -0.0723 | -14.8895 | -84.0033 | -93.5907 |
| H1 | 0.0921 | -3.9376 | -33.3498 | -41.2734 |
| H4 | -0.3090 | -1.0995 | -8.7173 | -12.3380 |
| D1 | -0.5574 | -0.7065 | -2.3420 | -3.3739 |

### ETH_USD
| TF | Gross | Spread-only | All-in | 2× stress |
|----|------:|------------:|-------:|----------:|
| M15 | 1.0012 | -16.9748 | -77.9377 | -89.7367 |
| H1 | 0.3605 | -4.4875 | -29.1057 | -37.8350 |
| H4 | -0.2787 | -1.2492 | -7.3792 | -10.8482 |
| D1 | -0.1702 | -0.3417 | -1.5430 | -2.3912 |

Artifact: `research/crypto/diagnostics/family_c_trend_persistence_001/cost.json`
