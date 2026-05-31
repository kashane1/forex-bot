# CAMPAIGN_029 — HTF alignment design (range bars → H4 / D1AGG)

**Strategy:** `usdjpy_range_bar_mtf_breakout 0.1.0-c029`
**Status:** `SCAFFOLD_ONLY / NOT_RUN / NOT_APPROVED`
**Companion:** `CAMPAIGN_029_PRECOMMIT_SCOPE.md` (binding rule)

> This document specifies **exactly** how each 10-pip range bar reads
> higher-timeframe context without lookahead. It reuses the existing
> `forex_bot.features.htf_align.align_last_completed` infra — no bespoke
> alignment is introduced.

---

## 1. The alignment problem for range bars

Range bars are **event-driven**, not clock-driven: a USD_JPY 10-pip bar can span
1 minute or (across a weekend gap) ~3 days (preflight: median elapsed 600 s, max
266,040 s). So "the H4 bar for this range bar" is **not** a fixed offset — it must
be resolved by **timestamp** against the H4 / D1AGG series.

The decision instant for a range bar is its **close timestamp**
(`RangeBar.close_time`, which equals `RangeBar.time`). That is the first moment all
of the bar's information exists. HTF context is resolved **as of that instant**.

## 2. Resolution rule (frozen)

For a range bar closing at `t = bar.close_time`:

1. **H4 (H4M1, M1-derived) — mandatory.** Take the **single last completed H4 bar**
   with `h4_close_time <= t`, via
   `align_last_completed(pd.DatetimeIndex([t]), h4_frame, [...], complete_column="complete")`.
   - The H4 frame is pre-filtered to **completed bars only** (`CandleFrame.completed_only()`),
     so a partially-formed H4 bar can never be selected.
   - The H4 trend (close vs EMA50, EMA50 slope over the last 3 completed H4 bars) is
     computed from bars **at or before** that aligned bar (the slope helper masks
     `times <= anchor_time`). No H4 bar that closes after `t` is ever read.

2. **D1AGG (native-H4-derived) — optional confirmation.** Take the **single last
   completed D1AGG bar** with `d1agg_close_time <= t`, same `align_last_completed`
   call. D1AGG must carry provenance `native_h4_derived_d1agg`; `m1_derived_d1agg`
   is **rejected** at signal time (raises).

3. **No partially completed HTF bars.** Only rows with `complete == true` are
   eligible. The current, still-forming H4 / D1AGG bar (whose close is in the
   future relative to `t`) is structurally excluded.

4. **Entry vs decision.** Context is resolved at the **trigger bar close** `t`; the
   **entry** is the **open of the next completed range bar** (`next_bar_open`),
   whose timestamp is strictly `> t`. The HTF context that authorised the entry is
   therefore strictly older than the entry — never coincident, never future.

## 3. Stale / missing HTF behaviour (frozen)

`align_last_completed` returns a per-decision `*_blocked_reason` of `HTF_UNAVAILABLE`
(no completed HTF bar at/before `t`) or `HTF_STALE` (last completed bar older than
`max_staleness`, when a staleness bound is supplied).

| HTF input | unavailable / stale at `t` | behaviour (frozen) |
|-----------|----------------------------|--------------------|
| **H4** (mandatory bias) | `HTF_UNAVAILABLE` / `HTF_STALE` | **No trade.** The bias filter cannot be evaluated → skip the range bar. |
| **D1AGG** (optional) | `HTF_UNAVAILABLE` / `HTF_STALE` | **D1AGG gate not applied.** The trade is permitted on H4 alone; the signal records that D1AGG was absent. |

Staleness bounds for the *future execution sprint*: a candidate `max_staleness` of
**2 × H4 = 8 h** for H4 and **3 calendar days** for D1AGG (covering weekend gaps)
is the precommit default; the execution sprint may tighten but not loosen these,
and must document the chosen value before running.

## 4. Provenance fields required in future trade logs (frozen)

Every signal / trade record produced by a future execution sprint MUST carry, so
that lookahead can be audited after the fact:

| field | meaning |
|-------|---------|
| `decision_time` | range bar `close_time` (`t`) — when context was read |
| `source_candle_timestamp` | trigger range bar `close_time` |
| `available_data_cutoff` | `t` — no data after this was used |
| `entry_time` | next completed range bar `open_time` (`> t`) |
| `htf_feature_times.h4` | aligned H4 bar close time used (`<= t`) |
| `htf_feature_times.d1agg` | aligned D1AGG bar close time used (`<= t`), or omitted if absent |
| `data_provenance.execution_bars` | `range_bar_10pip_m1_mid` |
| `data_provenance.context_h4` | `m1_derived` |
| `data_provenance.d1agg_context` | `native_h4_derived_d1agg` |
| `d1agg_applied` | bool — whether the optional D1AGG gate bound this decision |

These are validated by the existing
`forex_bot.features.htf_align.validate_signal_provenance` /
`validate_htf_provenance` (every `htf_feature_time` must be `<= decision_time`).
The Phase-4 strategy populates `Signal.htf_feature_times`, `decision_time`,
`available_data_cutoff`, and `source_candle_timestamp` accordingly.

## 5. What this reuses (no new alignment code)

- `forex_bot.features.htf_align.align_last_completed` — backward-looking join.
- `forex_bot.features.htf_align.validate_signal_provenance` — post-hoc audit.
- `forex_bot.domain.candles.CandleFrame.completed_only` — completed-bar filter.
- `forex_bot.strategies.indicators.ema` — H4 / D1AGG EMAs.

The only new code (Phase 4) is the range-bar trigger + the thin H4/D1AGG trend
wrappers around `align_last_completed`; the alignment primitive itself is untouched.
