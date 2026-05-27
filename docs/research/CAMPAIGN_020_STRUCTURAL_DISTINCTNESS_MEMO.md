# CAMPAIGN_020 — Structural Distinctness Memo

**Date:** 2026-05-27  
**Campaign:** CAMPAIGN_020 · `multi_timeframe_confluence_pullback 0.1.0-c020`  
**Conclusion:** **STRUCTURALLY DISTINCT** — proceed with scaffold (not blocked)

## Why this is not an exit-only C008 / C018 / C019 variant

| dimension | C008/C018/C019 mean-reversion family | CAMPAIGN_020 |
|---|---|---|
| entry thesis | fade z-score extension in **low ADX** range | **with-trend** pullback continuation after HTF agreement |
| direction | counter-trend reversion | pro-trend (long in bullish stack, short in bearish) |
| HTF | regime EMA on H4 only | **D1AGG** trend via `htf_align` + H4 context |
| exit family | midline / protective stop / thesis invalidation | hard ATR stop + time stop only (no z-exit) |
| fill timing (committed) | C019 used `signal_bar_close` | **`next_bar_open`** approval-bound |

C019 proved that C008-identical entries fail even with new exits; C020 changes **entry selection**, not exit engineering.

## Why this is not a C012 regime_switcher retune

C012 fires only in **HIGH-VOL D1AGG ATR percentile** regimes with a short H4 close-move momentum sub-signal. C020 uses **D1 EMA trend structure** (close vs EMA50, EMA20 vs EMA50) and requires an explicit **H4 pullback + EMA20 re-acceptance**. No ATR-percentile regime gate, no 4-bar momentum-only entry.

## Why this is not a C013 currency-strength retune

C013 ranks eight synthetic currency strengths across pairs and trades rank gaps. C020 is **single-pair**, price-structure confluence on D1AGG + H4 — no cross-pair ranking.

## Why this is not a C014 calendar retune

C014 is event-window anomaly detection on a committed calendar fixture. C020 has **no event calendar** dependency.

## Why this is not C015 failed-breakout reversal

C015 trades false breaks of range boundaries. C020 requires aligned trends and pullback-to-EMA re-acceptance — not fade of a failed breakout.

## Why this is not a weekly C016 / C017 retune

C016/C017 operate on **completed weekly** bars with cross-sectional or volatility-contraction logic. C020 executes on **H4** with **D1AGG** HTF only — different timeframe stack and hypothesis.

## Relation to CAMPAIGN_007 pullback_continuation

C007 is H4-only EMA pullback without D1AGG gating. C020 adds **mandatory D1AGG trend filter** via shared alignment, optional ADX floor, and stricter pullback-to-EMA20 trigger — reducing the high-turnover weak H4-only pattern that failed in prior broad search.

## New hypothesis under test

**Multi-timeframe confluence reduces false H4 entries:** when D1AGG structure, H4 trend, and local pullback re-acceptance agree, expectancy after realistic `next_bar_open` fills may beat the deduped null and avoid the mean-reversion failure mode.

## Why test despite prior failures

Infrastructure now enforces `next_bar_open`, HTF alignment, signal provenance, and financing overlay hooks. Prior rejections mixed optimistic fill timing and single-timeframe entries; C020 is the first **precommitted** candidate designed under the new policy from day one.

## Falsification criteria (future execution)

- Train expectancy < 0 under `next_bar_open`
- Validation fails precommitted gates (PF, trade count, pair breadth, 2× cost)
- Does not beat deduped C011 null by +0.010R margin
- Backtrader parity fails before any test lockbox

## No strategy approved

`configs/approved_strategies.yaml` remains `approved: []`. CAMPAIGN_020 scaffold does not change any prior verdict.
