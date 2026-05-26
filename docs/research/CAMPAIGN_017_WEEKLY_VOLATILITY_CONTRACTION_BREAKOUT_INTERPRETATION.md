# CAMPAIGN_017 Interpretation

**Date:** 2026-05-26 · **Verdict:** **REJECT**

## 1. Pass or reject?

**REJECT** — failed aggregate expectancy, profit factor, and fold pass rate gates on both base and 2× cost.

## 2. Beat deduped null?

**No.** Aggregate exp_r **−0.0227** vs null centre **−0.0029** (gap **−0.0198**). Did not exceed null by +0.03 R.

## 3. Survive 2× cost?

**No.** 2× exp_r **−0.0283**, PF **0.72**.

## 4. Enough trades?

**Yes.** **230** trades — within the 120–350 precommit band. Low-turnover weekly cadence hypothesis held on sample size.

## 5. Performance concentrated?

Pair gross-positive-R dominance **38.4%** (passes ≤60%). Fold concentration **21.3%** — not the failure mode. Failure mode is **negative aggregate expectancy** with fold 7 collapse (−0.353 exp_r).

## 6. Backtrader confirm or block?

**BLOCKED** (non-decision-blocking) — full BT fold runner deferred; weekly boundary and compression parity PASS in unit tests only.

## 7. Worth a follow-up?

**No new candidate without a fresh precommit.** Weekly volatility contraction breakout on this frozen spec does not clear the research screen. Folds 0, 5–6 showed positive fold-level exp_r but LOO and median fold metrics fail anti-overfit gates; fold 7 dominates the negative aggregate.

## 8. Does this approve anything?

**No.** `configs/approved_strategies.yaml` remains `approved: []`.
