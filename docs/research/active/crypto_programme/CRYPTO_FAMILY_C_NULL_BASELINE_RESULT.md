# Crypto Family C Null Baseline Result

**Seed:** 42 · **Trials by TF:** {'M15': 100, 'H1': 200, 'H4': 300, 'D1': 500}

| Instrument | TF | AC1 obs | shuffle p | sign-flip p | block-boot p |
|------------|-----|--------:|----------:|------------:|-------------:|
| BTC_USD | M15 | 0.0349 | 0.0000 | 0.0000 | 0.5200 |
| BTC_USD | H1 | 0.0049 | 0.7800 | 0.8000 | 0.6200 |
| BTC_USD | H4 | -0.0093 | 0.4133 | 0.5067 | 0.9333 |
| BTC_USD | D1 | -0.0334 | 0.1560 | 0.3080 | 0.3640 |
| ETH_USD | M15 | -0.0053 | 0.7200 | 0.7600 | 0.9600 |
| ETH_USD | H1 | 0.0015 | 0.9400 | 0.9800 | 0.2500 |
| ETH_USD | H4 | 0.0166 | 0.1467 | 0.2800 | 0.2733 |
| ETH_USD | D1 | -0.0352 | 0.1560 | 0.2440 | 0.8400 |

Interpretation: low p-value vs null suggests observed AC1 is unlikely under iid/random-sign assumptions; does **not** imply tradability after costs.

Artifact: `research/crypto/diagnostics/family_c_trend_persistence_001/null_baseline.json`
