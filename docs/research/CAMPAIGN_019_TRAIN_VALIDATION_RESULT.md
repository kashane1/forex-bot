# CAMPAIGN_019 — Train / Validation Result

**Date:** 2026-05-27  
**Branch:** `research-campaign-019-thesis-invalidation-execution-001`  
**Campaign:** CAMPAIGN_019 · `mean_reversion_thesis_invalidation 0.1.0-c019`  
**Hypothesis:** `thesis_invalidation_zscore_continuation_exit`  
**Status:** `strategy_evidence: true` · `not_approved: true` · `paper_demo_live_enabled: false`

---

## Command run

```bash
python scripts/run_campaign_019_thesis_invalidation.py train-validation
```

Elapsed: **298.6 s** · Git commit at run: `a9ebce4`

---

## Data path and splits

| Item | Value |
|---|---|
| Database | `data/campaign_002.sqlite3` |
| Dedupe policy | `keep_last` (deduped candles mandatory) |
| Train | 2020-01-01 → 2022-12-31 |
| Validation | 2023-01-01 → 2024-12-31 |
| Pairs | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF (H4) |
| Base cost | spread×0.5, slippage 0.2 pips |
| Stress 2× | validation only, spread×2.0, slippage 0.5 pips |
| Stress 15× | full window, spread×1.5, slippage 0.3 pips |

---

## Train metrics

| Metric | Value |
|---|---|
| Trade count | 219 |
| Expectancy (R) | **−0.072** |
| Profit factor | 0.927 |
| Pairs positive | 3 / 6 |

---

## Validation metrics

| Metric | Value |
|---|---|
| Trade count | 138 |
| Expectancy (R) | **+0.0962** |
| Profit factor | 1.1423 |
| Pairs positive | 6 / 6 |

---

## Gate table (screening)

| Gate | Threshold | Result | Pass |
|---|---|---|---|
| G1 train expectancy | ≥ 0.0 R | −0.072 R | **FAIL** |
| G2 validation expectancy | > 0.0 R | +0.0962 R | PASS |
| G3 validation PF | ≥ 1.05 | 1.1423 | PASS |
| G4 validation pairs positive | ≥ 2 | 6 | PASS |
| G5 validation trade count | ≥ 30 | 138 | PASS |
| G6 validation stress 2× exp | ≥ 0.0 R | +0.0499 R | PASS |
| G7 beat C011 null | > −0.0029 + 0.010 R | +0.0962 > +0.0071 | PASS |
| G8 thesis_invalidation rate | 5–45% | 12.6% (runner aggregate) | PASS |
| G9 zero target exits | 0 | 0 | PASS |
| G10 zero protective exits | 0 | 0 | PASS |
| G11 train vs C008 deduped | ≥ −0.025 R | −0.072 < −0.025 | **FAIL** |
| G12 full stress_15x exp | ≥ 0.0 R | −0.0139 R | **FAIL** |

**Screening pass:** **false** · **Verdict:** **REJECT**

Failed gates: `train_expectancy_gte_zero`, `train_expectancy_gte_c008_deduped`, `full_stress_15x_expectancy_gte_zero`

---

## Cost stress (validation 2×)

| Metric | Value |
|---|---|
| Trade count | 138 |
| Expectancy (R) | +0.0499 |
| Profit factor | 1.0633 |
| Pairs positive | 4 / 6 |

---

## Mechanism diagnostics

From `research/campaign_019/mechanism_diagnostics.json` (runner concatenates all cost-regime runs):

| Diagnostic | Value |
|---|---|
| Thesis invalidation exits | 122 (12.6%) |
| Hard stop exits | 551 |
| Time exits | 294 |
| Target exits | 0 |
| Protective exits | 0 |
| Time-exit median R | 1.3615 |
| Thesis invalidation z-score median | 3.0557 (n=122) |

Train-only exit shares (bespoke): stop 60.7%, thesis_invalidation 12.3%, time 26.5%.

---

## Comparison to baselines

| Baseline | Train exp (R) | Val exp (R) | Notes |
|---|---|---|---|
| **C019** | −0.072 | +0.0962 | this run |
| C008 deduped | −0.025 | +0.1612 | C019 train **worse** than C008 |
| C009 deduped | −0.0253 | +0.1859 | target share 0% (C019 ok) |
| C018 executed | −0.1188 | +0.194 | protective share 0% (C019 ok); C019 train **better** than C018 |
| C011 deduped null | — | −0.0029 | C019 beats null by +0.0991 R margin |

---

## Backtrader parity before lockbox

Parity is **required** before test lockbox per precommit. Screening **failed** first, so lockbox
remains closed regardless. Parity was run in Phase 4 (see
[`CAMPAIGN_019_BACKTRADER_PARITY_RESULT.md`](CAMPAIGN_019_BACKTRADER_PARITY_RESULT.md)).

---

## Test lockbox

**NOT allowed to open** — screening gates failed (train expectancy negative).

---

## No approval

No strategy was approved. `configs/approved_strategies.yaml` remains `approved: []`.
Paper/demo/live remain blocked.
