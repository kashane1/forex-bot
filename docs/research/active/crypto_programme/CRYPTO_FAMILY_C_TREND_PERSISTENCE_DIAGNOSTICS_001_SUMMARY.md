# Crypto Family C Trend Persistence Diagnostics 001 — Summary

**Sprint:** `crypto-family-c-trend-persistence-diagnostics-001`
**Date:** 2026-06-01
**Branch:** `main`

---

## 1. Current branch

`main` (no feature branch; no worktree)

---

## 2. Commit hashes by phase

| Phase | Commit | Message |
|-------|--------|---------|
| 0 | `78b9f8e` | Phase 0 plan |
| 1 | `f040d0c` | Phase 1 diagnostic loader and analytics |
| 2 | `a3165eb` | Phase 2 baseline results |
| 3 | `7eee174` | Phase 3 null baseline |
| 4 | `4d9a57e` | Phase 4 regime sensitivity |
| 5 | `5c7ee25` | Phase 5 cost/turnover |
| 6 | `a760ca3` | Phase 6 synthesis |
| 7 | `6834d63` | Phase 7 next prompt (Family B) |
| 8 | `8abddfb` | Phase 8 programme index |
| 9 | *(this commit)* | Phase 9 summary |

*Note:* Prior exploratory commit `7a553a8` superseded by phased sprint artifacts under `family_c_trend_persistence_001/`.

---

## 3. Files changed by phase

| Phase | Key paths |
|-------|-----------|
| 0 | `CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001_PLAN.md` |
| 1 | `research/crypto/diagnostics/*`, `scripts/run_crypto_family_c_trend_persistence_diagnostics.py`, `tests/test_crypto_trend_persistence_diagnostics.py` |
| 2 | `CRYPTO_FAMILY_C_BASELINE_TREND_PERSISTENCE_RESULT.md`, `.../baseline.json` |
| 3 | `CRYPTO_FAMILY_C_NULL_BASELINE_RESULT.md`, `.../null_baseline.json` |
| 4 | `CRYPTO_FAMILY_C_REGIME_SENSITIVITY_RESULT.md`, `.../regime.json` |
| 5 | `CRYPTO_FAMILY_C_COST_TURNOVER_SENSITIVITY_RESULT.md`, `.../cost.json` |
| 6 | `CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001_SYNTHESIS.md`, `.../full.json`, index MD |
| 7 | `NEXT_PROMPT_CRYPTO_FAMILY_B_RELATIVE_VALUE_DIAGNOSTICS_001.md` |
| 8 | `README.md`, `CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md` |
| 9 | This summary |

---

## 4. Commands run

```bash
pytest tests/ -q
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
ruff check src tests scripts research
python scripts/run_crypto_family_c_trend_persistence_diagnostics.py
git status --short
```

---

## 5. Validation results

| Check | Result |
|-------|--------|
| pytest | **2483 passed** |
| research freeze | **PASS** |
| archive validation | **PASS** |
| secret scan | **PASS** |
| ruff | **40 pre-existing/style issues** (documented; not sprint-blocking) |
| working tree | clean after Phase 9 commit |

---

## 6. Dataset used

- **Venue:** Coinbase spot → `m1_materialized` in local Postgres
- **Window:** `2021-05-31T00:00:00Z` → `2026-05-31T23:57:53Z`
- **Env:** `FOREX_BOT_RESEARCH_DATABASE_URL`
- **Policy:** available bars only; **no gap interpolation**

---

## 7. Assets analyzed

`BTC_USD`, `ETH_USD`

---

## 8. Timeframes analyzed

M15, H1, H4 (`H4M1` storage), D1

---

## 9. Cost assumptions used

Frozen `CRYPTO_COST_MODEL_001.md`: BTC half-spread 5 bps, ETH 8 bps, taker RT 120 bps, horizon slippage M15/H1 2 bps/leg, H4/D1 0. Four variants: gross, spread-only, all-in, 2× stress.

---

## 10. Null methods used

- IID shuffle of log returns
- Random sign flips
- Block bootstrap (TF-scaled block size)
- **Seed:** 42
- **Trials:** M15 100, H1 200, H4 300, D1 500 (subsample cap 8000 returns for null draws)

---

## 11. BTC headline result

Weak M15 lag-1 AC1 (~0.0005); negative D1 AC1 (~-0.033); momentum proxy **never** positive after spread-only or all-in costs; gross H1 Sharpe ~0.09 only.

---

## 12. ETH headline result

Strongest exploratory AC1 at M15 (~0.0129) and H1 (~0.0087); gross M15 momentum Sharpe ~1.0 but **all-in Sharpe ~-78**; ETH drives short-horizon AC1 vs BTC.

---

## 13. Pooled headline result

Mean AC1 positive only when ETH M15/H1 pull the average; **no pooled cost-surviving persistence**.

---

## 14. Strongest horizon

**ETH_USD / M15** (AC1 and gross momentum proxy); still cost-defeated all-in.

---

## 15. Weakest horizon

**BTC_USD / D1** and **ETH_USD / D1** (negative AC1, negative gross Sharpe).

---

## 16. Regime sensitivity result

Mixed: BTC D1 low-vol AC1 positive (~0.078), high-vol negative; ETH M15 high-vol slightly positive AC1; no regime shows all-in momentum survival.

---

## 17. Spread-only cost result

**No survival** — spread-only momentum Sharpe negative at every asset/horizon (e.g. ETH M15 spread-only Sharpe ~-17).

---

## 18. All-in cost result

**No survival** — all-in edges ~-130 to -140 bps vs gross edges near zero (see cost report table).

---

## 19. 2× stress result

**No survival** — stress Sharpe more negative than all-in everywhere.

---

## 20. Gap-impact note

Exchange-side M1 gaps accepted by operator; ~99.94% coverage; diagnostics use stored bars only; gaps could bias short streak statistics slightly but are unlikely to create 120 bps tradable edge.

---

## 21. Synthesis classification

**`STATISTICAL_ONLY_COST_DEFEATED`**

---

## 22. Family C proceed to factor validation?

**No** — exploratory pass does not justify pre-registered factor validation; pivot to Family B.

---

## 23. Strategy created?

**No**

---

## 24. Campaign created?

**No**

---

## 25. Approved strategies empty?

**Yes** (`approved: []`)

---

## 26. Paper/demo/live blocked?

**Yes** (research freeze loops refuse)

---

## 27. Raw data committed?

**No** — JSON diagnostics only (compact aggregates)

---

## 28. Recommended next sprint

**Family B — Relative Value diagnostics** (`NEXT_PROMPT_CRYPTO_FAMILY_B_RELATIVE_VALUE_DIAGNOSTICS_001.md`)

---

## 29. Files to review first

1. `CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001_SYNTHESIS.md`
2. `CRYPTO_FAMILY_C_COST_TURNOVER_SENSITIVITY_RESULT.md`
3. `CRYPTO_FAMILY_C_NULL_BASELINE_RESULT.md`
4. `research/crypto/diagnostics/family_c_trend_persistence_001/full.json`
