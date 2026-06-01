# Crypto Family B Relative Value Diagnostics 001 — Plan

**Sprint:** `crypto-family-b-relative-value-diagnostics-001`
**Date:** 2026-06-01
**Branch:** `main`
**Type:** Exploratory diagnostics only

---

## 1. Purpose

Test whether BTC/ETH relative value (lead-lag, relative momentum, beta-adjusted spread reversion) produces a **larger, more robust, and more cost-resilient** effect than Family C raw trend persistence, under frozen Coinbase spot costs.

---

## 2. Non-goals

No strategy, campaign, front-gate, production factors, approval, paper/demo/live, ingestion API calls, cost tuning, or M1 gap interpolation.

---

## 3. Family C handoff

| Item | Value |
|------|-------|
| Classification | `STATISTICAL_ONLY_COST_DEFEATED` |
| Strongest raw signal | ETH M15 AC1 / gross momentum Sharpe ~1.0 |
| Cost survival | None at spread-only, all-in, or 2× |
| Recommendation | Pivot to Family B (this sprint) |

---

## 4. Data window and instruments

| Field | Value |
|-------|-------|
| Instruments | `BTC_USD`, `ETH_USD` only |
| Window | `2021-05-31T00:00:00Z` → `2026-05-31T23:57:53Z` |
| Source | `m1_materialized` in Postgres |
| Alignment | Timestamp **intersection** only — no forward-fill |

---

## 5. Timeframes

M15, H1, H4 (`H4M1`), D1

---

## 6. Relative-value hypotheses (pre-declared)

1. BTC leads ETH (or reverse) at short lags.
2. Relative momentum: prior BTC−ETH (or beta-adj) outperformance persists.
3. Large spread z-scores mean-revert (divergence/reversion).
4. Effects may concentrate in high-vol or high-correlation regimes.

**Lookbacks (not tuned post-hoc):**

| TF | Relative momentum lookbacks |
|----|----------------------------|
| M15 | 4, 16, 48 |
| H1 | 4, 24, 72 |
| H4 | 3, 6, 18 |
| D1 | 3, 7, 21 |

**Z-score bands:** |z| ≥ 1, 1.5, 2

---

## 7. Cost assumptions

Frozen `CRYPTO_COST_MODEL_001.md`. Report per diagnostic:

- Gross
- Spread-only (one-leg and **paired** BTC+ETH)
- All-in (one-leg and paired)
- 2× paired stress

Paired conservative proxy: round-trip cost on **both** legs when diagnostic implies two-sided exposure.

---

## 8. Null baseline plan

- Seed **42**
- Shuffle, sign-flip, block-bootstrap (Family C lesson: subsample ≤8000 returns; trials 100–500 by TF)
- Document subsample size and trial counts in artifacts

---

## 9. Computational limits

- Intersect aligned bars only (drops gap-misaligned timestamps)
- Subsample for null draws on M15/H1
- No full-universe permutation on 175k+ rows without subsampling

---

## 10. Safety rules

- `configs/approved_strategies.yaml` stays empty
- Research freeze / archive gates after each phase
- No raw candles or secrets in commits
- Ruff: document ~40 pre-existing issues; non-blocking

---

## 11. Expected outputs

| Phase | Deliverable |
|-------|-------------|
| 0 | This plan |
| 1 | `relative_value.py`, loader alignment, run script, tests |
| 2 | `CRYPTO_FAMILY_B_LEAD_LAG_RELATIONSHIP_RESULT.md` |
| 3 | `CRYPTO_FAMILY_B_RELATIVE_MOMENTUM_RESULT.md` |
| 4 | `CRYPTO_FAMILY_B_DIVERGENCE_REVERSION_RESULT.md` |
| 5 | `CRYPTO_FAMILY_B_REGIME_SENSITIVITY_RESULT.md` |
| 6 | `CRYPTO_FAMILY_B_COST_AND_FX_S4_COMPARISON_RESULT.md` |
| 7 | `CRYPTO_FAMILY_B_RELATIVE_VALUE_DIAGNOSTICS_001_SYNTHESIS.md` |
| 8 | Next prompt by classification |
| 9 | Programme README / roadmap |
| 10 | `CRYPTO_FAMILY_B_RELATIVE_VALUE_DIAGNOSTICS_001_SUMMARY.md` |

Artifacts: `research/crypto/diagnostics/family_b_relative_value_001/`

---

## 12. Phase 0 baseline (2026-06-01)

| Check | Result |
|-------|--------|
| Branch `main` | PASS |
| Working tree clean | PASS |
| Family C classification | `STATISTICAL_ONLY_COST_DEFEATED` |
| `approved_strategies.yaml` | empty |
| pytest | 2483 passed |
| research freeze | PASS |
| archive validation | PASS |
| secret scan | PASS |
| ruff | 40 pre-existing issues |
