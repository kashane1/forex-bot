# Crypto Family C Baseline Trend Persistence Result

**Sprint:** `crypto-family-c-trend-persistence-diagnostics-001`
**Type:** Exploratory diagnostic only — no strategy, campaign, or approval

---

## Autocorrelation by lag

| Instrument | TF | AC1 | AC2 | AC4 | AC8 |
|------------|-----|----:|----:|----:|----:|
| BTC_USD | M15 | 0.0005 | -0.0142 | -0.0021 | 0.0037 |
| BTC_USD | H1 | -0.0019 | -0.0037 | 0.0016 | 0.0039 |
| BTC_USD | H4 | -0.0046 | 0.0115 | 0.0148 | 0.0019 |
| BTC_USD | D1 | -0.0334 | -0.0101 | 0.0281 | -0.0369 |
| ETH_USD | M15 | 0.0129 | -0.0126 | 0.0012 | 0.0073 |
| ETH_USD | H1 | 0.0087 | -0.0076 | 0.0029 | 0.0081 |
| ETH_USD | H4 | -0.0039 | 0.0205 | 0.0084 | -0.0012 |
| ETH_USD | D1 | -0.0352 | -0.0077 | 0.0055 | -0.0311 |

## Run-length and continuation

| Instrument | TF | Mean run | P(cont|2 bars) | P(cont|4 bars) |
|------------|-----|--------:|---------------:|---------------:|
| BTC_USD | M15 | 1.91 | 0.4563 | 0.4297 |
| BTC_USD | H1 | 1.89 | 0.4478 | 0.4221 |
| BTC_USD | H4 | 1.85 | 0.4490 | 0.4333 |
| BTC_USD | D1 | 1.89 | 0.4594 | 0.4593 |
| ETH_USD | M15 | 1.91 | 0.4554 | 0.4290 |
| ETH_USD | H1 | 1.89 | 0.4544 | 0.4294 |
| ETH_USD | H4 | 1.89 | 0.4599 | 0.4461 |
| ETH_USD | D1 | 1.86 | 0.4478 | 0.4767 |

## Horizon cross (diagnostic only)

- **BTC_USD H4_to_M15:** n=10906, mean=0.0004, hit=0.5646
- **BTC_USD D1_to_H1:** n=1782, mean=0.0009, hit=0.5449
- **ETH_USD H4_to_M15:** n=10897, mean=0.0006, hit=0.5711
- **ETH_USD D1_to_H1:** n=1778, mean=0.0009, hit=0.5292

Artifact: `research/crypto/diagnostics/family_c_trend_persistence_001/baseline.json`
