# M1 / HTF Confluence — State Definitions

**Status:** DEFINITIONS LOCKED (pre-analysis)
**Date:** 2026-05-29
**Branch:** `research-m1-htf-confluence-sampling-matrix-001`
**Freeze state:** intact — definitions only; not a strategy, not entry/exit rules.

These are **context states**, not trade signals. A state describes a multi-timeframe market
context and carries a **context direction** (+1 long-context, −1 short-context) used only to
*sign the forward return* so a directional bias can be tested. There are no entries, exits,
stops, targets, or sizing here. Definitions are fixed before any numbers are computed so the
discovery passes cannot be tuned to the data.

---

## 1. Timeframes

- **Execution / response timeframe:** M1 (the thing we measure forward movement on).
- **Structure timeframes (candidate):** M5, M15.
- **Trend timeframes (candidate):** M15, H1, H4 (stored as `H4M1`, aggregated from M1).

All HTF features are computed on the HTF's own completed bars and then mapped onto each M1
timestamp **lookahead-safe**: an HTF bar is usable on an M1 bar only once the HTF bar has
*completed* (its close time ≤ the M1 bar's time). No future HTF information ever touches an
M1 timestamp.

## 2. Primitives (simple, explicit — no pattern recognition)

Computed on each HTF series with the shared indicator helpers
(`forex_bot.strategies.indicators`). Locked parameters:

| Primitive | Definition (on an HTF series) |
|---|---|
| `ema_fast` | `ema(close, 20)` |
| `ema_slow` | `ema(close, 50)` |
| `slope` | `ema_slope(close, 50, lookback=3)` (change in EMA50 over 3 completed HTF bars) |
| `trend_up` | `close > ema_slow` **and** `slope > 0` |
| `trend_down` | `close < ema_slow` **and** `slope < 0` |
| `aligned_up` | `close > ema_slow` (structure agrees with up) |
| `aligned_down` | `close < ema_slow` |
| `pullback_up` | `close > ema_slow` **and** `close < ema_fast` (price dipped below fast EMA inside an up context) |
| `pullback_down` | `close < ema_slow` **and** `close > ema_fast` |
| `breakout_up` | `close > donchian_high(high, 20).shift(1)` (close exceeds the prior 20-bar high; shift avoids self-inclusion) |
| `breakout_down` | `close < donchian_low(low, 20).shift(1)` |
| `compression` | `atr(14) ≤ 33rd-percentile ATR over the trailing 100 completed HTF bars` |

Rationale for the parameter choices: EMA 20/50 and Donchian-20 are conventional, round, and
were *not* selected by scanning outcomes; tercile compression and a 3-bar slope lookback are
likewise fixed a priori. The point of the sprint is to ask whether *any* reasonable,
un-tuned confluence shows conditional structure — not to find the best parameters (which would
be optimization, and is forbidden here).

## 3. Confluence states (9 archetypes × 2 directions = 18 signed states)

Each archetype is defined as an HTF context condition. Its **long** instance uses the `_up`
primitives with direction +1; its **short** instance mirrors with `_down` primitives and
direction −1. The signed forward return is `direction × (M1 forward mid return)`, so a
*positive* mean signed return means price tended to move **in the direction the context
implied**.

### Family A — M5 structure + M15 trend

| Archetype | Long condition | Dir |
|---|---|---|
| `A1_trend_cont` | M15 `trend_up` **and** M5 `aligned_up` | ±1 |
| `A2_pullback` | M15 `trend_up` **and** M5 `pullback_up` | ±1 |
| `A3_breakout` | M15 `trend_up` **and** M5 `breakout_up` | ±1 |
| `A4_compression` | M15 `trend_up` **and** M5 `compression` | ±1 |

### Family B — M15 structure + H1 trend

| Archetype | Long condition | Dir |
|---|---|---|
| `B1_trend_cont` | H1 `trend_up` **and** M15 `aligned_up` | ±1 |
| `B2_pullback` | H1 `trend_up` **and** M15 `pullback_up` | ±1 |
| `B3_breakout` | H1 `trend_up` **and** M15 `breakout_up` | ±1 |

### Family C — M15 structure + H1 trend + H4 trend

| Archetype | Long condition | Dir |
|---|---|---|
| `C1_trend_cont` | H4 `trend_up` **and** H1 `trend_up` **and** M15 `aligned_up` | ±1 |
| `C2_pullback` | H4 `trend_up` **and** H1 `trend_up` **and** M15 `pullback_up` | ±1 |

(Short instances replace every `_up` with the corresponding `_down` and use direction −1.
Compression is direction-agnostic in itself; `A4` pairs it with the M15 trend sign, testing
whether compression *inside a trend* precedes expansion in the trend's direction.)

## 4. Event sampling (de-overlapping)

A state is `True` on many consecutive M1 bars, which would make naive per-bar samples heavily
autocorrelated and inflate apparent significance. To get near-independent samples:

- An **event** is the **rising edge** of a state's condition (transition `False → True`).
- A **cooldown of 60 minutes** is enforced: after an event, no new event of the *same* state
  is recorded until 60 minutes have elapsed. Since 60 min is the longest forward horizon,
  consecutive events' forward windows do not overlap.

This is a sampling/independence decision, not an entry rule — there is no position taken at an
event; we only *observe* what M1 does afterward.

## 5. Recorded fields & forward response (locked)

For each event: `timestamp`, `pair`, `state`, `direction`, `session`, `spread` (pips at the
event bar, `ask−bid`), `volatility` (trend-TF `atr(14)` in pips at the event).

Sessions (UTC hour): `tokyo` 00–07, `london` 07–12, `ny` 12–21, `offhours` 21–24.

Forward response measured at horizons **5, 10, 15, 30, 60 minutes** on M1 **mid** prices,
entry = event-bar mid close:

- **forward_return** — signed: `direction × (mid[t+h] − mid[t]) / pip`, in pips.
- **MFE** — max favorable excursion (pips): `max over the window of direction×(mid − entry)`, floored at 0.
- **MAE** — max adverse excursion (pips): `min over the window of direction×(mid − entry)`, capped at 0 (reported as a non-negative magnitude).
- **MFE/MAE** — ratio of the two magnitudes.
- **directional hit rate / P(positive) / P(negative)** — fraction of events with signed forward_return >0, ==/<0 at the horizon.

Pip size: USD_JPY = 0.01, EUR_USD = 0.0001.

**Gaps:** the horizon endpoint is the M1 bar whose time is the first ≥ `t + h`. If that bar's
time exceeds `t + h` by more than a 5-minute tolerance (weekend / data gap), the event is
dropped *for that horizon*. The excursion window is all M1 bars with `t < time ≤ endpoint`.

**No positions, no PnL, no stops, no targets.** Spread is recorded and reported for
spread-awareness; it does not gate or close anything. This stays pure response analysis.
