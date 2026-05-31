# CAMPAIGN_020 — MTF Confluence Execution Sprint Summary

**Date:** 2026-05-27  
**Branch:** `research-campaign-020-mtf-confluence-execution-001`  
**Base:** `main` (merged scaffold @ `37d36c4`)  
**Verdict:** **REJECT**

## Workflow completed

1. Merged `research-mtf-confluence-candidate-020-scaffold-001` → `main` (fast-forward).
2. Created `research-campaign-020-mtf-confluence-execution-001` from clean `main`.
3. Reverted unrelated `financing_overlay_local_first` drift before execution.
4. Ran `python scripts/run_campaign_020_mtf_confluence.py train-validation` (~43 min).

## Key results (`next_bar_open`)

| metric | value |
|---|---|
| Train expectancy | **−0.035 R** (353 trades) |
| Validation expectancy | +0.053 R (204 trades) |
| Validation PF | 1.1313 |
| 2× stress validation exp | +0.049 R |
| Train gate | **FAIL** |
| Test lockbox | **not opened** |
| Approved | **no** |

## Gate discipline

Train failed → **STOP** — no test, no retune, no validation rescue despite positive validation metrics.

## Docs / artifacts

| artifact | path |
|---|---|
| Train/validation | `docs/research/CAMPAIGN_020_TRAIN_VALIDATION_RESULT.md` |
| Gates | `docs/research/CAMPAIGN_020_GATE_DECISION.md` |
| Interpretation | `docs/research/CAMPAIGN_020_FINAL_INTERPRETATION.md` |
| Lockbox | `docs/research/CAMPAIGN_020_TEST_LOCKBOX_NOT_OPENED.md` |
| Parity | `docs/research/CAMPAIGN_020_BACKTRADER_PARITY_RESULT.md` (NOT_RUN) |
| JSON | `research/campaign_020/` |
| Backtests | `backtests/CAMPAIGN_020_mtf_confluence_pullback/` |

## Remaining items

- Backtrader parity lane for C020 not implemented (blocks future parity-gated test).
- Financing overlay sensitivity blocked by same-timestamp entry/exit rows in some trades (document only).
