# CAMPAIGN_018 — Test Lockbox Not Opened

**Date:** 2026-05-27  
**Branch:** `research-campaign-018-protective-stop-execution-001`

---

## Decision

The 2025–2026 test lockbox was **not opened**.

---

## Reason

Precommitted screening gates **failed**:

1. **train_expectancy_gte_zero** — observed **−0.119 R** (required ≥ 0)
2. **full_stress_15x_expectancy_gte_zero** — full-window 1.5× stress aggregate **negative**

Per [`CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md`](CAMPAIGN_018_EXIT_HYPOTHESIS_GATE_DESIGN.md), the test window opens only when **all** screening gates pass.

---

## What was not run

- No test split backtest (2025-01-01 → 2026-05-20)
- No test gate evaluation (T1–T4)

---

## Verdict impact

Campaign classified **REJECT** at screening stage. No further splits authorized under this precommit.

---

## No approval

Test lockbox discipline preserved. No strategy approved.
