# CAMPAIGN_021 — Structural Distinctness Memo

**Date:** 2026-05-27  
**Campaign:** CAMPAIGN_021 · `lower_timeframe_mtf_confluence_entry 0.1.0-c021`  
**Conclusion:** **STRUCTURALLY DISTINCT** — proceed with scaffold (not blocked)

## How C021 differs from CAMPAIGN_020 (rejected H4 MTF confluence)

| dimension | CAMPAIGN_020 (`multi_timeframe_confluence_pullback`) | CAMPAIGN_021 |
|---|---|---|
| execution timeframe | **H4** completed bars | **M15** completed bars |
| entry trigger | H4 pullback to EMA20/RSI + H4 reclaim | **M15** pullback to EMA20/50 + M15 EMA20 reclaim |
| tactical context | none (H4 is both context and execution) | **H1** EMA20 + slope over 3 bars |
| intermediate context | H4 trend only | **H4** EMA50 trend (separate from execution) |
| structural HTF | D1AGG via `htf_align` | D1AGG via `htf_align` (same policy, different join target) |
| data lane | H4-native research store | **M1-canonical** M15/H1/H4 + **native H4→D1AGG** hybrid |
| bars in trade | 24 H4 (~4 days) | 32 M15 (~8 hours) |
| C020 verdict | REJECT (train −0.035R, val +0.053R) | not executed; hypothesis retest on LTF |

C021 is **not** a parameter retune of C020: execution bar granularity, trigger geometry, H1 gate, and provenance are all different.

## Why this is not C008 / C018 / C019 mean-reversion

Mean-reversion family fades extension in low-ADX ranges with z-score / midline exits. C021 is **pro-trend MTF confluence** with hard ATR stop + M15 time stop only — no z-exit, no thesis-invalidation exit stack.

## Why this is not C012 regime switcher

C012 uses D1AGG ATR-percentile regime + short H4 momentum. C021 uses D1 EMA structure + H4/H1 trend alignment + M15 pullback reclaim — no ATR-percentile regime gate.

## Why this is not C013 / C014 / C015 / C016 / C017 / C011

- **C013:** cross-pair currency ranking — C021 is single-pair structure.
- **C014:** calendar event windows — C021 has no event calendar.
- **C015:** failed-breakout fade — C021 requires aligned trends + reclaim, not range false-break fade.
- **C016/C017:** weekly bar logic — C021 is intraday M15 with D1AGG/H4/H1 stack.
- **C011:** random null — C021 is directional structure hypothesis.

## Why lower-timeframe execution is worth testing

C020 showed validation-positive but train-negative expectancy under H4 `next_bar_open`, consistent with **late entries** on a slow bar. Tighter M15 reclaim after HTF agreement may improve entry location without changing the core “trade with HTF confluence” thesis.

## Falsification criteria (future execution only)

- Train expectancy < 0 under `next_bar_open` with frozen parameters
- Validation fails precommitted gates (PF, trade count, pair breadth, 2× cost stress)
- Does not beat deduped C011 null by +0.010R margin
- Backtrader parity fails before any test lockbox
- M15 entries do not improve train/validation split vs C020 directional diagnosis

## No strategy approved

`configs/approved_strategies.yaml` remains `approved: []`. CAMPAIGN_020 remains **REJECT**. This memo does not change any prior verdict.
