# CAMPAIGN_024 — PRECOMMIT: M5 Donchian + HTF confluence breakout

**Strategy:** `m5_donchian_htf_confluence_breakout`
**Version:** `0.1.0-c024`
**Campaign:** `CAMPAIGN_024`
**Branch:** `research-campaign-024-m5-donchian-htf-confluence-scaffold-001`
**Date frozen:** 2026-05-28
**Status:** `SCAFFOLD_ONLY / NOT_RUN / NOT_APPROVED`

> **This document is the frozen pre-registration of the strategy.** Every rule,
> parameter, threshold, and gate below is committed **before any evidence run**.
> No value here may be changed after seeing evidence. Changing any rule or gate
> after results invalidates the campaign. The test lockbox stays closed until a
> later execution sprint passes the train/validation + Backtrader-parity gates.

---

## 1. Data & timeframes (frozen)

| Role | Timeframe | Source (frozen) |
|------|-----------|-----------------|
| Execution / trigger | **M5** | `m1_materialized` (M1-derived) |
| Local setup | **M15** | `m1_materialized` (M1-derived) |
| Trend context | **H1** | `m1_materialized` (M1-derived) |
| Trend context | **H4 (H4M1)** | `m1_materialized` (M1-derived) |
| Macro regime | **D1AGG** | `native_h4_derived_d1agg` (native H4 → D1 aggregation) |

- M1-derived D1AGG is **rejected** (`m1_derived_d1agg`) until M1→D1AGG day
  completeness is fixed.
- All higher-timeframe (M15/H1/H4/D1AGG) values used at an M5 decision must come
  from the **last completed** HTF bar (`align_last_completed`). No HTF lookahead.

## 2. Indicators & parameters (frozen)

### M5 (execution)
- `entry_channel_length = 20` — Donchian over the **prior 20 completed M5 bars**.
  - `donchian_high` / `donchian_low` use `.shift(1)` → current bar is **never**
    part of its own channel (no current-bar lookahead).
- `atr_lookback = 14` — M5 ATR(14). The ATR used for stop sizing is the value at
  the **prior** completed M5 bar (`atr.iloc[-2]`), never the signal bar's own ATR.

### M15 (local setup)
- `m15_pullback_lookback = 8` — pullback window in completed M15 bars.
- `m15_ema_fast = 20`, `m15_ema_slow = 50` — EMAs for pullback touch test.
- `m15_compression_donchian_lookback = 12` — local range-contraction window.
- `m15_compression_atr_lookback = 14`.
- `m15_compression_width_atr_max = 3.0` — compression iff
  `Donchian(12) channel width / ATR(14) <= 3.0`. (Frozen precommit threshold.)

### H1 (trend context)
- `h1_ema_fast = 20`, `h1_ema_slow = 50`.
- `h1_ema_slope_bars = 3` — slope of EMA20 over last 3 completed H1 bars.

### H4 / H4M1 (trend context)
- `h4_ema_fast = 20`, `h4_ema_slow = 50`.

### D1AGG (macro regime)
- `d1_ema_fast = 20`, `d1_ema_slow = 50`.
- `d1_ema_slope_bars = 3` — slope of D1AGG EMA20 over last 3 completed D1AGG bars.

## 3. Directional context definitions (frozen)

**H1 trend**
- bullish: `EMA20 > EMA50` **and** EMA20 slope over last 3 completed H1 bars `>= 0`.
- bearish: `EMA20 < EMA50` **and** EMA20 slope over last 3 completed H1 bars `<= 0`.
- otherwise neutral.

**H4 trend**
- bullish context: `close > EMA50` **and** `EMA20 >= EMA50`.
- bearish context: `close < EMA50` **and** `EMA20 <= EMA50`.
- otherwise neutral.

**D1AGG regime** (a permissive "not against" filter)
- **not bearish** (long allowed): `D1AGG close >= D1AGG EMA50` **OR**
  D1AGG EMA20 slope over last 3 completed D1AGG bars `>= 0`.
- **not bullish** (short allowed): `D1AGG close <= D1AGG EMA50` **OR**
  D1AGG EMA20 slope over last 3 completed D1AGG bars `<= 0`.
- If D1AGG is unavailable or stale at the decision → **no trade**.

## 4. M15 setup (pullback OR compression) (frozen)

A long setup requires (pullback **OR** compression):
- **pullback:** within the last `m15_pullback_lookback = 8` completed M15 bars,
  the M15 **low touched or moved below EMA20** (`low <= EMA20`) on at least one bar.
- **compression:** current M15 `Donchian(12) width / ATR(14) <= 3.0`.

A short setup requires (pullback **OR** compression):
- **pullback:** within the last 8 completed M15 bars, the M15 **high touched or
  moved above EMA20** (`high >= EMA20`) on at least one bar.
- **compression:** current M15 `Donchian(12) width / ATR(14) <= 3.0`.

This precondition is mandatory — it exists to prevent pure high-turnover breakout
chasing.

## 5. Entry rules (frozen)

**Long setup** (all must hold at the M5 signal bar close):
1. H4 context bullish.
2. H1 context bullish.
3. D1AGG context **not bearish**.
4. M15 pullback **or** compression present (§4).
5. M5 **close > prior 20-bar Donchian high** (the breakout trigger).
6. Entry = **next M5 bar open** (`next_bar_open`).

**Short setup** (all must hold at the M5 signal bar close):
1. H4 context bearish.
2. H1 context bearish.
3. D1AGG context **not bullish**.
4. M15 pullback **or** compression present (§4).
5. M5 **close < prior 20-bar Donchian low** (the breakout trigger).
6. Entry = **next M5 bar open** (`next_bar_open`).

No new signal is emitted while a position is open on that instrument.

## 6. Stops & exits (frozen — single exact rule)

### Initial stop — the ONE frozen rule
The initial stop is placed at **whichever is farther** from the M5 signal-bar
close of these two levels:

- **(a) ATR stop:** `2.0 × ATR(14)` from the signal-bar close, where the ATR is
  the value at the **prior** completed M5 bar.
- **(b) Structure stop:** the opposite side of the recent M5 structure, defined
  as the **prior 20-bar M5 Donchian low** (for a long) / **Donchian high** (for
  a short) — i.e. the far side of the same channel that produced the trigger.

Formally, with `d_atr = 2.0 * prior_atr` and
`d_struct = |signal_close - structure_level|`:

```
stop_distance = max(d_atr, d_struct)
stop_price(long)  = signal_close - stop_distance
stop_price(short) = signal_close + stop_distance
```

The stop is anchored to the **signal-bar close** (data available at decision
time); the fill happens at the next bar open. Stop distance uses only prior
completed M5 bars, so there is no lookahead.

- `atr_stop_multiple = 2.0` (frozen).
- `structure_lookback = 20` (= `entry_channel_length`, frozen).

### Position risk
- `risk_per_trade_pct = 0.25` (research default; existing risk conventions).

### Time stop
- `max_bars_in_trade = 48` M5 bars. The position is force-exited at exactly the
  48th completed M5 bar after entry if neither the stop nor end-of-data has
  triggered first.

### Forbidden exits (frozen)
- **No** take-profit target.
- **No** trailing stop.
- **No** protective stop (beyond the single initial hard stop above).

### Exit priority (frozen)
1. `stop` (initial hard stop hit)
2. `time` (48 M5 bars elapsed)
3. `eod` / `end_of_data` (run/session boundary)

## 7. Execution realism (frozen)

- `fill_timing = next_bar_open` only.
- `evidence_use = approval_bound`; `execution_realism = conservative`.
- **No** `signal_bar_close` fills; **no** same-bar entry on the signal bar.
- **No** lookahead from H1/H4/D1AGG context; all HTF values from the last
  completed higher-timeframe bar.
- Entry timestamp is strictly **after** the signal timestamp.

## 8. Universe (frozen)

Seven majors for scaffold compatibility, with mandatory **pair-level
diagnostics**: `EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD`.

The strategy is **not** assumed to work on every pair. A future single-pair
continuation is permitted **only** if pre-committed and justified **before** test
evidence (`SINGLE_PAIR_REVIEW_ONLY`, never an automatic PASS).

## 9. Precommitted gates for the future execution sprint (frozen)

These gates govern a later `…-train-validation-001` sprint. They are frozen now
and may not be changed after results.

1. **Train expectancy `>= 0`** (per-R, aggregate).
2. **Validation expectancy `> 0`** (per-R, aggregate).
3. **Validation profit factor `>= 1.05`**.
4. **Validation trades `>= 100`** (aggregate across pairs).
5. **At least 4/7 pairs non-negative on validation**, OR — if that fails but one
   pair is materially strong — classify `SINGLE_PAIR_REVIEW_ONLY`, **not** PASS.
6. **2× cost-stress validation expectancy `>= 0`**.
7. **Beat the C011 null baseline by `>= +0.010R`**
   (`C011_NULL_EXP_R = -0.0029154071495408797`; threshold ≈ `+0.0070845928R`).
8. **Average holding period** not so short that spread dominates; the
   **spread/ATR ratio** must be documented.
9. **Backtrader parity required** before any promotion-review classification.
10. **Test lockbox stays closed** unless train/validation **and** parity gates
    pass in a later execution sprint.
11. **Maximum possible status after evidence:**
    `RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED` — never approved by this campaign.

## 10. Splits (frozen, for the future sprint)

| Split | Range |
|-------|-------|
| train | 2020-01-01 → 2022-12-31 |
| validation | 2023-01-01 → 2024-12-31 |
| test (lockbox) | 2025-01-01 → 2026-05-20 |

## 11. Safety invariants (frozen)

- `configs/approved_strategies.yaml` stays `approved: []`.
- Strategy module has **no** broker/executor/OANDA imports; deterministic from
  provided bar data.
- Paper/demo/live remain blocked; no executor/broker change; no OANDA
  order/trade/position/transaction/live endpoints; no live credentials.
- No `.env`, credentials, SQLite, raw candle data, or bulky artifacts committed.
- This scaffold sprint runs **no** full evidence and opens **no** lockbox.
