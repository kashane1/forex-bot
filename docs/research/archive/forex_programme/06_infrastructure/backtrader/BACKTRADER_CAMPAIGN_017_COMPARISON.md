# Backtrader CAMPAIGN_017 Comparison

**Date:** 2026-05-26 · **Classification:** **BLOCKED** (non-decision-blocking)

## Summary

Full Backtrader fold-window trade parity for `weekly_volatility_contraction_breakout 0.1.0-c017` is **not implemented** in this sprint. The bespoke walk-forward engine remains canonical.

| check | result |
|---|---|
| Weekly boundary parity (Monday UTC) | **PASS** |
| Compression flag parity (unit tests) | **PASS** |
| Fold-window trade parity | **BLOCKED** — deferred |
| Broker/OANDA imports | **PASS** — none |

## Rationale

Bespoke CAMPAIGN_017 already **REJECT** on primary gates (exp_r −0.0227, PF 0.77, 3/8 folds). Backtrader secondary lane is **non-decision-blocking** per precommit §9.

Adapter stub: `research/backtrader_lane/strategies/campaign_017_weekly_volatility_contraction_breakout.py`

JSON: `research/campaign_017/diagnostics/backtrader_comparison.json`

**No approval.**
