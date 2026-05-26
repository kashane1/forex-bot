# CAMPAIGN_016 Interpretation

**Date:** 2026-05-26 · **Verdict:** **REJECT**

## 1. Pass or reject?

**REJECT** — failed aggregate expectancy, profit factor, and fold pass rate gates on both base and 2× cost.

## 2. Beat deduped null?

**No.** Aggregate exp_r **−0.0633** vs null centre **−0.0029** (gap **−0.0604**).

## 3. Survive 2× cost?

**No.** 2× exp_r **−0.0719**, PF **0.92**.

## 4. Enough trades?

**Marginal.** **137** trades — above the 120 minimum but far below the ~400–700 weekly-cadence target in the discovery draft. Low turnover hypothesis held; sample still passed the precommit floor.

## 5. Performance concentrated?

Pair gross-positive-R dominance **39%** (passes ≤60%). Fold concentration **26%** — not the failure mode. Failure mode is **broad negative expectancy** in recent folds (5–7).

## 6. Backtrader confirm or block?

**BLOCKED** (non-decision-blocking) — cross-pair BT port deferred; weekly boundary parity PASS only.

## 7. Worth a follow-up?

**No new candidate without a fresh precommit.** Weekly cross-sectional momentum on this frozen spec does not clear the research screen. Folds 2–4 showed positive fold-level exp_r but LOO and median fold metrics fail anti-overfit gates; recent regime collapse in folds 5–7 dominates.

## 8. Does this approve anything?

**No.** `configs/approved_strategies.yaml` remains `approved: []`.
