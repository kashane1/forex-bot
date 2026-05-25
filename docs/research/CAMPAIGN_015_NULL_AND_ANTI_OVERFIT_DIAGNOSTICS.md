# CAMPAIGN_015 Null Comparison + Anti-Overfit Diagnostics

**Date:** 2026-05-25 · **Branch:** `research-failed-breakout-reversal-campaign-015`
**Classifier label:** `BLOCKED`

> **No strategy approved.** `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live loops remain blocked.
> CAMPAIGN_011 (the null baseline) is **not** modified by this
> document; the comparator is read-only.

## 1. Outcome

The Phase 4 diagnostic classifier is **`BLOCKED`** by direct inheritance
from Phase 3
([`CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_RESULT.md`](CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_RESULT.md)
§1). The bespoke walk-forward engine did not execute, so there are
no per-fold expectancy values, no aggregate metrics, no per-pair
gross R, no per-trade R series, and no campaign artifacts against
which to compare CAMPAIGN_011.

The classifier emits `BLOCKED` programmatically when given the
`DiagnosticInputs(blocked=True, blocked_reasons=[...])` it would
receive from the upstream Phase 3 `gate_result.json`. See
[`research/anti_overfit/campaign_015.py`](../../research/anti_overfit/campaign_015.py).

## 2. What this means

`BLOCKED` is **not** a verdict on the failed-breakout-reversal
hypothesis. It is the absence of inputs to the diagnostic. A future
sprint that runs CAMPAIGN_015 against the canonical local data store
can call the classifier with concrete `DiagnosticInputs` and the
label will land in the actual decision domain:

| label | meaning |
|---|---|
| `ROBUST_ABOVE_NULL` | aggregate floor + every anti-overfit gate pass, no single cell dominates |
| `ABOVE_NULL_BUT_FRAGILE` | aggregate floor passes but at least one anti-overfit gate fails |
| `SELECTED_CELL_ARTIFACT` | one pair or one fold drives > threshold of gross positive R |
| `WITHIN_NULL` | campaign aggregate metrics sit inside the CAMPAIGN_011 null band |
| `WORSE_THAN_NULL` | campaign aggregate metrics materially worse than the matched null |
| `BLOCKED` | inputs missing / Phase 3 BLOCKED / fewer than 3 folds with data |

(See Phase 0 §11 for the binding label set.)

## 3. The classifier (pure function; testable; no broker, no LEAN)

The classifier is implemented as a single pure function:

```python
from research.anti_overfit import DiagnosticInputs, classify_campaign_015

inputs = DiagnosticInputs(
    blocked=False,
    campaign_expectancy_r=...,
    campaign_return_pct=...,
    campaign_profit_factor=...,
    campaign_pairs_positive=...,
    campaign_total_trades=...,
    campaign_per_fold_expectancy_r=[...],
    campaign_pair_gross_positive_r={...},
    campaign_fold_gross_positive_r=[...],
    campaign_trade_r_series=[...],
    campaign_total_cost_r=...,
    null_expectancy_r=...,
    null_return_pct=...,
    null_profit_factor=...,
    null_pairs_positive=...,
    null_per_fold_expectancy_r=[...],
)
out = classify_campaign_015(inputs)
# {"label": "...", "anti_overfit_gates": {...}, "metrics": {...}, "reasons": [...]}
```

The classifier imports nothing from `forex_bot.broker`, `oandapyV20`,
LEAN, or QuantConnect (verified by `tests/unit/test_anti_overfit_campaign_015.py::test_classifier_never_imports_broker_or_lean`).

## 4. Anti-overfit gates pinned by the classifier (Phase 0 §9)

| gate | binding threshold |
|---|---|
| LOO min mean gap vs matched null in R | `>= +0.05` |
| t-stat of per-fold gap | `>= 2.0` |
| median per-fold expectancy R | `>= 0.0` |
| trade-level cumulative R | `> 0.0` |
| pair concentration (max share of gross positive R) | `<= 70%` |
| fold concentration (max share of gross positive R) | `<= 60%` |
| cost dominance (`total_estimated_costs_r / abs_total_r`) | `<= 0.50` |

A future re-run with concrete data computes each of these from the
per-fold + per-pair + per-trade artifacts written by
`scripts/run_campaign_015.py`.

## 5. Test coverage

`tests/unit/test_anti_overfit_campaign_015.py` pins the classifier on
10 synthetic fixtures:

1. label set is the verbatim Phase 0 §11 list
2. `blocked=True` short-circuits to `BLOCKED`
3. fewer than 3 folds short-circuits to `BLOCKED`
4. all gates + diversified cells → `ROBUST_ABOVE_NULL`
5. erratic per-fold expectancy (low t-stat) → `ABOVE_NULL_BUT_FRAGILE`
6. one pair = 80% of gross positive R → `SELECTED_CELL_ARTIFACT`
7. metrics inside null band on every axis → `WITHIN_NULL`
8. every axis materially worse than null → `WORSE_THAN_NULL`
9. zero-variance per-fold gap series → label still in the binding set
10. classifier module never imports broker / OANDA SDK / LEAN

These tests do **not** exercise real campaign data; they pin the
binding label logic so a future re-run classifies cleanly without
silent drift.

## 6. Null comparison: read-only ingest of CAMPAIGN_011

CAMPAIGN_011 (`random_entry_anchor 0.1.0-c011`) is the matched null
baseline. The classifier consumes (when given inputs):

* `null_expectancy_r` — CAMPAIGN_011 aggregate expectancy in R
* `null_return_pct` — CAMPAIGN_011 aggregate return %
* `null_profit_factor` — CAMPAIGN_011 aggregate PF
* `null_pairs_positive` — CAMPAIGN_011 pairs-positive count
* `null_per_fold_expectancy_r` — CAMPAIGN_011 per-fold expectancy
  series, **sample-matched** to the CAMPAIGN_015 folds

The matched null is pre-existing committed evidence in
`backtests/CAMPAIGN_011_random_entry_anchor/` and is **not** mutated
by this document. The Phase 4 doc only reads.

Because Phase 3 is `BLOCKED`, no read of CAMPAIGN_011 fold artifacts
happens in this sprint; the comparison cells in the classifier
output are empty.

## 7. Anti-overfit posture verification (binding)

| invariant | state |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (byte-stable) |
| `failed_breakout_reversal` in the registry | **No** |
| CAMPAIGN_011 evidence mutated | **No** (read-only contract) |
| Anti-overfit gate thresholds in this doc | verbatim Phase 0 §9 |
| Classifier labels in this doc | verbatim Phase 0 §11 |
| Classifier imports broker / OANDA / LEAN | **None** |
| Phase 3 result mutated | **No** |
| Diagnostic doc fabricates results | **No** (BLOCKED, no numeric inputs) |

## 8. Files produced by Phase 4

| file | role |
|---|---|
| `research/anti_overfit/__init__.py` | module init + public surface |
| `research/anti_overfit/campaign_015.py` | pure-function classifier |
| `tests/unit/test_anti_overfit_campaign_015.py` | 10 classifier tests pinning the binding labels |
| `docs/research/CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_DIAGNOSTICS.md` | this document |

## 9. Disposition

* Phase 4 verdict: `BLOCKED` (inherited from Phase 3).
* No promotion path. No registry edit. No loop config edit.
* The classifier is committed and ready: a future sprint that
  obtains the canonical OANDA-practice H4 store may construct
  `DiagnosticInputs` from the bespoke runner output and the
  CAMPAIGN_011 fold artifacts, then call `classify_campaign_015(...)`
  to obtain the binding label.
