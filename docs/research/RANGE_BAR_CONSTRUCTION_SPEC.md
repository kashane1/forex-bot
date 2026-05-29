# Range Bar Construction Spec

**Sprint:** `infra-range-and-volatility-bars-001` · Phase 1
**Module:** `src/forex_bot/data/non_time_bars.py` (`RangeBarConfig`, `RangeBar`, `build_range_bars`)
**Status:** infrastructure spec. No strategy, no approval.

A *range bar* completes when price has moved a configured number of **pips away from the bar
open** (in either direction). Bars are event-driven, not time-driven: quiet periods produce few
bars, volatile periods produce many.

---

## 1. Input schema

`build_range_bars` consumes an iterable of `forex_bot.domain.candles.Candle` (the same objects
the Postgres store yields via `_row_to_candle`). Required per row:

| field | use |
|------|-----|
| `instrument` | must be constant across the input; sets pip size |
| `time` (tz-aware UTC) | ordering + provenance timestamps |
| `bid_o/h/l/c`, `ask_o/h/l/c`, `mid_o/h/l/c` | price basis source (see §2) |
| `volume` | summed into the bar |
| `complete` | informational; incomplete source rows are still consumed but counted |

Intended source granularity is **M1**. The builder does not hard-enforce the granularity label
(range bars can in principle be built from any homogeneous base series), but all pip semantics
and the known-limitations section assume M1 OHLC.

## 2. Price basis options

`price_basis ∈ {bid, ask, mid}`. For each row the builder extracts `(o, h, l, c)` from the
matching component:

- `bid` → `bid_o/bid_h/bid_l/bid_c`
- `ask` → `ask_o/ask_h/ask_l/ask_c`
- `mid` → `mid_o/mid_h/mid_l/mid_c`, falling back to `(bid + ask) / 2` per field when the mid
  component is absent (mirrors `CandleFrame.from_candles`).

If the required component is missing for any consumed row, the builder raises `ValueError`
(data-quality failure, surfaced rather than silently coerced).

**Default recommendation: `mid`.** Mid is symmetric and basis-independent of trade direction,
the right default for *structure* research. Spread/cost is a separate, later concern and must be
applied at strategy time (bid for sells, ask for buys); baking a single side into the bar
geometry now would bias any later long/short comparison.

## 3. Pip conversion rules & JPY handling

`pip_size(instrument) = 0.01` when the instrument name ends with `JPY`, else `0.0001`. Pips are
computed as `price_distance / pip_size`. The only JPY pair in the corpus is `USD_JPY`
(pip = 0.01); all others use 0.0001. This matches the existing repo convention
(`research/lifecycle_features.py`, `trade_lifecycle.py`). A pip threshold of e.g. 10 therefore
means a 0.0010 move on EUR_USD and a 0.10 move on USD_JPY.

## 4. Bar OHLC construction

The builder is a strict left-to-right fold over M1 rows. The forming bar holds:
`bar_open` (the open of its first contributing row, in the chosen basis), running `high`,
running `low`, last seen `close`, summed `volume`, first/last source timestamps and source
count.

For each incoming M1 row `(o, h, l, c)`:

1. If no bar is forming, start one: `bar_open = o`, `high = h`, `low = l`, `close = c`.
2. Otherwise merge: `high = max(high, h)`, `low = min(low, l)`, `close = c`, accumulate volume,
   advance `source_end_time` and `source_count`.
3. Compute `up_span = high − bar_open`, `down_span = bar_open − low` (in pips).
4. **Completion test:** if `max(up_span, down_span) ≥ threshold_pips`, the bar completes at this
   row. Its OHLC is `open = bar_open`, `high`, `low`, `close = c` (the completing row's close).
   A new (empty) forming bar starts at the *next* row.

The completed bar's `high`/`low` are the **true M1 extremes** observed across all contributing
rows — including any overshoot past the threshold (see §8). `open` is the genuine first open and
`close` is the genuine completing-row close.

## 5. Timestamp policy

- `open_time` = `time` of the first contributing M1 row.
- `close_time` = `time` of the completing M1 row.
- **Canonical bar timestamp = `close_time`** (completion time), matching the repo convention that
  candle frames are indexed by close (`CandleFrame`). Both timestamps are retained in the record.
- All timestamps are tz-aware UTC, copied verbatim from source rows (no synthesis).

## 6. Source provenance fields (per bar)

`instrument`, `price_basis`, `threshold_pips`, `source_granularity = "M1"`,
`source_start_time` (= open_time), `source_end_time` (= close_time), `source_count`
(number of M1 rows merged), `completion_reason`, `thresholds_crossed`, `overshoot_pips`,
`incomplete`. Plus OHLC + summed `volume`.

## 7. Incomplete final bar policy

When the input ends before the forming bar reaches its threshold, that trailing partial bar is
**dropped by default**. If `emit_incomplete_final = True`, it is emitted with
`incomplete = True`, `completion_reason = "incomplete"`, `thresholds_crossed = 0`, and its OHLC
reflecting whatever was accumulated. Default `False` so downstream research never accidentally
trades a bar that had not actually completed.

## 8. Multi-threshold crossing policy (deterministic)

A single M1 candle can move much further than one threshold (e.g. a 38-pip M1 candle with a
10-pip threshold). **Policy: the completing M1 candle closes exactly one range bar.** We do *not*
fabricate synthetic intra-candle sub-bars, because M1 OHLC cannot resolve the true intrabar path
and inventing boundary-to-boundary sub-bars would manufacture price/timestamp data the source
does not contain.

Instead the single completed bar honestly carries the overshoot, and we record:

- `thresholds_crossed = floor(max(up_span, down_span) / threshold_pips)` — how many full
  thresholds the completing move spanned (≥ 1 by construction).
- `overshoot_pips = max(up_span, down_span) − threshold_pips` — pips beyond the first threshold.

This is fully deterministic and reproducible. Consequence: range bars are **at least**
`threshold` tall but may be taller when a single volatile M1 candle overshoots; bar height is not
forced to a fixed value. (The synthetic fixed-height "Renko-style" alternative is documented in
§11 as rejected for this corpus.)

## 9. Completion-reason / direction rule

`completion_reason ∈ {"range_up", "range_down", "incomplete"}`:

- `"range_up"` if `up_span ≥ down_span` at completion, else `"range_down"`.
- At least one span is `≥ threshold` by construction. Ties (`up_span == down_span`) resolve to
  `"range_up"` (documented deterministic tie-break).

## 10. Deterministic replay rules & lookahead-bias prevention

- **Pure fold, no peeking.** A bar's OHLC and completion decision use only rows at-or-before the
  completing row. The builder never reads the next row to decide the current bar — appending more
  rows can only start/extend *later* bars, never alter an already-completed one. (Asserted by a
  unit test: bars over `rows[:k]` are a prefix of bars over all `rows`.)
- **No intrabar path assumption is required**, because we never split a candle (§8). The only
  modeling content is "OHLC extremes are taken as the candle's true high/low," which is a
  property of the source data, not a forward-looking guess.
- **Same input → identical output**, bit for bit (deterministic float fold over an ordered
  stream).
- **Ordering / duplicates.** Input must be strictly time-increasing. With `require_sorted = True`
  (default) unsorted input raises `ValueError`; `False` sorts a copy first. Duplicate timestamps:
  `duplicate_policy = "reject"` (default) raises; `"keep_first"` / `"keep_last"` dedupe
  explicitly. Nothing is silently reordered or dropped under the defaults.

## 11. Known limitations (M1 OHLC vs true tick data)

- **Intrabar path is unknown.** We only know each minute's O/H/L/C, not the order in which high
  and low were touched. We sidestep this by never splitting a candle, but it means within-candle
  overshoot is attributed to a single bar rather than to several (§8). A true tick feed would let
  a fast 38-pip minute spawn multiple clean range bars.
- **Synthetic fixed-height range bars are intentionally NOT produced.** They would require a
  fabricated intrabar path and would inject non-existent prices/timestamps — rejected as
  dishonest for this OHLC corpus.
- **Weekend/session gaps.** M1 has gaps (FX close, holidays). A range bar can therefore span a
  gap; `source_start_time`/`source_end_time` make such spans inspectable.
- **Pip threshold is in price space, not cost space.** Spread/commission is not modeled here; a
  5-pip range bar is *not* a tradable 5-pip move after costs. Cost feasibility is a strategy-time
  concern and explicitly out of scope for this infrastructure.
