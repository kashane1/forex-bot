# CAMPAIGN_015 Pre-Commit — `failed_breakout_reversal 0.1.0-c015`

**Date:** 2026-05-25 · **Branch:** `research-failed-breakout-reversal-campaign-015`
`strategy_evidence: false`

Phase 0 binding pre-commit for **CAMPAIGN_015 /
`failed_breakout_reversal 0.1.0-c015`**. This pre-commit freezes the
hypothesis, the strategy rules, frozen parameters, fill timing, cost
treatment, financing treatment, walk-forward plan, gate vector,
anti-overfit gate vector, null comparison plan, Backtrader secondary-
lane plan, and BLOCKED conditions BEFORE any code in this sprint runs
generate_signal against real candles. The Phase 2 runner will
`_assert_frozen()` against the values below; any deviation aborts
before any backtest fires.

> **Maximum possible verdict for this sprint is `PASS_RESEARCH_SCREEN`
> ("candidate for human review"). No strategy is approved. Even a
> clean screen pass leaves `configs/approved_strategies.yaml` at
> `approved: []`. Paper / demo / live loops remain blocked. The
> research freeze, archive validator, approval registry, and live
> safety gates are not weakened by this sprint.**

CAMPAIGN_001 — CAMPAIGN_014 are historical evidence and remain
untouched.

## 1. Thesis (binding)

On H4 majors, range extremes are rejected more often than they
follow through. Instead of buying Donchian breakouts (CAMPAIGN_002 /
003 / 004 territory), this candidate **fades failed breakouts**: if
the current completed H4 bar sweeps past the prior 20-bar range
extreme by at least `0.10 * ATR(14)` and then closes back **inside**
that range, take the **reversal** trade at the **next bar's open**.

This is a single-leg, ATR-stopped, time-stopped counter-trend
hypothesis **conditional on a within-pair price statistic** (a
failed sweep of the prior 20-bar range). It is **not** an event-
conditional, regime-conditional, cross-pair, calendar, or session
hypothesis.

## 2. Why this is not a retune of CAMPAIGN_002 / 003 / 004 / 007 / 008 / 009 / 010 / 012 / 013 / 014

| campaign | family | direction | trigger | why C015 differs |
|---|---|---|---|---|
| 002 / 003 | trend_following (Donchian + EMA, +/- ADX gate) | with breakout | Donchian-N breakout close | C015 **fades** breakouts, opposite direction; requires close back **inside** range; ADX gate is `adx <= 20.0` not `adx >= X`. |
| 004 | volatility_breakout | with breakout | ATR-compression + Donchian breakout close | C015 has no compression requirement; opposite direction; requires the sweep to **fail** (close back inside). |
| 007 | pullback_continuation | with trend | EMA fast/slow regime + pullback band | C015 has no EMA regime filter; trades counter-trend on a single-bar sweep, not a multi-bar pullback. |
| 008 / 009 | mean_reversion | mean-revert | z-score + RSI + EMA regime + midline target | C015 uses range geometry (sweep + close-back-inside) not z-score; no midline target; time-stop only. |
| 010 | session_breakout (Asian-range / London open) | with breakout | session-time gate + prior Asian bar | C015 has no session gate; range is 20-bar Donchian, not single prior bar; fades the breakout. |
| 012 | regime_switcher_atr_percentile | regime-conditional | D1AGG ATR percentile regime gate + H4 direction | C015 has no D1 regime input and is not direction-conditional on regime; uses ADX-quiet gate only. |
| 013 | cross_pair_currency_strength_rotation | cross-pair | rank-gap between currencies | C015 is single-pair / single-leg, uses no cross-pair data. |
| 014 | calendar_event_window_anomaly | event-conditional | scheduled macro event + post-event H4 | C015 has no event calendar input; trades on any sweep-and-reject bar regardless of calendar. |

C015 is **the first sprint in this repo to test the failed-breakout
reversal hypothesis**. It is not a parameter sweep of any prior
candidate. Any deviation from §5 below constitutes a NEW candidate;
the runner will reject it.

## 3. Implementation files (committed by this sprint)

| file | role |
|---|---|
| `src/forex_bot/strategies/failed_breakout_reversal.py` | strategy module |
| `src/forex_bot/strategies/__init__.py` | re-export `FailedBreakoutReversalStrategy` |
| `src/forex_bot/config.py` | `FailedBreakoutReversalStrategyConfig` + `StrategyConfig` slot |
| `tests/unit/test_failed_breakout_reversal.py` | unit tests |
| `configs/campaign_015_failed_breakout_reversal.yaml` | research-only candidate config |
| `scripts/run_campaign_015.py` | walk-forward evidence runner |
| `tests/unit/test_run_campaign_015.py` | runner-contract tests |
| `research/backtrader_lane/strategies/campaign_015_failed_breakout_reversal.py` | Backtrader secondary-lane adapter |
| `tests/unit/backtrader_lane/test_campaign_015_failed_breakout_reversal.py` | adapter tests |
| `docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md` | this document |
| `docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_RESULT.md` | Phase 3 result (may be BLOCKED) |
| `docs/research/CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_DIAGNOSTICS.md` | Phase 4 diagnostics (may be BLOCKED) |
| `docs/research/BACKTRADER_CAMPAIGN_015_COMPARISON.md` | Phase 6 BT-vs-bespoke comparison (may be BLOCKED) |
| `docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_SUMMARY.md` | Phase 7 final handoff |

`configs/approved_strategies.yaml` is **not** modified by this sprint.

## 4. Strategy rules (binding, verbatim)

At the latest completed H4 bar `t`, using only **prior completed
bars** (`t-N..t-1`) to compute the range:

```
prior_high = max(high[t-20], ..., high[t-1])
prior_low  = min(low[t-20],  ..., low[t-1])
range_width = prior_high - prior_low
atr = ATR(14) at bar t (Wilder; consumes completed bars only)
adx = ADX(14) at bar t (Wilder; consumes completed bars only)
```

**Reject the setup** (no signal) if any of the following holds:

* `adx > 20.0`
* `range_width / atr < 1.25`
* `range_width / atr > 5.00`
* `atr` is missing / non-finite / `<= 0`
* `range_width <= 0`
* the current candle is incomplete (`candles.completed_only()` already
  enforces this in `ctx.candles`)
* spread / session / risk engine rejects the candidate (`RiskEngine`
  is the canonical gate)
* there is an existing open position in the instrument

**Short setup** (failed upside breakout):

* `high[t] > prior_high + 0.10 * atr` (the sweep)
* `close[t] < prior_high` (the rejection — close back inside range)
* `side = short`
* `stop = high[t] + 0.10 * atr` (beyond the sweep extreme)

**Long setup** (failed downside breakout):

* `low[t] < prior_low - 0.10 * atr` (the sweep)
* `close[t] > prior_low` (the rejection — close back inside range)
* `side = long`
* `stop = low[t] - 0.10 * atr` (beyond the sweep extreme)

If both setups would trigger in the same bar (pathological gap),
emit **no signal** — defense in depth.

**Stop-distance gate** (after computing `stop` against the next-bar-
open fill reference, which is `close[t]` for the strategy module's
diagnostic features; the bespoke engine uses the realized fill):

```
stop_distance_atr = abs(close[t] - stop) / atr
reject if stop_distance_atr < 0.80
reject if stop_distance_atr > 2.20
```

The strategy module computes `stop_distance_atr` using `close[t]` as
the diagnostic entry reference. The bespoke engine fills at
`open[t+1]`; any small drift between `close[t]` and `open[t+1]` is
absorbed by the gate's [0.80, 2.20] band.

**Entry timing.**

* Primary campaign evidence path: `next_bar_open` (i.e. the bespoke
  engine fills at the open of the bar following the signal bar).
* `signal_bar_close` is **not** part of the primary evidence path. It
  may appear as a non-gating diagnostic comparison only if the
  bespoke fill-timing model supports it safely.

**Exit.**

* Hard stop (long: `stop`, short: `stop`).
* Time stop: `max_bars_in_trade = 12` H4 bars.
* No midline target. No fixed take-profit. No trailing stop.
* Never widen stop.
* If a single bar both touches the stop and the time-stop boundary
  ambiguously, the **adverse stop wins** (`same_bar_adverse_stop_wins
  = true`).

## 5. Frozen parameters (binding; mirrors §4 verbatim)

| parameter | value | rationale / bounds |
|---|---|---|
| `version` | `0.1.0-c015` | binding string |
| `timeframe` | `H4` | matches CAMPAIGN_010 / 011 / 012 / 013 / 014 |
| `range_lookback` | `20` | Donchian-equivalent prior-bar range window |
| `atr_lookback` | `14` | Wilder, repo convention |
| `adx_lookback` | `14` | Wilder, repo convention |
| `adx_max` | `20.0` | ADX-quiet gate; `adx > 20.0` rejects |
| `sweep_buffer_atr` | `0.10` | minimum sweep distance beyond range, in ATR |
| `min_range_atr_multiple` | `1.25` | reject ranges that are too narrow vs ATR |
| `max_range_atr_multiple` | `5.00` | reject ranges that are too wide vs ATR |
| `stop_buffer_atr` | `0.10` | stop placed beyond the sweep extreme by this ATR fraction |
| `min_stop_atr_multiple` | `0.80` | reject if `stop_distance_atr < 0.80` |
| `max_stop_atr_multiple` | `2.20` | reject if `stop_distance_atr > 2.20` |
| `max_bars_in_trade` | `12` | hard time stop, H4 bars |
| `take_profit_r` | `null` | no fixed TP |
| `trailing_stop_atr_multiple` | `null` | no trailing |
| `entry_timing` | `next_bar_open` | primary evidence path |
| `same_bar_adverse_stop_wins` | `true` | binding ambiguity rule |
| `min_atr_pips` | `{}` | no per-pair floor in v1 |
| `risk.starting_equity_usd` | `500` | matches CAMPAIGN_010 / 011 / 012 / 013 / 014 |
| `risk.risk_per_trade_pct` | `0.25` | matches CAMPAIGN_010 / 011 / 012 / 013 / 014 |

**No sweep of any of these parameters.** Any deviation constitutes a
NEW candidate; the runner aborts before any backtest fires.

## 6. Universe + data + cost + financing

| dimension | value | source |
|---|---|---|
| universe | `EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD` (7 pairs) | matches CAMPAIGN_010 / 011 / 012 / 013 / 014 verbatim |
| timeframe | `H4` (4-hour) | same |
| data source | `oanda-practice` H4 candles from local SQLite store | identical hashes as CAMPAIGN_002 / 010 / 011 / 012 / 013 / 014 if local data present |
| network | **none** — read-only local SQLite | binding |
| broker / OANDA / LEAN | **none** — runner imports no broker, no OANDA SDK, no LEAN | binding |
| spread cost | base = `BacktestConfig.fixed_slippage_pips + spread_slippage_multiplier`; 2x-cost-stress = both doubled | runner CLI flag |
| slippage cost | same as spread cost | bundled |
| commission | from `BacktestConfig.commission_per_unit` (currently 0.0) | base + 2x |
| financing | **ESTIMATED only** — no MODELED financing in v1; `financing_treatment = "estimated"` in manifest | matches CAMPAIGN_014 financing posture |

**Financing posture is `ESTIMATED only`.** The candidate **cannot be
approved live** under this posture even with a screen-pass; that
requires a separate MODELED-financing sprint.

## 7. Walk-forward plan

* Splitter: existing `research.walk_forward` harness, `split_style =
  rolling`, `parameter_mode = frozen`, `strategy_evidence = false`.
* 8 folds.
* Train window: 540 days; validation window: 180 days; test window:
  180 days; step: 180 days.
* Universe start / end inherits from the existing plan-construction
  utility (matching CAMPAIGN_010 / 011 / 012 / 013 / 014 windows so
  the 2025-2026 lockbox discipline is preserved).
* The runner asserts the loaded plan has `parameter_mode == frozen`
  and `split_style == rolling` and `strategy_evidence == false`. Any
  deviation aborts.

## 8. Pass / fail gates (aggregate)

The runner emits a verdict from the bespoke engine alone, before any
null-baseline comparison or anti-overfit diagnostic. The richer
classification (PASS_RESEARCH_SCREEN / REJECT / BLOCKED) is applied
in Phase 3 result doc.

### 8.1 Aggregate base-cost gates (binding)

* aggregate closed trades **>= 200**
* aggregate closed trades **<= 800** (turnover budget)
* base-cost aggregate expectancy **>= +0.03 R**
* base-cost aggregate profit factor **>= 1.05**
* fold pass rate **>= 5 / 8**
* pairs positive **>= 4 / 7**
* no single pair contributes **> 70%** of gross positive R

### 8.2 Aggregate 2x-cost-stress gates (binding)

* 2x-cost-stress aggregate expectancy **>= 0.00 R**
* 2x-cost-stress aggregate profit factor **>= 1.00**

### 8.3 Per-fold sanity (advisory; not a hard reject by itself)

Per-fold reporting includes:

* fold trade count
* fold expectancy in R
* fold return % (sum of per-pair returns)
* fold pairs positive
* fold profit factor
* fold single-pair dominance %

A fold "passes" the per-fold sanity vector when:

* `trade_count >= 30`
* `expectancy_r >= 0.0`
* `pairs_positive >= 3`
* `single_pair_dominance_pct <= 60.0`

Fold pass rate = fraction of folds satisfying the per-fold sanity
vector. The aggregate gate `fold pass rate >= 5/8` consumes this.

### 8.4 Safety gates (binding)

* no broker / OANDA / LEAN imports in the runner
* `configs/approved_strategies.yaml` unchanged
* paper-loop / demo-loop still refuse every configured strategy
* archive validator passes; freeze checker passes; secret scanner passes
* fixture / event-calendar / external-API: **none used**

## 9. Anti-overfit gates (binding)

Applied in Phase 4 (`CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_DIAGNOSTICS.md`)
on top of the aggregate gates of §8:

* **LOO min mean gap vs matched null** `>= +0.05 R` (leave-one-out
  cross-validation: drop fold k, recompute aggregate expectancy on the
  remaining 7 folds, compare against the CAMPAIGN_011 sample-matched
  random-entry null for the same 7 folds; take the minimum across k).
* **t-stat of per-fold gap >= 2.0** (per-fold expectancy gap = C015
  fold expectancy − matched-null fold expectancy; t-stat = mean / (std
  / sqrt(N)) across the 8 folds).
* **median per-fold expectancy R >= 0.0**.
* **trade-level cumulative R > 0.0** (the running sum of per-trade R
  over all trades end-of-campaign is strictly positive).
* **pair concentration**: no single pair > 70% of gross positive R
  (already in §8.1; also reported in Phase 4).
* **fold contribution concentration**: no single fold > 60% of gross
  positive R.
* **cost dominance**: `total_estimated_costs_r / |total_gross_r| <=
  0.50` (costs do not dominate gross R).

If any anti-overfit gate fails, the strategy is classified
`ABOVE_NULL_BUT_FRAGILE` or worse — see §11.

## 10. Null comparison plan (binding)

The null model is `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011),
already an evidence-grade null with the same 7-pair / H4 / 8-fold
plan and same data store. The Phase 4 comparison:

* Loads the CAMPAIGN_011 fold-level expectancy series (per fold, per
  pair, aggregate) from `backtests/CAMPAIGN_011_random_entry_anchor/`.
* Builds the sample-matched comparison: same fold indexes, same
  pairs, same data window.
* Computes:
  * gap vs null in R (campaign mean − null mean, aggregate);
  * null per-fold standard deviation across the 8 folds;
  * **LOO min mean gap** (§9 definition);
  * **per-fold t-stat** (§9 definition);
  * **median per-fold expectancy R** of the campaign (not the gap);
  * **trade-level cumulative R** (signed running sum of campaign R);
  * pair-concentration and fold-concentration of campaign gross R.

The CAMPAIGN_011 null is **not** itself a trading candidate; this is
a comparator. The Phase 4 doc must not modify CAMPAIGN_011 evidence.

## 11. Phase 4 diagnostic classifier (binding labels)

The Phase 4 diagnostics classifier emits exactly one of:

* `ROBUST_ABOVE_NULL` — all aggregate gates of §8 pass AND all anti-
  overfit gates of §9 pass AND the campaign sits outside the null
  band on at least 3 of {expectancy, PF, return %, pairs positive}.
* `ABOVE_NULL_BUT_FRAGILE` — aggregate gates of §8 pass but at least
  one anti-overfit gate of §9 fails (e.g. LOO min gap < +0.05 R; or
  per-fold t-stat < 2.0; or pair concentration > 70%; or cost
  dominance > 0.50).
* `SELECTED_CELL_ARTIFACT` — at most one pair drives the entire
  positive R; or at most one fold drives the entire positive R; or
  removing the top pair or top fold collapses the campaign below the
  null. Diagnostic-only; never an approval path.
* `WITHIN_NULL` — the aggregate metrics sit inside the
  CAMPAIGN_011 null band on every axis (expectancy gap within the
  null per-fold std band; PF within 0.95-1.05; return % within ±2%
  vs null; pairs positive within ±1 of null).
* `WORSE_THAN_NULL` — campaign aggregate metrics are materially
  worse than CAMPAIGN_011 on every binding axis (direction-of-trade
  falsification).
* `BLOCKED` — data missing, runner refused, or anti-overfit
  diagnostic could not be computed (e.g. < 3 folds with non-zero
  trades).

## 12. Backtrader secondary-lane plan (binding)

The Backtrader lane is the local verification lane and **cannot
approve anything**. It exists only to corroborate the bespoke
engine's signal logic and exit behavior on the same input candles.

* Adapter: `research/backtrader_lane/strategies/campaign_015_failed_breakout_reversal.py`.
* Data adapter: existing `research/backtrader_lane/...` local data
  adapter only. **No Backtrader broker / OANDA / LEAN integration.**
* Same frozen rules of §4:
  * prior 20-bar range (`prior_high` / `prior_low` from completed
    bars before the signal bar);
  * `adx <= 20.0`;
  * sweep buffer `0.10 * ATR`;
  * stop buffer `0.10 * ATR` beyond sweep extreme;
  * 12-bar time stop or hard stop;
  * next-bar-open primary fill if feasible in the BT lane.
* If Backtrader cannot replicate next-bar-open semantics cleanly,
  document the approximation in
  `BACKTRADER_CAMPAIGN_015_COMPARISON.md` and classify it as
  `FILL_TIMING_APPROXIMATION`, not a bug.
* If local Backtrader data is absent, emit a BLOCKED artifact and
  stop cleanly.

## 13. BLOCKED conditions (binding)

The runner emits a valid BLOCKED artifact (and stops cleanly) if any
of:

* the configured `database_path` (default `./data/campaign_002.sqlite3`)
  does not exist;
* the database exists but has no `H4` candles for at least one of the
  7 pairs;
* the recorded data source is not `oanda-practice` for at least one of
  the 7 pairs (the runner only honors the binding source);
* a fold's test window has zero local candles for at least one pair;
* the `RiskEngine` cannot be constructed from the loaded settings.

Phase 4 emits `BLOCKED` if Phase 3 emitted `BLOCKED`, or if fewer than
3 folds have non-zero trades.

Phase 5 / 6 emit `BLOCKED` (in their adapter / comparison artifacts)
if local Backtrader data is absent or bespoke `walk_forward/results.json`
is absent.

A BLOCKED artifact is a legitimate sprint outcome. **Do not fabricate
results to avoid BLOCKED. Do not promote BLOCKED to PASS.**

## 14. Safety invariants (binding; verified by Phase 0 + Phase 7)

* `configs/approved_strategies.yaml` remains `approved: []`.
* `STRATEGY_STATUS.md` records every campaign as `paper: NO · demo: NO
  · live: NO`.
* `failed_breakout_reversal` is **not** added to
  `configs/approved_strategies.yaml`.
* Paper-loop and demo-loop continue to refuse every configured
  strategy (verified by `scripts/check_research_freeze.py`).
* `validate_research_archive.py` passes (no manifest / report drift).
* `scan_artifacts_for_secrets.py` passes (no committed credentials).
* No broker order is submitted, modified, cancelled, or closed by
  any code path in this sprint.
* OANDA live credentials are not used. OANDA practice credentials
  are not used by Phase 1-7 (no network call). The local SQLite
  store is read-only; no rehydrate is performed by this sprint's
  runner.
* No LEAN / QuantConnect integration is added.
* The bespoke engine and the Backtrader lane are independent;
  neither is changed to match the other.
* No tuning of `failed_breakout_reversal` parameters after seeing any
  CAMPAIGN_015 result.

## 15. Pre-commit baseline state (verbatim)

Before the Phase 0 commit:

* `git status`: clean on the dedicated branch
  `research-failed-breakout-reversal-campaign-015`.
* `pytest tests/ -q`: **1364 passed**.
* `ruff check src tests scripts research`: 3 pre-existing RUF100
  errors in `research/lean_parity/algorithms/campaign_002_h4_baseline/
  main.py`; identical on `main`; not part of this sprint to fix
  (LEAN is retired).
* `python scripts/check_research_freeze.py`: **ALL CHECKS PASSED**.
* `python scripts/validate_research_archive.py`: **ALL CHECKS PASSED**.
* `python scripts/scan_artifacts_for_secrets.py`: **PASSED** (pattern
  scan only — no live `.env` sourced; binding posture for the sprint).
* `configs/approved_strategies.yaml`: `approved: []` (verified
  textually).
* `failed_breakout_reversal` is not in the strategy registry; the
  strategy module does not exist yet. This pre-commit document is
  the first artifact of the sprint.

## 16. Verdict ceiling (binding)

> The maximum possible verdict for CAMPAIGN_015 is
> **`PASS_RESEARCH_SCREEN`** ("candidate for human review"). It is
> **not** an approval path. Even on `PASS_RESEARCH_SCREEN`:
>
> * `configs/approved_strategies.yaml` remains `approved: []`;
> * paper / demo / live loops remain blocked;
> * `STRATEGY_STATUS.md` lists the candidate as `research-only`;
> * MODELED financing is still required before any live-promotion
>   conversation;
> * an independent secondary lane (Backtrader) must corroborate the
>   signal logic OR be classified as a transparent approximation
>   (`FILL_TIMING_APPROXIMATION`), and the corroboration result is
>   documented in `BACKTRADER_CAMPAIGN_015_COMPARISON.md`.
>
> Approval (i.e. adding the name to `configs/approved_strategies.yaml`)
> is a separate, deliberate human action requiring a fresh and
> distinct sprint, and is explicitly out of scope here.

---

_Signed-off pre-commit. Any deviation from §4–§14 in this sprint's
later phases must amend this document by a new dated revision (not a
silent edit). The Phase 2 runner asserts §5 verbatim._
