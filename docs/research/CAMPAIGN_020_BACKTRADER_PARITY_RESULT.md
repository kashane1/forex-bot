# CAMPAIGN_020 — Backtrader Parity Result

**Date:** 2026-05-27  
**Status:** **NOT_RUN**

## Summary

No Backtrader lane adapter exists for `multi_timeframe_confluence_pullback` in `scripts/run_backtrader_exit_parity.py` (supported campaigns: C008, C009, C018, C019 only).

Precommitted gate **backtrader_parity_pass** was marked **false**. Screening failed on train before any test lockbox consideration.

## Impact

Parity failure is an independent blocker for test lockbox even if train/validation metrics had passed all economic gates.

## Follow-up

Implement `research/backtrader_lane/strategies/campaign_020_mtf_confluence_pullback.py` per `CAMPAIGN_020_BACKTRADER_PARITY_DESIGN.md` before any future campaign re-test that requires parity-gated test access.
