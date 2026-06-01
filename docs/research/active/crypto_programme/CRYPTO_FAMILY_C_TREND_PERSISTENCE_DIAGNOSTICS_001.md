# Crypto Family C Trend Persistence Diagnostics 001

**Sprint:** `crypto-family-c-trend-persistence-diagnostics-001`
**Type:** Exploratory diagnostic only — no strategy, campaign, or approval
**Window:** `2021-05-31T00:00:00+00:00` → `2026-05-31T23:57:53+00:00`
**Source:** `m1_materialized` (UTC-aligned materialized candles)

---

## 1. Explicit statements

- **No strategy created.** `configs/approved_strategies.yaml` unchanged.
- **No campaign created.** No front-gate run.
- **No approval granted.** Research freeze preserved.
- **No factor promoted to production.** Exploratory statistics only.

---

## 2. Trend persistence summary (lag-1 return autocorrelation)

| Instrument | M15 AC1 | H1 AC1 | H4 AC1 | D1 AC1 |
|------------|--------:|-------:|-------:|-------:|
| BTC_USD | 0.0005 | -0.0019 | -0.0046 | -0.0334 |
| ETH_USD | 0.0129 | 0.0087 | -0.0039 | -0.0352 |

Positive AC1 suggests short-horizon trend persistence (momentum). Values near zero indicate random-walk-like behavior.

---

## 3. Null baseline (block-bootstrap autocorrelation)

| Instrument | TF | Actual AC1 | Null mean | Null p95 | p-value |
|------------|-----|----------:|----------:|---------:|--------:|
| BTC_USD | M15 | 0.0005 | 0.0022 | 0.0031 | 0.9950 |
| BTC_USD | H1 | -0.0019 | -0.0037 | -0.0023 | 0.0200 |
| BTC_USD | H4 | -0.0046 | -0.0026 | 0.0009 | 0.8050 |
| BTC_USD | D1 | -0.0334 | -0.0276 | -0.0212 | 0.9400 |
| ETH_USD | M15 | 0.0129 | 0.0119 | 0.0129 | 0.0550 |
| ETH_USD | H1 | 0.0087 | 0.0092 | 0.0107 | 0.7100 |
| ETH_USD | H4 | -0.0039 | -0.0057 | -0.0026 | 0.1800 |
| ETH_USD | D1 | -0.0352 | -0.0308 | -0.0236 | 0.8450 |

---

## 4. Momentum proxy — cost sensitivity (annualized Sharpe)

Signal: always-in-market sign of cumulative lookback return. Costs applied on position flips using frozen `CRYPTO_COST_MODEL_001.md`.

### BTC_USD

| TF | Lookback | Gross | Spread-only | All-in | 2× stress |
|----|---------:|------:|------------:|-------:|----------:|
| M15 | 4 | -0.0723 | -14.8895 | -84.0033 | -93.5907 |
| H1 | 4 | 0.0921 | -3.9376 | -33.3498 | -41.2734 |
| H4 | 6 | -0.3090 | -1.0995 | -8.7173 | -12.3380 |
| D1 | 5 | -0.5574 | -0.7065 | -2.3420 | -3.3739 |

### ETH_USD

| TF | Lookback | Gross | Spread-only | All-in | 2× stress |
|----|---------:|------:|------------:|-------:|----------:|
| M15 | 4 | 1.0012 | -16.9748 | -77.9377 | -89.7367 |
| H1 | 4 | 0.3605 | -4.4875 | -29.1057 | -37.8350 |
| H4 | 6 | -0.2787 | -1.2492 | -7.3792 | -10.8482 |
| D1 | 5 | -0.1702 | -0.3417 | -1.5430 | -2.3912 |

---

## 5. Regime sensitivity (vol tercile AC1)

| Instrument | TF | Low-vol AC1 | High-vol AC1 |
|------------|-----|----------:|-------------:|
| BTC_USD | M15 | -0.0265 | -0.0061 |
| BTC_USD | H1 | -0.0131 | -0.0051 |
| BTC_USD | H4 | 0.0279 | -0.0241 |
| BTC_USD | D1 | 0.0779 | -0.0580 |
| ETH_USD | M15 | -0.0083 | 0.0079 |
| ETH_USD | H1 | 0.0080 | 0.0065 |
| ETH_USD | H4 | 0.0357 | -0.0427 |
| ETH_USD | D1 | -0.0016 | -0.0585 |

---

## 6. Run-length statistics

| Instrument | TF | Mean run | Max run | Run count |
|------------|-----|--------:|--------:|----------:|
| BTC_USD | M15 | 1.91 | 16 | 91499 |
| BTC_USD | H1 | 1.89 | 14 | 23094 |
| BTC_USD | H4 | 1.85 | 11 | 5892 |
| BTC_USD | D1 | 1.89 | 10 | 943 |
| ETH_USD | M15 | 1.91 | 14 | 91510 |
| ETH_USD | H1 | 1.89 | 13 | 23094 |
| ETH_USD | H4 | 1.89 | 12 | 5772 |
| ETH_USD | D1 | 1.86 | 9 | 954 |

---

## 7. Verdict

Positive return autocorrelation appears at one or more horizons, but the simple momentum proxy does not survive spread+fee costs at any horizon under frozen assumptions. Directional structure may exist but is likely untradeable at this turnover.

**Classification:** PERSISTENCE_DETECTED_BUT_COST_DEFEATED

---

## 8. Artifact

`research/crypto/diagnostics/family_c_trend_persistence_001.json`
