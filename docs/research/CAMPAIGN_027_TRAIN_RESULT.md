# CAMPAIGN_027_TRAIN_RESULT

**Status:** TRAIN/VALIDATION EXECUTION — Phase 4 / **REJECT_TRAIN_GATE** /
TEST_LOCKBOX_CLOSED / NOT_APPROVED. Branch
`research-campaign-027-h4-filtered-zscore-reversion-train-validation-001`.

Train evidence for the single frozen candidate (`c027_frozen_001`), computed on
the campaign's own ledgers with the **conservative (binding) cost** model. **No
tuning.** The frozen rule failed binding train gates → REJECT; validation was
**not run** (Phase 5).

> Frozen rule: [precommit scope](CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md).
> Gates: [plan](CAMPAIGN_027_TRAIN_VALIDATION_001_PLAN.md). Split:
> [coverage/split](CAMPAIGN_027_DATA_COVERAGE_AND_SPLIT_DECISION.md).

---

## Command run

```
PYTHONPATH=$PWD/src python scripts/run_campaign_027_h4_filtered_zscore_reversion.py \
    --train-validation
# defaults: train 2020-01-01..2022-12-31, validation 2023-01-01..2024-12-31,
#           --matched-null-seeds 50, --no-test-lockbox, --fail-if-test-window
```

Artifacts: `research/campaign_027/train_validation/` (run_manifest, candidate
registry, signal/trade/funnel/filter-stage ledgers, train metrics, gate result,
pair/year/side metrics, cost stress, matched-null, filter-ablation, recency report,
compliance, warnings).

## Train window

`2020-01-01 → 2022-12-31` (signals assigned by decision-bar timestamp; entry + full
12-bar exit self-contained in-window). 7 majors. Leading ≈264-bar warmup is drawn
from inside 2020 (no pre-2020 history). `dropped_trailing_signals = 0`.

## Train metrics (conservative cost binding)

| metric | value |
|---|---|
| trades (short-only entered) | **180** |
| expectancy (conservative, return fraction/trade) | **+0.00011974** |
| expectancy (optimistic) | +0.00023494 |
| profit factor (conservative) | **1.0433** |
| hit rate (conservative) | 0.500 |
| pairs non-negative | **4/7** |
| years non-negative | **1/3** (only 2022) |
| avg bars held | 10.38 |
| avg spread paid (pips) | 1.665 |
| exit reasons | time_stop 137 · protective_atr_stop 43 |
| **2× cost stress expectancy** | **−0.00007745** (PF 0.973) |

Funnel: 5,617 base-trigger (`|z|≥2.0`, both sides) signals → 180 short entries
after `|z|≥2.5 & low-vol & quiet-session & self-contained-completion`.

## Train gate table (pre-registered; binding on conservative cost)

| gate | result | detail |
|---|---|---|
| expectancy_conservative > 0 | ✅ PASS | +0.00011974 (wafer-thin) |
| profit_factor ≥ 1.05 | ❌ **FAIL** | 1.0433 |
| trades ≥ 100 | ✅ PASS | 180 |
| ≥ 4/7 pairs non-negative | ✅ PASS | 4/7 |
| ≥ 2/3 years non-negative | ❌ **FAIL** | 1/3 (2020 −, 2021 −, 2022 +) |
| 2× cost stress ≥ 0 | ❌ **FAIL** | −0.00007745 |
| matched-null above random | ✅ PASS | session/full ABOVE (pctl 90) |
| filter-ablation: retained filters add edge | ❌ **FAIL** | strong-extension only reduces sample |

**4 of 8 binding train gates fail → `REJECT_TRAIN_GATE`.**

## Pair-level results (conservative expectancy/trade)

```
AUD_USD +0.00223   EUR_USD +0.00056   USD_CAD +0.00044   NZD_USD +0.00045
GBP_USD −0.00197   USD_CHF −0.00082   USD_JPY −0.00052
```

4/7 positive, but the edge is concentrated in AUD_USD; GBP_USD/USD_CHF/USD_JPY are
clearly negative. (USD_JPY — the front gate's cost-advantaged member — is *negative*
on the realized execution, consistent with the precommit's "USD_JPY is not a
standalone thesis / LIKELY_SELECTION_NOISE" caution.)

## Year-level results (conservative expectancy/trade)

```
2020 −0.00057    2021 −0.00029    2022 +0.00119
```

Only 2022 is positive. The two earliest train years are negative; the apparent
train edge is a single-year (2022) artifact — the same single-year-dominance the
front gate claimed the filters had cured (Phase-4 reconciliation), here **not**
reproduced on the campaign's own realized ledger.

## Filter-stage diagnostics (ablation on the campaign's own train funnel)

Value = fixed-horizon h12 close-to-close log return (front-gate-comparable).
Trigger-only expectancy −0.00004947; all-filters n=113.

| filter | marginal gain | flag |
|---|---|---|
| f_low_vol | **+0.000572** | FILTER_ADDS_EDGE ✅ |
| f_quiet_session | **+0.000339** | FILTER_ADDS_EDGE ✅ |
| f_strong_extension | +0.000034 | **FILTER_ONLY_REDUCES_SAMPLE** ❌ |
| f_cost_adv_pair (dropped) | −0.000150 | FILTER_ONLY_REDUCES_SAMPLE (correctly dropped) |
| f_long_side (dropped) | −0.000372 | FILTER_HURTS_EDGE (correctly dropped → short-only) |

Two of the three retained filters still add edge, but **`f_strong_extension`
(|z|≥2.5) does not re-derive `FILTER_ADDS_EDGE` on the campaign's own train data**
(+0.000034, below the noise tolerance) — the front gate measured +0.000208. This
is the pre-registered **filter forking-path risk** materializing, and it fails the
filter-ablation train gate.

## Signal funnel diagnostics

5,617 base triggers (both sides) → strong-extension, low-vol and quiet-session
filters + short-only + completion reduce to 180 entered trades. Long signals are
logged diagnostic-only (`entered=false`) and never sized.

## Cost-stress result

2× conservative cost (spread + slip doubled) turns expectancy **negative**
(−0.00007745, PF 0.973): the wafer-thin train edge does not survive a 2× cost
assumption — kill condition #7.

## Matched-null result

Post conservative cost, seeds 0–49, window 12 bars:

| mode | strategy | null mean | percentile | flag |
|---|---|---|---|---|
| timestamp_random_same_pair | +0.000392 | −0.000483 | 90 | ABOVE_MATCHED_NULL |
| session_matched_random | +0.000392 | −0.000526 | 90 | ABOVE_MATCHED_NULL |
| full_matched_null | +0.000329 | −0.000286 | 90 | ABOVE_MATCHED_NULL |
| side_shuffled | — | — | — | WITHIN (degenerate: short-only ledger) |

The timing/direction **information** is real (strategy above the structure-matched
null on all three informative modes, ~90th percentile). But — exactly as the
precommit warned — "beats/above the matched null" measures *loses less than
random*, **not** *makes money*: the realized post-cost expectancy still fails the
profit, year-robustness, and cost-stress gates. Information ≠ a tradable edge.

## Whether train permits validation

**No.** Binding train gates failed (PF, year-robustness, 2× cost stress, filter
ablation). Per the Phase-5 rule, **validation is NOT run** (it is confirmation, not
a rescue). See `CAMPAIGN_027_VALIDATION_NOT_RUN.md`.

## Explicit no-approval statement

No strategy is approved. `configs/approved_strategies.yaml` stays `approved: []`.
`not_approved: true`, `promotion_eligible: false`, `paper_demo_live_enabled:
false`. The test lockbox (2025-01-01 → 2026-05-20) was not opened. No
broker/executor/OANDA endpoint was touched.
</content>
