# Backtrader vs Bespoke Comparison — CAMPAIGN_015

> **SUPERSEDED / STALE DUE TO DUPLICATE-CANDLE CONTAMINATION** — see
> [`BACKTRADER_CAMPAIGN_015_DEDUPED_COMPARISON.md`](BACKTRADER_CAMPAIGN_015_DEDUPED_COMPARISON.md).

**Date:** 2026-05-25 · **Branch:** `research-failed-breakout-reversal-campaign-015`
**Divergence classification:** `BLOCKED`

> **No strategy approved.** `configs/approved_strategies.yaml` remains
> `approved: []`. The Backtrader lane is a **secondary verification
> lane**; it cannot approve any strategy under any verdict.

## 1. Outcome

The Phase 6 BT-vs-bespoke comparison is **`BLOCKED`** by direct
inheritance from Phase 3
([`CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_RESULT.md`](CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_RESULT.md)
§1) and Phase 5 BT data availability:

* **No bespoke run output:** the bespoke walk-forward did not execute
  because the canonical local `data/campaign_002.sqlite3` is absent in
  this worktree. There is no `backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/results.json`
  with per-fold trades to compare against.
* **No Backtrader run output:** the Backtrader adapter requires the
  same local OANDA practice H4 store (or an equivalent
  `CandleAdapterResult` produced from that store) to run on the
  walk-forward universe; that store is absent.

Both engines were given identical scaffolding (committed strategy
modules + tests + runner; identical frozen parameters); neither was
fed real data. There is no per-pair trade list on either side, hence
no comparison.

## 2. What is **not** in this document

Per Phase 0 §6 and §13 BLOCKED-conditions:

* No trade count comparison.
* No per-pair trade-count comparison.
* No side distribution comparison.
* No average R comparison.
* No return % comparison.
* No max-drawdown comparison.
* No exit-reason distribution comparison.
* No timing-divergence chart.
* No fabricated numbers, no synthetic substitution, no proxy data.

## 3. Divergence-class library (binding label set; Phase 0 §6)

The classifier that would consume real BT + bespoke run outputs emits
exactly one of:

| label | meaning |
|---|---|
| `PASS` | per-pair trade count + side + average R + return % within tolerance; exit-reason histogram aligned |
| `TOLERABLE_DRIFT` | small per-pair drift (e.g. ±1 trade per pair, R within 0.05) within the published BT lane drift tolerance |
| `DATA_MISMATCH` | the two engines were not driven by byte-identical H4 candles |
| `TIMESTAMP_MISMATCH` | candle timestamps differ across the two lanes |
| `SIGNAL_RULE_MISMATCH` | trade list reveals a divergence in the entry-rule R1-R10 implementation |
| `FILL_TIMING_MISMATCH` | divergence traceable to the BT lane's `next_bar_open` approximation (Phase 5 metadata flag `FILL_TIMING_APPROXIMATION`) |
| `STOP_OR_TIME_EXIT_MISMATCH` | divergence in hard-stop or 12-bar time-stop firing |
| `SIZING_OR_PNL_MISMATCH` | divergence in unit-sizing or R-formula |
| `BLOCKED` | one or both sides did not produce a runnable trade list (this sprint) |

## 4. Backtrader-side approximation flags (Phase 5; verbatim)

For documentation continuity, the BT adapter's published approximations
are repeated here:

* `FILL_TIMING_APPROXIMATION` — next-bar-open fill emulated via a
  `_pending_side` queue on the signal bar; entry executes at the open
  of the bar after signal. Minor microstructure drift expected.
* `RANGE_PRIOR_BARS_ONLY` — prior_high / prior_low read from
  `self.data.high[-offset]` (offsets 1..N), matching the bespoke
  `.iloc[-(N+1):-1]` window exactly.
* `ADX_AND_ATR_CURRENT_BAR` — ADX / ATR read at the current bar,
  matching `adx_series.iloc[-1]` / `atr_series.iloc[-1]`.
* `ADVERSE_STOP_WINS` — same-bar adverse-stop rule active on entry
  bar (long: `bar_low <= stop`; short: `bar_high >= stop`).
* `NO_TRAILING_STOP` — only hard stop + 12-bar time stop; no
  take-profit, no trailing.
* `BACKTRADER_BROKER_BYPASSED` — Cerebro broker not used for fills.
* `MANUAL_SIZING_RISK_FRACTION` — 0.25% of compounding NAV, whole
  units floor.
* `NO_FINANCING` — financing/swap not modeled on either engine.

If a real-data run produces a divergence, the comparison classifier
must check whether the divergence is attributable to one of the
above-published approximations before labeling it a bug.

## 5. Reproduction (when data becomes available)

A future sprint that has the canonical local data:

```
# Bespoke side:
OANDA_ACCOUNT_ID_PRACTICE=test \
OANDA_ACCESS_TOKEN_PRACTICE=test \
python scripts/run_campaign_015.py \
  --config configs/campaign_015_failed_breakout_reversal.yaml \
  --out backtests/CAMPAIGN_015_failed_breakout_reversal

# Backtrader side:
python scripts/run_backtrader_parity.py --campaign CAMPAIGN_015 \
  --output backtests/CAMPAIGN_015_failed_breakout_reversal/backtrader

# Comparison:
python scripts/compare_backtrader_parity.py \
  --campaign CAMPAIGN_015 \
  --bespoke-trades backtests/CAMPAIGN_015_failed_breakout_reversal/folds/base \
  --bt-trades   backtests/CAMPAIGN_015_failed_breakout_reversal/backtrader \
  --output      docs/research/BACKTRADER_CAMPAIGN_015_COMPARISON.md
```

(The `run_backtrader_parity.py --campaign CAMPAIGN_015` and
`compare_backtrader_parity.py --campaign CAMPAIGN_015` arguments
register automatically on import because the CAMPAIGN_015 adapter
is registered in `research/backtrader_lane/strategies/__init__.py`.)

## 6. Safety invariants

| invariant | state |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (byte-stable) |
| `failed_breakout_reversal` in registry | **No** |
| Bespoke engine modified to match Backtrader | **No** |
| Backtrader adapter modified to match bespoke | **No** |
| Strategy parameters tuned after seeing results | **No** (no results to see) |
| Phase 3 bespoke verdict (BLOCKED) overridden | **No** |
| BT lane claims approval authority | **No** (it never can) |
| CAMPAIGN_001-014 evidence mutated | **No** |

## 7. Disposition

* Phase 6 verdict: `BLOCKED` (inherited from Phase 3 + Phase 5 BT
  data availability).
* No tuning. No bug declared on either side (neither side ran).
* The comparison harness's published label set is committed and
  ready: a future sprint may re-run both lanes against the canonical
  local store and produce a non-BLOCKED divergence classification.
* Even a `PASS` divergence classification at that future point would
  remain bounded by Phase 0 §16: the maximum verdict for the
  candidate is `PASS_RESEARCH_SCREEN`, not approval.
