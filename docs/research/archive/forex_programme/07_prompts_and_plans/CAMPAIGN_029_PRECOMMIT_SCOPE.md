# CAMPAIGN_029 — PRECOMMIT: USD_JPY 10-pip range-bar MTF breakout

**Strategy:** `usdjpy_range_bar_mtf_breakout`
**Version:** `0.1.0-c029`
**Campaign:** `CAMPAIGN_029`
**Branch:** `research-campaign-029-usdjpy-range-bar-scaffold-001`
**Date frozen:** 2026-05-29
**Status:** `SCAFFOLD_ONLY / NOT_RUN / NOT_APPROVED`

> **This document is the frozen pre-registration of the strategy.** Every rule,
> parameter, threshold, and gate below is committed **before any strategy
> evidence run**. No value here may be changed after seeing evidence; changing any
> rule or gate after results invalidates the campaign. The test lockbox stays
> closed until a later `…-execution-001` sprint passes the train/validation +
> range-bar-parity gates.

---

## 1. Data & timeframes (frozen)

| Role | Bars | Source (frozen) |
|------|------|-----------------|
| Execution / trigger | **10-pip range bars** | built from USD_JPY **M1 mid** prices via `non_time_bars.stream_range_bars` |
| Trend context | **H4 (H4M1)** | `m1_derived` (M1-materialized H4) |
| Macro context (optional) | **D1AGG** | `native_h4_derived_d1agg` (native H4 → D1 aggregation) |

- Pair is **USD_JPY only**. Pip size = `0.01` (JPY quote). Range threshold = **10
  pips** (price moves 0.10 from the bar open in either direction → bar completes).
- Range bars are **candle-atomic**: a single M1 row closes at most one bar; any
  overshoot is recorded, never split into synthetic sub-bars (M1 OHLC cannot
  justify a split). `price_basis = mid`, `duplicate_policy = reject`,
  `require_sorted = true`.
- **No tick data is assumed.** Mid is `(bid+ask)/2` per OHLC field with the
  documented fallback in `non_time_bars._basis_ohlc`.
- The **incomplete final** range bar (`emit_incomplete_final`) is **never traded**
  — only completed bars produce signals or fills.
- M1-derived D1AGG is **rejected** (`m1_derived_d1agg`). D1AGG, when used, must be
  `native_h4_derived_d1agg`.
- All H4 / D1AGG values used at a range-bar decision come from the **last
  completed** HTF bar at the range bar's **close timestamp** (`align_last_completed`).
  No HTF lookahead. See `CAMPAIGN_029_HTF_ALIGNMENT_DESIGN.md`.

## 2. Indicators & parameters (frozen)

### Range bars (execution)
- `range_threshold_pips = 10`.
- `pullback_lookback = 5` — completed range bars **before** the trigger bar that
  are scanned for the pullback leg.
- `structure_lookback = 5` — completed range bars (including the trigger) whose
  swing defines the structural stop.

### H4 (trend context, M1-derived)
- `h4_ema_fast = 20`, `h4_ema_slow = 50`.
- `h4_ema_slope_bars = 3` — slope of the H4 EMA50 over the last 3 completed H4 bars.

### D1AGG (optional macro confirmation, native-H4-derived)
- `d1_ema_fast = 20`, `d1_ema_slow = 50`.
- `d1_ema_slope_bars = 3` — slope of the D1AGG EMA20 over the last 3 completed bars.

### Overshoot guard (anti-spike)
- `overshoot_max_thresholds = 1` — reject a trigger bar whose single closing M1
  candle crossed **more than one** 10-pip threshold (`thresholds_crossed > 1`).
- `overshoot_max_pips = 10.0` — reject a trigger bar whose overshoot beyond the
  10-pip threshold exceeds one full threshold (`overshoot_pips > 10.0`).

### Stop & time
- `stop_range_multiple = 2.0` → stop floor = `2.0 × 10 pip = 20 pip = 0.20` price.
- `max_bars_in_trade = 12` completed range bars (range-bar-count time stop).

## 3. Directional context definitions (frozen)

**H4 trend** (the *mandatory* bias filter):
- **bullish:** H4 `close > EMA50` **and** H4 EMA50 slope over the last 3 completed
  H4 bars `> 0`.
- **bearish:** H4 `close < EMA50` **and** H4 EMA50 slope over the last 3 completed
  H4 bars `< 0`.
- otherwise **neutral** → no trade.
- If H4 is **unavailable or stale** at the decision → **no trade**.

**D1AGG agreement** (*optional* "not against" confirmation):
- If D1AGG is available and not stale at the decision, it must **not oppose** the
  side:
  - long allowed iff D1AGG `close >= EMA50` **or** D1AGG EMA20 slope `>= 0`;
  - short allowed iff D1AGG `close <= EMA50` **or** D1AGG EMA20 slope `<= 0`.
- If D1AGG is **unavailable or stale** at the decision → the D1AGG gate is **not
  applied** (the trade is permitted on H4 alone). This is the only HTF input that
  is optional; H4 is mandatory.

## 4. Range-bar trigger — continuation after pullback & reclaim (frozen)

Evaluated on **completed** range bars only; the *trigger bar* is the most recent
completed range bar at the decision.

**Long** (requires H4 bullish):
1. **Pullback:** within the `pullback_lookback = 5` completed bars **immediately
   before** the trigger bar, at least one bar completed as `range_down`.
2. **Reclaim:** the **trigger bar** completed as `range_up` (i.e. resumed in the
   H4-trend direction).
3. **Anti-spike:** the trigger bar passes the overshoot guard (§2).

**Short** (requires H4 bearish): the mirror — at least one `range_up` in the prior
5 bars, the trigger bar completed `range_down`, and it passes the overshoot guard.

No new signal is emitted while a position is open on USD_JPY (one position per
instrument).

## 5. Entry rules (frozen)

**Long** — all must hold at the trigger-bar close:
1. H4 context bullish (§3).
2. D1AGG not opposing, *if* D1AGG available (§3).
3. Pullback-and-reclaim long trigger present (§4).
4. Trigger bar passes the overshoot guard (§2).
5. Entry = **open of the next completed range bar** (`next_bar_open`).

**Short** — the mirror with bearish H4, D1AGG not opposing, short trigger.

## 6. Stops & exits (frozen — single exact rule)

### Initial stop — the ONE frozen rule
With the trigger-bar close `c`, pip size `p = 0.01`, and the structural swing over
the last `structure_lookback = 5` completed range bars:

- `structure_level(long)`  = **lowest `low`** of the last 5 completed range bars.
- `structure_level(short)` = **highest `high`** of the last 5 completed range bars.
- `d_struct = |c − structure_level|`.
- `d_floor  = stop_range_multiple × range_threshold_pips × p = 2.0 × 10 × 0.01 = 0.20`.
- `stop_distance = max(d_struct, d_floor)`.

```
stop_price(long)  = c − stop_distance
stop_price(short) = c + stop_distance
```

The stop is anchored to the **trigger-bar close** (data available at decision
time); the fill happens at the next range-bar open. The structural level uses only
completed range bars at/before the trigger → no lookahead.

### Time stop
- `max_bars_in_trade = 12` completed range bars. The position is force-exited at
  exactly the 12th completed range bar after entry if neither the stop nor
  end-of-data has triggered first.

### Forbidden exits (frozen)
- **No** take-profit target (none justified at scaffold time).
- **No** trailing stop.
- **No** second/protective stop beyond the single initial hard stop above.

### Exit priority (frozen)
1. `stop` — initial hard stop hit (checked intrabar on subsequent range bars'
   high/low).
2. `time` — 12 completed range bars elapsed since entry.
3. `end_of_data` — run/data boundary.

## 7. Execution realism (frozen)

- `fill_timing = next_bar_open` only — entry is the **open of the next completed
  range bar** after the trigger bar. **No** same-bar range-bar fill; **no** fill on
  the trigger bar itself.
- `evidence_use = approval_bound`; `execution_realism = conservative`.
- Entry timestamp is strictly **after** the trigger timestamp.
- **No** HTF lookahead: all H4 / D1AGG values from the last completed HTF bar at
  the range-bar close timestamp.

## 8. Universe (frozen)

**USD_JPY only.** This campaign makes **no** multi-pair claim. Any future
extension to other pairs must be **separately pre-committed** and justified before
test evidence — it is never an automatic generalisation from a USD_JPY result.

## 9. Splits (frozen, for the future execution sprint)

USD_JPY M1 coverage is **2021-05-27 → 2026-05-26** (local Postgres research store;
confirmed Phase 0). Splits are set inside that coverage; exact range-bar boundary
counts are confirmed by the Phase-2 preflight, which never reveals the test window.

| Split | Range |
|-------|-------|
| train | 2021-05-27 → 2023-12-31 |
| validation | 2024-01-01 → 2024-12-31 |
| test (lockbox) | 2025-01-01 → 2026-05-20 |

## 10. Precommitted gates for the future execution sprint (frozen)

These gates govern a later `…-execution-001` sprint. They are frozen now and may
not be changed after results.

1. **Train expectancy `>= 0`** (per-R, aggregate over USD_JPY).
2. **Validation expectancy `> 0`** (per-R).
3. **Validation profit factor `>= 1.05`**.
4. **Validation trades `>= 100`** (a single-pair range-bar candidate must still
   clear a real sample; if fewer, classify `INSUFFICIENT_SAMPLE`, never PASS).
5. **2× cost-stress validation expectancy `>= 0`**.
6. **Beat the C011 null baseline by `>= +0.010R`**
   (`C011_NULL_EXP_R = -0.0029154071495408797`; threshold ≈ `+0.0070845928R`).
7. **Spread/range-size sanity:** average holding period (in range bars and in
   wall-clock) documented; the **spread / 10-pip-range ratio** must be documented
   and must not let cost dominate expectancy.
8. **Range-bar execution parity required** before any promotion-review
   classification (see `CAMPAIGN_029_BACKTRADER_PARITY_DESIGN.md`).
9. **Test lockbox stays closed** unless the train/validation **and** parity gates
   pass in a later execution sprint.
10. **Maximum possible status after evidence:**
    `RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED` — never approved by this campaign.

## 11. Safety invariants (frozen)

- `configs/approved_strategies.yaml` stays `approved: []`.
- The strategy module has **no** broker / executor / OANDA imports; it is a
  deterministic function of provided range bars + HTF frames. It is **not**
  registered in `strategies/__init__.py` and **not** wired to any loop (range bars
  are not a `CandleFrame.Granularity`; see plan §5).
- Paper / demo / live remain blocked; no executor/broker change; no OANDA
  order/trade/position/transaction/live endpoints; no live credentials.
- No `.env`, credentials, SQLite, raw candle data, or **full generated range-bar
  CSVs** committed. Full bars stay local & gitignored.
- This scaffold sprint runs **no** strategy evidence and opens **no** lockbox.
