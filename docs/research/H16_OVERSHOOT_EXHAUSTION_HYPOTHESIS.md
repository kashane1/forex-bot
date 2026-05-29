# H16 overshoot-exhaustion fade — precise hypothesis

**Sprint:** `research-non-time-bar-overshoot-frontgate-001` · Phase 1
**Type:** definition only. No code, no claims.

---

## 1. Definitions

### Range bar (the clock)
A **range bar** completes when price travels `threshold` pips from the bar's open.
The completing M1 candle is the one whose move carries price across the threshold. The
existing `forex_bot.data.non_time_bars` builder records, per completed bar:
`completion_reason ∈ {range_up, range_down}`, `overshoot_pips`, `thresholds_crossed`,
OHLC, and open/close times.

### Overshoot
**`overshoot_pips`** = how far price travelled **beyond** the threshold in the single
completing M1 candle, i.e. `(|completing-candle move from bar open| − threshold)` in
pips. A bar that *just* crosses the threshold has overshoot ≈ 0; a bar completed by a
violent candle that blows well past the threshold has large overshoot. Overshoot is a
property of the **completion geometry**, not of price level or trend.

### Completion direction
`completion_dir = +1` if `range_up`, `−1` if `range_down`. This is the direction the
bar travelled to complete.

### Exhaustion (the hypothesised effect)
**Exhaustion** = after a bar completes with **unusually large overshoot**, the move is
hypothesised to be *over-extended* (a liquidity gap / stop-run / impulsive candle that
out-ran fair value), so the **next few bars tend to retrace** *against* the completion
direction rather than continue.

### Fade return (how we measure the effect — NOT a trade)
For a bar `i` completing at mid-close `c_i`, and horizon `k ∈ {1,2,3}` bars:
```
fade_return_k(i) = −completion_dir(i) × (c_{i+k} − c_i)      [in pips]
```
- `fade_return_k > 0` ⇒ price **reverted** against the completion move (exhaustion).
- `fade_return_k < 0` ⇒ price **continued** in the completion direction (momentum).

This is a **conditional forward-return measurement**, with no position, stop, sizing,
or PnL. It answers "what does price do after large overshoot?", nothing more.

### Completion geometry (context features recorded)
Per bar: overshoot_pips, `thresholds_crossed` (jump vs smooth completion), session of
completion (UTC bucket), and the spread at completion (for cost/spread-state).

## 2. Candidate thresholds & parameters (pre-declared, fixed — no tuning)

- **Bar threshold:** **30-pip range bars** — the single cost-feasible threshold the
  feasibility study found viable on all majors. One value; no sweep.
- **Pairs:** USD_JPY, EUR_USD, GBP_USD.
- **Overshoot buckets:** per-pair **quartiles** of `overshoot_pips` →
  `small` (Q1), `medium` (Q2), `large` (Q3), `extreme` (Q4); plus an explicit
  **top-5% tail** reported separately. Edges are data-defined quantiles, fixed in
  advance; not optimised toward any outcome.
- **Horizons:** next **1 / 2 / 3** completed bars (event time → short, intraday-scale).
- **Window:** C029 train `2021-05-27 → 2023-12-31` (lockbox untouched).

## 3. Expected holding period

Short — **1 to 3 range bars** in event time. At 30-pip range bars on these pairs the
feasibility study showed median bar durations of tens of minutes to a few hours, so a
1–3 bar fade is **intraday-scale** and is intended to **close before the NY rollover**,
avoiding overnight financing (the C031 channel). No multi-day holds.

## 4. Expected market behaviour if the hypothesis holds

- Reversion (`fade_return_k > 0` on average) that **increases with overshoot magnitude**:
  the `extreme`/`large` buckets fade-positive, the `small` bucket ≈ flat or
  slightly continuation.
- The reversion in the large/extreme buckets is **large enough to exceed round-trip
  cost** at some k ∈ {1,2,3}.
- The effect is **not** merely a restatement of unconditional drift, and **not** a
  shuffle artifact.
- It appears on **≥ 2 of 3** pairs.

## 5. What would have to be true for this idea to work

1. **Overshoot carries information** about subsequent direction (the conditional fade
   return depends on the overshoot bucket — a real gradient).
2. The information is **reversion**, not continuation (sign is positive for large
   overshoot).
3. The reversion is **economically meaningful** — its magnitude exceeds the realistic
   round-trip cost on a cost-feasible bar.
4. It is **not a single-pair / single-session artifact** and **not** explained by a
   shuffled-overshoot null.
5. It is **harvestable on a short, intraday horizon** (so financing is irrelevant).

## 6. What would falsify it (any one ⇒ FAIL)

1. **No gradient:** mean fade return is flat across overshoot buckets (overshoot has no
   conditional information).
2. **Wrong sign:** large overshoot is followed by **continuation**, not reversion (the
   opposite of the thesis — and a *different*, separately-registered hypothesis, not a
   saved win).
3. **Cost-defeated:** any reversion is **smaller than round-trip cost** at all horizons —
   the C029/feasibility failure mode again.
4. **Null-indistinguishable:** the large/extreme-bucket mean sits **inside** the
   shuffled-overshoot null distribution and does not exceed the unconditional baseline.
5. **Fragile:** present on only one pair, or only in the expensive rollover session
   where cost eats it.

## 7. Explicit non-goals

No backtest, no positions, no stops, no PnL, no equity curve, no train/val/test split,
no lockbox, no signal emission, no threshold optimisation, no campaign. This sprint
**measures conditional distributions** and renders a front-gate verdict.
