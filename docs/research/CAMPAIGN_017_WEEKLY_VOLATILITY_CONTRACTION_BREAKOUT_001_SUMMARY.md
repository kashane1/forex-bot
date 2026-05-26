# CAMPAIGN_017 Sprint Summary

**Date:** 2026-05-26 · **Branch:** `research-weekly-volatility-contraction-breakout-001`

## Strategy

`weekly_volatility_contraction_breakout 0.1.0-c017` — synthetic weekly compression from deduped H4, breakout from compressed week range with ATR buffer, opposite-range stop, 42-bar max hold.

## Frozen settings (unchanged post-precommit)

- 12-week compression lookback, P25 threshold
- 0.25 × ATR(14) breakout buffer
- Monday 00:00 UTC week boundary
- 7-pair H4 universe, deduped `CandleRepo.list`
- max 2 portfolio positions, 1 per pair

## Bespoke verdict

**REJECT**

| metric | base | 2× |
|---|---:|---:|
| exp_r | −0.0227 | −0.0283 |
| PF | 0.77 | 0.72 |
| trades | 230 | 230 |
| folds pass | 3/8 | 3/8 |
| pairs positive | 4/7 | — |

## Null / anti-overfit

**WITHIN_NULL** — gap −0.0198 R vs deduped null centre; aggregate floor not met.

## Backtrader

**BLOCKED** (non-decision-blocking) — fold parity deferred; boundary/compression unit parity PASS.

## Approval

**No.** `configs/approved_strategies.yaml` remains `approved: []`. Paper / demo / live blocked.

## Recommended next step

Continue deduped candidate discovery (post-CAMPAIGN_017 selection sprint) — do **not** retune C017 parameters. No strategy approval path from this sprint.

## Files to review first

1. `docs/research/CAMPAIGN_017_WEEKLY_VOLATILITY_CONTRACTION_BREAKOUT_PRECOMMIT.md`
2. `docs/research/CAMPAIGN_017_WEEKLY_VOLATILITY_CONTRACTION_BREAKOUT_RESULT.md`
3. `backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/walk_forward/gate_result.json`
4. `docs/research/CAMPAIGN_017_NULL_AND_ANTI_OVERFIT.md`
5. `docs/research/CAMPAIGN_017_WEEKLY_VOLATILITY_CONTRACTION_BREAKOUT_INTERPRETATION.md`

## Commits by phase

| phase | commit | summary |
|---|---|---|
| 0 | `35c3d7e` | binding precommit |
| 1 | `f72b27d` | weekly volatility features |
| 2 | `ff2c422` | strategy module + config |
| 3 | `c3b31bc` | runner + diagnostics scaffold |
| 4–7 | (this commit) | walk-forward result + evidence docs |
