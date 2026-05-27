# CAMPAIGN_020 — Final Interpretation

**Date:** 2026-05-27  
**Strategy:** `multi_timeframe_confluence_pullback 0.1.0-c020`  
**Verdict:** **REJECT**  
**Fill timing:** `next_bar_open` (approval-bound)

## What we tested

A new MTF confluence pullback candidate: D1AGG trend alignment via `htf_align`, H4 trend context, pullback-to-EMA20, and reclaim trigger — structurally distinct from rejected mean-reversion, regime-switcher, and weekly families.

## What happened

Under conservative `next_bar_open` fills:

- **Train (2020–2022):** 353 trades, **−0.035 R** expectancy — fails the primary train gate.
- **Validation (2023–2024):** 204 trades, **+0.053 R**, PF 1.13, 5/6 pairs positive, passes 2× stress and beats the deduped C011 null margin.

Train failure dominates: this is the same failure mode seen across the C008-family (validation can look acceptable while train is negative). Per sprint rules we did **not** retune, rescue, or open the test lockbox.

## Conclusion

**Hypothesis not supported** on train under realistic fill timing. CAMPAIGN_020 is **REJECT** for promotion. No approval; paper/demo/live remain blocked.

## What did not change

- CAMPAIGN_019 remains **REJECT**
- `configs/approved_strategies.yaml` remains `approved: []`
- No broker or executor changes
