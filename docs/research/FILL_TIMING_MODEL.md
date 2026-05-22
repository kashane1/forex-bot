# Fill-Timing Model

**Date:** 2026-05-22 · **Branch:** `infra-execution-fidelity-001` · Phase 1

The backtest engine now has an explicit **fill-timing model** —
*which bar's quote a backtest entry fills against*. It is separate
from the `FillModel` (which decides the fill *price* from a bid/ask
quote: ask for a long, bid for a short, plus slippage).

Two timings are supported, set by `backtest.fill_timing`:

| value | entry fills at | status |
|---|---|---|
| `signal_bar_close` | the close of the completed signal bar N | default |
| `next_bar_open` | the open of bar N+1 | opt-in |

## Why signal-bar-close is optimistic — and risky

The engine replays completed bars. A signal computed on bar N can only
*exist* once bar N has closed: the strategy reads bar N's close, EMAs,
Donchian channel, ATR — none of which is known until the bar is done.

`signal_bar_close` then fills the entry at **that same close price**.
That is a subtle look-back: it executes at a price that, by the time
the signal is actually known, has already passed. It assumes a
zero-latency fill at a price no live trader could still get. The
effects:

- **Optimistic entries.** In a trending move the close that triggered
  a breakout is often a local extreme; filling there flatters every
  breakout strategy.
- **Understated slippage.** Real execution happens *after* the
  decision, into the next bar, where the price has already moved.
- **Bigger distortion at lower frequency.** On H4 the gap between a
  bar's close and the next bar's open is usually small. On daily bars
  it can be large — an overnight gap is a full session of drift.

It is not a *bug* — it is a known, documented modelling choice — but it
makes `signal_bar_close` results an **upper bound** on a strategy's
real performance, not a realistic estimate.

## What next-bar-open does

With `next_bar_open`:

1. The strategy still computes the signal on completed bar N — exactly
   as before. The strategy sees no future data.
2. The entry fills at **bar N+1's bid/ask open** — the first price
   actually tradeable once the signal is known.
3. Position sizing, the spread filter, and the risk-engine gates are
   evaluated against bar N+1's open quote — the quote that the fill
   actually occurs at.
4. Stops, trailing stops, the take-profit target, and the time stop
   are unchanged. The trade exists from bar N+1 onward; the engine
   checks bar N+1's full high/low range for an exit, so a position can
   be entered and stopped within the same bar.
5. **If bar N+1 does not exist** — the signal fired on the final bar of
   the data — the signal is recorded as an explicit skipped/rejected
   signal with code `NEXT_BAR_OPEN_UNAVAILABLE`. It is never silently
   dropped and never given a same-bar fallback fill.

### No lookahead

`next_bar_open` uses **no future data**. Bar N+1's *open* is the single
extra price consulted, and it is the first price that exists *after*
the signal is known — that is execution, not foresight. The engine
test suite asserts this directly: mutating every bar strictly after
N+1 leaves the entry price and entry time unchanged
(`tests/unit/test_fill_timing.py`).

## Implications for D1AGG

D1AGG (`forex_bot.backtesting.d1_aggregation`) builds synthetic daily
research bars from H4 candles. Daily-frequency research is exactly
where `signal_bar_close` is most misleading:

- A daily bar's close-to-next-open gap spans an entire overnight
  session. Filling a daily breakout at the signal bar's close can
  overstate the entry by far more than one H4 candle ever would.
- Any future low-frequency research on D1AGG should therefore run
  `next_bar_open` as the **primary** result, and may report
  `signal_bar_close` only as an optimistic reference bound.
- The D1AGG bar is timestamped at its research-day close (13:00 NY),
  clear of the rollover blackout. The N+1 bar is the *next* D1AGG bar,
  also clear of the blackout — `next_bar_open` does not re-introduce
  the CAMPAIGN_006 rollover-contamination problem.

This is a fidelity capability only. D1AGG remains research-grade
infrastructure; nothing here approves a strategy or a timeframe.

## Compatibility with old campaigns

`signal_bar_close` is the **default**, and it is deliberately
conservative about reproducibility:

- Campaign configs (`configs/campaign_*.yaml`) do not contain a
  `backtest.fill_timing` key. They load with the default
  `signal_bar_close` and reproduce their **exact** prior trades,
  metrics, and equity curves.
- The engine only folds `fill_timing` into its `config_hash` when it
  departs from `signal_bar_close`. A `signal_bar_close` run therefore
  produces the **same `config_hash`** as it did before this feature
  existed, so prior campaign artifacts (CAMPAIGN_001–009) stay
  hash-comparable. A `next_bar_open` run gets a distinct `config_hash`,
  so the two can never be silently confused.
- Every trade record, the trades CSV, the metrics Markdown, and the
  metrics / summary JSON now carry an explicit `fill_timing` field, so
  any artifact states which timing produced it.

Prior campaigns are **not** re-run as part of this sprint. Re-running
any of them under `next_bar_open` would be new research and is out of
scope here — it would need a fresh, pre-committed campaign.

## How to use it

```bash
# Config: configs/<your-config>.yaml
backtest:
  fill_timing: next_bar_open      # default: signal_bar_close

# CLI override (takes precedence over the config value):
bot backtest --config configs/paper.yaml --fill-timing next_bar_open
```

## Recommendation

- Treat `signal_bar_close` results as an **optimistic upper bound**.
- Any *future* (human-authorized) campaign — especially on D1AGG or any
  low-frequency timeframe — should pre-commit to `next_bar_open` as the
  headline result.
- This does not change any verdict already on record. Every campaign
  (CAMPAIGN_001–009) remains REJECT / NO-GO, and no strategy is
  approved.
