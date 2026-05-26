# Backtrader CAMPAIGN_016 Comparison

**Date:** 2026-05-26 · **Classification:** `BLOCKED` (non-decision-blocking)

## Summary

Full fold-window Backtrader trade parity for the seven-pair weekly
cross-sectional portfolio was **not executed** in this sprint. The
cross-pair rebalance state machine remains bespoke-canonical.

Partial verification **PASS**:

- Frozen parameters match between bespoke runner and BT adapter stub
- Weekly Monday UTC boundary logic shared via `forex_bot.features.weekly_momentum`
- Unit tests: `tests/unit/backtrader_lane/test_campaign_016_weekly_cross_sectional_momentum.py`

## Decision impact

**Non-blocking.** Bespoke walk-forward produced **REJECT**; Backtrader
gap does not change the sprint verdict.

## Artifacts

- `research/campaign_016/diagnostics/backtrader_comparison.json`
- `research/backtrader_lane/strategies/campaign_016_weekly_cross_sectional_momentum.py`

**No strategy approved.**
