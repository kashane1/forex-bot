# CAMPAIGN_029 — Backtrader / execution-parity design (design only)

**Strategy:** `usdjpy_range_bar_mtf_breakout 0.1.0-c029`
**Status:** `SCAFFOLD_ONLY / NOT_RUN / NOT_APPROVED`
**Companions:** `CAMPAIGN_029_PRECOMMIT_SCOPE.md`, `CAMPAIGN_029_HTF_ALIGNMENT_DESIGN.md`

> **Design only.** No parity harness is built in this sprint. This documents
> whether/how a Backtrader cross-check could represent **range bars**, the parity
> risks unique to event-driven bars, and the **minimum parity bar** that the
> future execution sprint must clear before any promotion-bound evidence
> (precommit gate §10.8). Full parity is **not** implemented now because it is
> neither cheap nor clearly scoped for an irregular-time bar feed.

---

## 1. Can Backtrader represent range bars directly?

**Not natively, and not safely as the system of record.** Backtrader is an
event-driven engine that steps **one OHLC bar at a time**. It does not require
fixed time intervals — a custom `bt.feeds.PandasData` feed accepts arbitrary
`datetime`-indexed OHLC rows — so a **precomputed** range-bar series *can* be fed
in. But two things break naive parity:

1. **Intrabar dynamics are gone.** A 10-pip range bar is already an *aggregate* of
   many M1 rows (preflight: mean 25, max 1363 M1 rows/bar). Its OHLC compresses a
   path Backtrader cannot see. Any fill/stop logic Backtrader runs *on the range
   bar's own High/Low* is therefore a coarse approximation of what happened on the
   underlying M1 tape.
2. **Irregular timestamps confuse time-based machinery.** Backtrader analyzers,
   sessions, and resampling assume roughly regular bars; range bars span 1 min to
   ~3 days. Anything time-derived inside Backtrader must be disabled or driven by
   the bar's own `close_time`, not inferred.

**Decision:** range bars are **precomputed** by `non_time_bars.build_range_bars`
(the lab's deterministic, lookahead-free builder — already the system of record)
and **fed to Backtrader as a synthetic OHLC feed** purely as an *independent
re-implementation cross-check of the decision logic*, never as a more-authoritative
execution model.

## 2. The right parity target (frozen intent)

The promotion-bound evidence engine for C029 should resolve **fills and stops on
the underlying M1**, not on the range bar's compressed OHLC:

- **Entry:** at the **open of the next completed range bar** (`next_bar_open`) —
  i.e. the first M1 mid open after the trigger bar's `close_time`. Unambiguous and
  identical in both engines.
- **Stop / time exit:** walked forward on **M1** (or on subsequent range bars whose
  High/Low bound the M1 path) so an intrabar stop touch is detected at the right
  bar, matching `resolve_exit`'s priority `stop → time → end_of_data`.

Backtrader parity then checks that the **bespoke engine and a Backtrader
re-implementation agree** on entries, exit reasons, and per-trade R within
tolerance — it is a second pair of eyes on the rules, not a different cost/fill
philosophy.

## 3. How the signal/entry/exit maps to Backtrader

| element | bespoke engine | Backtrader representation |
|---------|----------------|---------------------------|
| execution bar | `RangeBar` (precomputed) | `PandasData` row (synthetic OHLC, `datetime=close_time`) |
| H4 / D1AGG context | `align_last_completed` at `close_time` | precomputed per-range-bar context columns joined **before** the run (no in-engine HTF resample) |
| trigger | pullback-reclaim + overshoot guard | identical boolean precomputed; Backtrader only acts on it |
| entry | next range-bar open | `cheat_on_open=False`; order submitted on trigger bar, filled next bar's open |
| stop | `max(5-bar swing, 20pip floor)` | `StopOrder` at the same price; **but** evaluated on M1 (see §5) |
| time stop | 12 range bars | bar counter since entry |
| exit priority | `stop → time → end_of_data` | enforced by explicit ordering in `next()` |

To remove HTF resampling as a parity variable, **all HTF context and the trigger
boolean are precomputed** and carried as extra feed columns; Backtrader consumes
them rather than recomputing EMAs/alignment. This isolates the parity test to
*entry/stop/exit accounting*.

## 4. Cost model

Conservative, financing-inclusive, identical constants in both engines: fixed
slippage `0.2 pip`, spread-slippage multiplier `0.5`, commission `0.0` (see the
campaign config `backtest:` block). Cost must be applied at the **same** event
(entry fill and exit fill) in both engines. The spread / 10-pip-range ratio must
be reported (precommit gate §10.7).

## 5. Known parity risks (range-bar specific)

1. **Intrabar stop resolution.** If Backtrader checks the stop on the *range bar's*
   High/Low, a stop inside the bar is detected one bar late vs an M1 walk. **Mitigation:**
   resolve stops on M1 in both engines, or feed a finer bar for the holding window.
2. **Bar that both triggers and would stop.** A violent bar can cross the entry and
   the stop within one range bar. The `next_bar_open` rule already defers entry, and
   the anti-spike overshoot guard rejects multi-threshold trigger bars — but the
   parity harness must confirm both engines agree on these edge bars.
3. **Weekend-gap bars.** 261 bars span >1 day (preflight). The next-bar-open entry
   timestamp and any time-based cost (financing) must be handled identically.
4. **Incomplete final bar.** Never traded in either engine; the parity harness must
   drop it identically.
5. **Float vs Decimal.** The builder uses `Decimal` internally and exposes `float`
   OHLC; Backtrader is float-only. Parity tolerance must absorb this.

## 6. Minimum parity bar before promotion-bound evidence (frozen)

Before any C029 result may be classified `PROMOTION_REVIEW_REQUIRED`:

1. A Backtrader re-implementation reproduces the bespoke engine's **entries**
   (same trigger bars), **exit reasons**, and **per-trade R** on the **train**
   window within tolerance: **trade-count exact**, **exit-reason match ≥ 99%**,
   **mean per-trade R within ±0.02R**.
2. Any discrepancy is explained (not silently averaged away).
3. Parity is demonstrated on the **train/validation** windows only; the **test
   lockbox stays closed** until the train/validation gates *and* this parity bar
   both pass.

## 7. Scope statement

This sprint writes **only** this design. It builds no Backtrader feed, runs no
parity comparison, and produces no evidence. Implementing the parity harness is
work for `research-campaign-029-usdjpy-range-bar-execution-001`.
