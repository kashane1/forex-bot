# Crypto Family B Relative Value Diagnostics 001 — Summary

**Sprint:** `crypto-family-b-relative-value-diagnostics-001`
**Date:** 2026-06-01
**Branch:** `main`

---

## 1. Current branch

`main`

## 2. Commit hashes by phase

| Phase | Commit |
|-------|--------|
| 0 | `7d4d7c7` |
| 1 | `f888263` |
| fix | `2467406` |
| 2 | `642db94` |
| 3 | `0243ae2` |
| 4 | `3e0b787` |
| 5 | `0fc3888` |
| 6 | `bb974a3` |
| 7 | `836e640` |
| 8 | `9cd52f8` |
| 9 | *(this commit − 1)* |
| 10 | *(this commit)* |

## 3. Files changed by phase

See plan §11; artifacts under `research/crypto/diagnostics/family_b_relative_value_001/`.

## 4. Commands run

`pytest tests/ -q`, research freeze, archive validation, secret scan, ruff, `run_crypto_family_b_relative_value_diagnostics.py`, `git status --short`

## 5. Validation results

| Check | Result |
|-------|--------|
| pytest | 2489 passed |
| research freeze | PASS |
| archive validation | PASS |
| secret scan | PASS |
| ruff | 40 pre-existing issues |

## 6. Dataset used

Coinbase spot `m1_materialized`, Postgres, `2021-05-31T00:00:00Z` → `2026-05-31T23:57:53Z`, timestamp intersection only, no interpolation.

## 7. Assets analyzed

`BTC_USD`, `ETH_USD`

## 8. Timeframes analyzed

M15, H1, H4 (`H4M1`), D1

## 9. Cost assumptions used

Frozen `CRYPTO_COST_MODEL_001.md`; one-leg and paired (BTC+ETH) round-trip for gross, spread-only, all-in, 2× stress.

## 10. Null methods used

Shuffle, sign-flip, block-bootstrap; seed 42; subsample ≤8000; trials 100–500 by TF.

## 11. BTC → ETH lead-lag headline

High same-bar correlation (~0.85); lag-1 directional gross **~0.19 bps (M15)**, **~0.03 bps (H1)** — not economically significant vs paired costs.

## 12. ETH → BTC lead-lag headline

Lag-1 gross **~0.06 bps (M15)**, **~-0.28 bps (H1)** — negligible.

## 13. Relative momentum headline

Strongest gross quintile spread **H4 lookback 3: +4.56 bps** (top-minus-bottom); all horizons **fail** all-in paired survival.

## 14. Divergence/reversion headline

H4 short-spread |z|≥2 events show **~8.8 bps** gross paired reversion proxy; still **below ~266 bps** all-in paired hurdle.

## 15. Strongest timeframe

**H4**

## 16. Strongest effect family

**Relative momentum** (lookback 3 quintile spread)

## 17. Regime sensitivity result

Effects vary by vol/correlation tercile; no regime achieves all-in paired survival (see regime report).

## 18. Spread-only one-leg result

Lead-lag gross sub-bps to ~0.2 bps; **no** one-leg spread-only net survival at traded frequency.

## 19. Spread-only paired result

**No survival** (paired spread ~26 bps M15 vs gross effects under 5 bps).

## 20. All-in paired result

**No survival** (paired hurdle ~266–274 bps).

## 21. 2× stress result

**No survival**

## 22. Comparison to Family C

Gross scale **larger** (H4 ~4.6 bps vs Family C ~0.2 bps edge) but **same cost defeat**; Family C Sharpe illusion does not translate to paired RV tradability.

## 23. Comparison to FX S4

Same class: **statistically visible, economically cost-band trapped** (FX S4 “real but too weak”); crypto paired fees dominate single-digit bps gross.

## 24. Synthesis classification

**`STATISTICAL_ONLY_COST_DEFEATED`**

## 25. Family B factor validation?

**No**

## 26. Strategy created?

**No**

## 27. Campaign created?

**No**

## 28. Approved strategies empty?

**Yes**

## 29. Paper/demo/live blocked?

**Yes**

## 30. Raw data committed?

**No**

## 31. Recommended next sprint

**Family D or E selection** — `NEXT_PROMPT_CRYPTO_FAMILY_D_OR_E_SELECTION_001.md`

## 32. Files to review first

1. `CRYPTO_FAMILY_B_RELATIVE_VALUE_DIAGNOSTICS_001_SYNTHESIS.md`
2. `CRYPTO_FAMILY_B_COST_AND_FX_S4_COMPARISON_RESULT.md`
3. `CRYPTO_FAMILY_B_RELATIVE_MOMENTUM_RESULT.md`
4. `research/crypto/diagnostics/family_b_relative_value_001/full.json`
