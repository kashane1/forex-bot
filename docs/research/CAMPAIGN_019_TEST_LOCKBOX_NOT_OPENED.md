# CAMPAIGN_019 — Test Lockbox Not Opened

**Date:** 2026-05-27  
**Branch:** `research-campaign-019-thesis-invalidation-execution-001`  
**Campaign:** CAMPAIGN_019 · `mean_reversion_thesis_invalidation 0.1.0-c019`

---

## Decision

The precommitted test lockbox (2025-01-01 → 2026-05-20) was **NOT opened**.

---

## Reason

Train/validation **screening gates failed** before Backtrader parity was evaluated for lockbox
eligibility. Per precommit gate design, test window opens only if **ALL** screening gates pass.

### Failed screening gates

1. **train_expectancy_gte_zero** — train exp_r = **−0.072 R** (required ≥ 0.0)
2. **train_expectancy_gte_c008_deduped** — C019 train **worse** than C008 deduped (−0.025 R)
3. **full_stress_15x_expectancy_gte_zero** — full stress exp_r = **−0.0139 R**

---

## Backtrader parity note

C019 Backtrader parity **passed** (train exact match; validation −1 trade; CLOSE_MATCH exits).
Parity pass does **not** override screening failure.

---

## Classification

**REJECT** — binding screening gates failed. No test metrics exist.

---

## No approval

No strategy approved. Paper/demo/live remain blocked.
