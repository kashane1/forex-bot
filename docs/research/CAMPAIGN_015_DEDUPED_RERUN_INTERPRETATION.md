# CAMPAIGN_015 Deduped Rerun Interpretation

**Branch:** `infra-canonical-candle-dedup-and-campaign015-rerun-001`
**Date:** 2026-05-26

> **No strategy approved.** Paper / demo / live remain blocked.

## 1. What changed after dedupe?

Duplicate UTC-normalised H4 bars (~46% of loaded rows across pair/folds)
were dropped at the canonical `CandleRepo.list` boundary. Trade count
rose from 164 → 375 because dedupe restored signals that duplicate bars
had suppressed — but aggregate expectancy flipped from +0.23R to -0.01R.
The prior positive edge was **evidence-contaminated**, not real.

## 2. Did CAMPAIGN_015 remain promising?

**No.** Deduped base exp_r is -0.0101; 2x-cost exp_r is -0.0283.
Trade-level cumulative R is -3.79. The candidate does not show a
durable positive edge on clean data.

## 3. Did it pass or fail gates?

**REJECT.** Aggregate gates fail on expectancy_r, fold_pass_rate, and
pairs_positive. Two folds pass per-fold gates (up from zero), but that
does not meet the 5/8 aggregate threshold.

## 4. Did trade count rise above 200?

**Yes** — 375 trades (gate now passes; previously failed at 164).

## 5. Did fold pass count improve?

**Yes, marginally** — 2/8 folds pass (was 0/8 on contaminated data).

## 6. Did matched null remain favorable?

**No.** Anti-overfit label is **`WITHIN_NULL`**, not above null.
Prior `ROBUST_ABOVE_NULL` is invalidated.

## 7. Did Backtrader parity improve?

**Yes.** Classification moved from `DATA_MISMATCH` / `TIMESTAMP_MISMATCH`
to **`TOLERABLE_DRIFT`**. Fold 1 × AUD_USD: 13 bespoke vs 10 BT (was
2 vs 13). Residual drift remains but is no longer dominated by
duplicate-candle corruption.

## 8. Does this alter approval status?

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

## 9. Recommended next step

**Stop CAMPAIGN_015** as a promotion candidate. The deduped evidence
invalidates the prior promising diagnostics. Optional follow-ups (not
this sprint):

- Debug remaining BT bespoke drift (≈23% trade-count gap) if a future
  candidate needs secondary-lane corroboration.
- Design one **new pre-committed candidate** from deduped evidence base —
  do not retune CAMPAIGN_015 frozen parameters.

## Approval reminder

Even a clean `PASS_RESEARCH_SCREEN` would be "candidate for human
review" only. The deduped result is `REJECT`.
