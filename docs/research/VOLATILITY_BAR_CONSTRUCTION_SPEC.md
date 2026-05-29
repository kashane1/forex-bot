# Volatility Bar Construction Spec

**Sprint:** `infra-range-and-volatility-bars-001` · Phase 1
**Module:** `src/forex_bot/data/non_time_bars.py`
(`VolatilityBarConfig`, `VolatilityBar`, `build_volatility_bars`)
**Status:** infrastructure spec. No strategy, no approval.

A *volatility bar* completes when a **cumulative realized-movement proxy** reaches a configured
threshold (in pips). Unlike a range bar (which measures displacement from the bar open), a
volatility bar measures *path length / activity*: a choppy market that ends where it started can
still complete many volatility bars.

---

## 1. Input schema

Identical to the range-bar spec §1: an iterable of `forex_bot.domain.candles.Candle`, constant
`instrument`, tz-aware UTC `time`, bid/ask/mid OHLC, `volume`, `complete`. Intended source
granularity is **M1**.

## 2. Price basis options

`price_basis ∈ {bid, ask, mid}`, extracted exactly as in the range-bar spec §2 (mid falls back to
`(bid + ask) / 2` per field; missing required component → `ValueError`).
**Default recommendation: `mid`** (basis-independent of trade direction; cost applied later).

## 3. Pip conversion rules & JPY handling

Same as range bars: `pip_size = 0.01` for names ending `JPY` (only `USD_JPY` here), else `0.0001`.
All movement proxies are accumulated **in pips**.

## 4. Movement proxies (`method`)

Two deterministic proxies are implemented. Both accumulate a per-row increment, in pips, into a
running `movement` total for the forming bar.

### 4a. `abs_close` — cumulative absolute close-to-close
`increment_i = |close_i − close_{i-1}| / pip_size`, where `close_{i-1}` is the close of the
immediately preceding M1 row **in the input stream** (this carry persists *across* bar
boundaries — it is a property of the price series, not reset per bar). For the very first row of
the whole input there is no prior close, so `increment_0 = |close_0 − open_0| / pip_size`
(uses only that row's own data).

### 4b. `true_range` — cumulative true range
`increment_i = TR_i / pip_size` where
`TR_i = max(high_i − low_i, |high_i − close_{i-1}|, |low_i − close_{i-1}|)`,
with `close_{i-1}` the previous M1 row's close (carried across bar boundaries). For the first row,
`close_{i-1} := open_0`, so `TR_0 = high_0 − low_0`. Standard Wilder true range, no future data.

Both proxies use only the current row and the *previous* row's close — never a future row.

## 5. Threshold modes (`threshold_mode`)

### 5a. `fixed`
`threshold_pips` is a constant (e.g. 10, 20, 30, 50). Required when mode is `fixed`.

### 5b. `atr_scaled` (optional, prior-completed-data only)
The effective threshold for a forming bar is snapshot **once at bar open**:
`effective_threshold = atr_multiple × ATR_prior`, where `ATR_prior` is the mean true range (in
pips) over the trailing window of the last `atr_window` **already-completed M1 rows seen before
this bar opened**. Requires `atr_multiple` and `atr_window`.

Lookahead safety is structural: the window contains only M1 rows that closed *before* the bar
opened, the threshold is fixed for the whole life of the forming bar, and it is recomputed only at
the *next* bar open. The forming bar's own rows can never influence its own threshold. Until at
least `atr_window` prior rows exist, the builder is in a **warm-up** state and emits no completed
bars (warm-up row count is reported in diagnostics).

## 6. Bar OHLC construction

Left-to-right fold, same structure as range bars: `open` = first contributing row's open (basis),
running `high`/`low`, `close` = last row's close, summed `volume`. After merging each row, add the
movement increment (§4) to the running `movement`. **Completion:** when
`movement ≥ effective_threshold`, the bar completes at that row; a new forming bar starts at the
next row with `movement` reset to 0 (the cross-boundary `close_{i-1}` carry persists).

## 7. Timestamp policy

Identical to range bars §5: `open_time` = first row time, `close_time` = completing row time,
canonical bar timestamp = `close_time`, all tz-aware UTC copied verbatim.

## 8. Source provenance fields (per bar)

`instrument`, `price_basis`, `method`, `threshold_mode`, `threshold_pips` (the **effective**
threshold used for this bar — equal to the constant for `fixed`, or the per-bar ATR snapshot for
`atr_scaled`), `source_granularity = "M1"`, `source_start_time`, `source_end_time`,
`source_count`, `movement_pips` (accumulated movement at completion), `completion_reason`,
`thresholds_crossed`, `overshoot_pips`, `incomplete`. Plus OHLC + summed `volume`.

## 9. Incomplete final bar policy

Same as range bars §7: the trailing partial bar (movement below threshold at input end) is
**dropped by default**; emitted with `incomplete = True`, `completion_reason = "incomplete"` only
when `emit_incomplete_final = True`.

## 10. Multi-threshold crossing policy (deterministic)

If a single high-movement M1 row pushes the accumulator well past the threshold, the bar completes
once at that row (candle-atomic — consistent with the range-bar spec §8). We record:

- `thresholds_crossed = floor(movement_pips / effective_threshold)` (≥ 1 by construction),
- `overshoot_pips = movement_pips − effective_threshold`.

The accumulator resets to 0 at completion; overshoot is **recorded, not carried** into the next
bar. Because movement is accumulated from many small M1 increments, overshoot is typically bounded
by a single row's increment and small in practice (reported in diagnostics). The alternative
(carrying overshoot forward) is noted in §12 as a deliberately rejected variant for simplicity and
cross-consistency with range bars.

## 11. Completion-reason rule

`completion_reason ∈ {"volatility", "incomplete"}`. Volatility bars are directionless (they
measure activity, not displacement), so there is no up/down reason — direction, if needed later,
is read from `close` vs `open` by the consumer.

## 12. Deterministic replay rules & lookahead-bias prevention

- **Pure causal fold.** Increments depend only on the current row and the previous row's close;
  completion depends only on rows at-or-before the completing row; `atr_scaled` thresholds depend
  only on already-completed prior rows. No future row is ever read. Appending rows cannot alter an
  already-completed bar (unit-tested as a prefix property).
- **Same input → identical output** (deterministic float fold over an ordered stream).
- **Ordering / duplicates.** Same as range bars §10: `require_sorted = True` (default) raises on
  unsorted input; `duplicate_policy = "reject"` (default) raises on duplicate timestamps;
  `keep_first` / `keep_last` dedupe explicitly. No silent reordering/dropping under defaults.
- **Rejected variant:** carrying movement overshoot across bars. Rejected for simplicity and to
  keep the multi-threshold policy identical to range bars; the effect is small and the overshoot
  is recorded for auditability.

## 13. Known limitations (M1 OHLC vs true tick data)

- **Path length is undercounted.** `abs_close` only sees minute closes, so intrabar round-trips
  inside one minute are invisible; `true_range` captures the minute's high-low excursion but still
  misses sub-minute oscillation. True realized volatility from tick data would be larger. The
  proxies are therefore *lower bounds* on activity, but they are deterministic and lookahead-free.
- **`abs_close` vs `true_range` differ systematically.** `true_range` ≥ `|Δclose|` per row, so for
  the same pip threshold a `true_range` bar completes after fewer rows than an `abs_close` bar.
  The two are not interchangeable; diagnostics report both.
- **ATR warm-up.** The first `atr_window` rows produce no `atr_scaled` bars; this is expected and
  reported, not an error.
- **Pip threshold is price-space, not cost-space.** As with range bars, spread/commission is not
  modeled; volatility-bar thresholds are not net-of-cost tradable moves. Cost feasibility is a
  strategy-time concern, out of scope here.
