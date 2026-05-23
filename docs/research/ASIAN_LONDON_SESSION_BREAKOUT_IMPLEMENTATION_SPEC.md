# Asian/London Session Breakout — Implementation Spec

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-001`
`strategy_evidence: false`

Machine-facing implementation spec that translates
[`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
into precise, executable rules for Phase 2 code, Phase 3 tests,
and Phase 4 research config. **This document does not approve the
strategy and does not authorize a campaign run.** Every artifact
emitted under this spec carries `strategy_evidence: false`.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. CAMPAIGN_010 is candidate scaffold
> only.

## 1. Candidate identity

| field | value |
|---|---|
| strategy name (class `name`) | `session_breakout` |
| strategy version (class `version`) | `0.1.0-c010` |
| campaign label | `CAMPAIGN_010` |
| sprint label | `research-asian-london-session-breakout-001` |
| protocol category | Session-of-day breakout (non-CAMPAIGN_004 flavour) |

## 2. Rule table (verbatim)

At the latest **completed** H4 bar `t` taken from
`ctx.candles.completed_only().df`, the strategy applies the
following rules in order. **Any failed rule returns `None`
(no signal).** All rules use only `t`'s `close` and bar `t-1`'s
high/low/ATR-14; no other feature of bar `t`'s OHLC is used.

| # | rule | inputs | failure → `None` |
|---:|---|---|---|
| R1 | sufficient warm-up | `len(df) >= atr_lookback + 2` | yes |
| R2 | no open position on this instrument | `ctx.open_positions` | yes (mirrors `TrendFollowingStrategy.generate_signal` lines 82–84) |
| R3 | bar `t` is in the London window | `df.index[-1].tz_convert('UTC').hour in london_window` | yes |
| R4 | bar `t-1` is in the Asian window | `df.index[-2].tz_convert('UTC').hour in asian_window` | yes |
| R5 | bar `t-1` high/low/ATR-14 all finite | `not NaN` for each | yes |
| R6 | Asian range gate | `range_prev >= min_asian_range_atr_fraction * atr_prev` where `range_prev = high[t-1] - low[t-1]` and `atr_prev = atr_14.iloc[-2]` | yes |
| R7 | direction | `close[t] > high[t-1]` → `long`; `close[t] < low[t-1]` → `short`; equal → `None` | yes |
| R8 | optional min_atr_pips floor | `atr_prev / pip_size >= min_atr_pips_by_pair.get(instrument, 0)` | yes (default 0 → never trips) |
| R9 | stop sign check | for `long`: `stop = close[t] - atr_stop_multiple * atr_prev`; for `short`: `stop = close[t] + atr_stop_multiple * atr_prev`; verify `stop != close[t]` | no signal if `atr_prev == 0` (would yield zero-distance stop — fail closed) |
| R10 | round stop price | `instrument.round_price(Decimal(str(stop)))` | n/a |
| R11 | emit `Signal` | populated `Signal(name, version, instrument, timeframe, timestamp=UTC, side, entry_intent='market', stop_model, stop_price, exit_model, features, reason, signal_id)` | n/a |

## 3. Session window definitions

UTC hour-of-day at bar **open** timestamp (`df.index[-1].hour`
after `.tz_convert('UTC')`).

### 3.1 Half-open intervals

The convention is **half-open `[start, end)`**: the bar at exactly
`start` hour is inside the window; the bar at exactly `end` hour
is outside.

### 3.2 Asian window (wraps midnight)

```python
def in_asian(hour: int, start: int = 22, end: int = 6) -> bool:
    # Wraps midnight when start > end.
    if start > end:
        return hour >= start or hour < end
    return start <= hour < end
```

With `start=22, end=6`: hours `{22, 23, 0, 1, 2, 3, 4, 5}` are
Asian.

### 3.3 London window (does not wrap)

```python
def in_london(hour: int, start: int = 6, end: int = 12) -> bool:
    return start <= hour < end
```

With `start=6, end=12`: hours `{6, 7, 8, 9, 10, 11}` are London.

### 3.4 H4 bar boundary mapping (informational)

H4 bars use the project's `daily_alignment=17` NY convention.
NY → UTC mapping varies with DST:

| NY offset | UTC bar starts |
|---|---|
| NY standard (winter) UTC−5 | `22, 02, 06, 10, 14, 18` |
| NY DST (summer) UTC−4 | `21, 01, 05, 09, 13, 17` |

Under winter alignment:

| bar UTC start | hour | window | role in candidate |
|---|---:|---|---|
| 22 | 22 | Asian | Asian, "t-2" |
| 02 | 2 | Asian | Asian, **t-1** for the morning London bar |
| **06** | **6** | **London** | **t** — first London bar; eligible for signal |
| 10 | 10 | London | second London bar (its t-1 is also London → R4 fails → no signal) |
| 14 | 14 | NY overlap | not eligible |
| 18 | 18 | NY late | not eligible |

Under DST (summer) alignment:

| bar UTC start | hour | window | role |
|---|---:|---|---|
| 21 | 21 | not Asian (21 < 22) | inert |
| 01 | 1 | Asian | t-1 candidate (for the *next* bar) |
| 05 | 5 | Asian | the bar that *would* be the "London open" in NY-DST falls in the Asian window per UTC hours — so **no signal during DST under v1**. |
| 09 | 9 | London | t (its t-1 is the 05-UTC bar = Asian) → eligible for signal |
| 13 | 13 | NY overlap | not eligible |
| 17 | 17 | NY late | not eligible |

**Known v1 limitation (DST):** the candidate generates **one**
candidate London signal per day under each alignment. Under
NY-DST (~26 weeks/year), the eligible London bar starts at 09:00
UTC (with t-1 at 05:00 UTC). Under NY-standard (~26 weeks/year),
it starts at 06:00 UTC (with t-1 at 02:00 UTC). The structural
firing-rate sketch in
[`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
§13 (~5 opportunities × 7 pairs / day) projects **one
opportunity per pair per trading day** assuming one eligible
London bar per day across both alignments, which holds under the
mapping above. Phase 5 smoke + Phase 6 dry-run will confirm.

## 4. Frozen parameter table

| param | type | frozen value | rationale (from design) |
|---|---|---|---|
| `version` | `str` | `"0.1.0-c010"` | candidate version pin |
| `timeframe` | `Literal["H1","H4","D"]` | `"H4"` | primary timeframe |
| `atr_lookback` | `int` | `14` | standard Wilder ATR |
| `atr_stop_multiple` | `float` | `2.0` | same value used by CAMPAIGN_004 / CAMPAIGN_007 |
| `trailing_stop_atr_multiple` | `float \| None` | `None` | v1 has no trailing stop |
| `max_bars_in_trade` | `int` | `6` | maps to the design's `time_stop_bars` ≈ 1 trading day on H4 |
| `min_atr_pips` | `dict[str, float]` | `{}` | no per-pair ATR floor in v1 |
| `asian_session_hours_utc_start` | `int` | `22` | covers late-NY-late + Asian on UTC |
| `asian_session_hours_utc_end` | `int` | `6` | 8 hours of low-liquidity bar coverage |
| `london_session_hours_utc_start` | `int` | `6` | first London hours on UTC |
| `london_session_hours_utc_end` | `int` | `12` | 6-hour London-only window before NY overlap |
| `min_asian_range_atr_fraction` | `float` | `0.30` | the Asian-bar range must be ≥ 30 % of ATR-14 |

**RiskConfig** fields (set in the campaign YAML, not in the
strategy config):

| param | value | rationale |
|---|---|---|
| `risk_per_trade_pct` | `0.25` | matches every prior campaign |
| `max_positions_per_instrument` | `1` | hard prohibition; mirrors all prior campaigns |

### 4.1 Name mapping: design's `time_stop_bars` ↔ config's `max_bars_in_trade`

The design (Phase B4 §3) names the time-stop parameter
`time_stop_bars`. The existing repo convention
([`config.py`](../../src/forex_bot/config.py)
`TrendFollowingStrategyConfig.max_bars_in_trade`) names it
`max_bars_in_trade`. **The implementation uses
`max_bars_in_trade`** (existing convention) and records this
rename in `CAMPAIGN_010_PRECOMMIT_CHECKLIST.md` so the future
walk-forward sprint can cite the design + spec verbatim.

## 5. No-lookahead rules (binding)

| rule | enforcement |
|---|---|
| Use `df = ctx.candles.completed_only().df` only — never the raw `ctx.candles.df`. | code review + Phase 3 test |
| At bar `t`, only `close[t]` is consulted; `high[t]`, `low[t]`, `open[t]`, `volume[t]` are **forbidden** as features of the entry rule. | Phase 3 grep test |
| `atr_14` is computed once over the full series; the value at index `-2` is used (ATR as of bar `t-1`). | Phase 3 unit test pinning the index |
| No `.shift(-N)` for `N > 0`. | Phase 3 grep test |
| No `range(0, ...)` slicing into future bars. | Phase 3 grep test |
| No `df.iloc[t+...]` access. | structural |
| The strategy module imports nothing from `forex_bot.broker`. | Phase 3 grep test |
| Asian-range gate uses `high.iloc[-2]`, `low.iloc[-2]` only — bar `t-1`'s OHLC, not bar `t`'s. | code review + Phase 3 test |

## 6. Session boundary handling

| edge case | handling |
|---|---|
| Bar at exactly `asian_start` hour | inside Asian (`>=` half-open) |
| Bar at exactly `asian_end` hour | outside Asian (`<` half-open) |
| Bar at exactly `london_start` hour | inside London (`>=` half-open) |
| Bar at exactly `london_end` hour | outside London (`<` half-open) |
| `asian_start > asian_end` (midnight wrap) | special-cased in `in_asian()` helper |
| `asian_start == asian_end` | always-false (`raise` at config validation) |
| `london_start >= london_end` | always-false / invalid (`raise` at config validation) |
| Timezone-naive timestamp | invalid; rely on `CandleFrame` invariant that bars are UTC-aware (existing data contract); strategy does not silently coerce |
| Series shorter than 2 bars | `R1` short-circuits to `None` |
| `df.index[-2]` not finite (NaN ATR / missing OHLC) | `R5` short-circuits to `None` |
| Non-monotonic timestamps | strategy does not detect; this is a `CandleFrame` contract (existing data validator); a Phase 3 test asserts strategy behaviour is undefined and recommends upstream validation |

## 7. H4 / intraday limitation risks

| risk | mitigation |
|---|---|
| DST shifts the eligible London bar start hour (see §3.4) | documented; signal generated under both alignments; Phase 5 smoke counts opportunities-per-pair as a sanity check |
| Holiday H4 bars (no London session on bank holidays) | not detected by the strategy; the gate `R6` (Asian range size) will tend to under-fire on holidays naturally because liquidity is lower, but no explicit holiday calendar is consulted (consistent with the rest of the project — no holiday calendar is used anywhere in `src/forex_bot/`) |
| Pre-news widening of spreads in the London window | not detected by the strategy; the existing `RiskEngine.evaluate(mode='backtest')` applies `SpreadFilterConfig.max_spread_pips` and may reject the signal there |
| Single-bar Asian-range definition is brittle for instruments with sparse Asian volume (e.g. USD_JPY) | accepted as a v1 simplification; the design's distinctness requirement was satisfied without compounding indicator complexity |

## 8. Data assumptions

| assumption | source / verification |
|---|---|
| H4 bar timestamps are tz-aware UTC on `df.index` | `CandleFrame.from_candles(...)` contract; existing strategies rely on the same |
| `df["close"], df["high"], df["low"]` are `pd.Series[float]` | existing strategy modules |
| `df["close"].iloc[-1]` is the latest completed bar's close | `CandleFrame.completed_only()` invariant |
| Pip size lives on `ctx.instrument.pip_size` (`Decimal`) | `Instrument` model |
| `ctx.instrument.round_price(Decimal)` returns a rounded `Decimal` | `Instrument` model |
| 7-pair universe candles available in local SQLite | per [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md) §6 |

## 9. Risk interface assumptions (no edits)

The strategy never sizes the position. It emits a `Signal` with:

- `side`, `entry_intent="market"`, `stop_price` (rounded
  `Decimal`), `stop_model = f"ATR{atr_lookback}*{atr_stop_multiple}"`,
- `exit_model = "time_stop_only"` (no trailing stop; no TP),
- `features` dict with `prior_high`, `prior_low`, `prior_range`,
  `prior_atr`, `last_close`, `range_fraction`, `prior_hour_utc`,
  `current_hour_utc`,
- `reason` string for the audit trail.

The existing `BacktestEngine` + `RiskEngine.evaluate(mode="backtest")`
path turns the signal into an order (sized at 0.25 % equity per
trade with the campaign YAML's `risk` block) and applies the
existing gates verbatim (spread cap, session blackout if
configured, daily/weekly loss limits, exposure cap,
`max_positions_per_instrument=1`, margin, hard prohibitions). No
new gate is added; no `RiskEngine` change is required.

## 10. Financing overlay assumptions

Per [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
§10.1 Option 1:

- The candidate's first walk-forward run uses
  `research.financing.default_stress_rate_source()` for the full
  universe (flat conservative debit-on-both-sides per pair).
- Per-pair `TableRateSource` overlays are emitted as a
  diagnostic sidecar using the committed two-week
  `rates_two_week_*.json` fixtures (sample only, not full window).
- `financing_treatment = "estimated"`; `MODELED` is refused at
  all four pipeline layers and remains unavailable.
- The strategy module **does not** import from
  `research.financing`; the financing overlay is applied
  *post-hoc* by the campaign code (future sprint).

## 11. Walk-forward overlay assumptions

The strategy is structurally compatible with the existing
harness:

- emits `Signal | None` per bar — exactly what the bespoke
  `BacktestEngine` consumes;
- has a deterministic `signal_id` (SHA1 over name/version/
  instrument/timeframe/timestamp/side) — supports
  reproducibility checks;
- uses `parameter_mode="frozen"` only (the only authorized
  mode);
- needs no new adapter; the future walk-forward sprint can call
  `rolling_window_plan(...)` per
  [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
  §7.

## 12. Expected test cases (Phase 3 contract)

The Phase 3 suite (`tests/unit/test_session_breakout.py`) must
include at least the following ≥ 18 cases; each is named and
listed here so Phase 3 can match the spec.

| # | test name | what it covers |
|---:|---|---|
| 1 | `test_warmup_returns_none_when_too_few_bars` | R1 |
| 2 | `test_no_signal_when_open_position_present` | R2 |
| 3 | `test_no_signal_when_bar_t_not_in_london_window` | R3 |
| 4 | `test_no_signal_when_bar_tminus1_not_in_asian_window` | R4 |
| 5 | `test_no_signal_when_atr_is_nan` | R5 |
| 6 | `test_no_signal_when_asian_range_below_fraction_gate` | R6 |
| 7 | `test_long_signal_when_close_above_prior_high_and_gate_met` | R7 long |
| 8 | `test_short_signal_when_close_below_prior_low_and_gate_met` | R7 short |
| 9 | `test_no_signal_when_close_equals_prior_high_or_low` | R7 tie |
| 10 | `test_no_signal_when_prior_atr_zero` | R9 fail-closed |
| 11 | `test_stop_price_is_atr_multiple_below_close_for_long` | R9 long |
| 12 | `test_stop_price_is_atr_multiple_above_close_for_short` | R9 short |
| 13 | `test_session_windows_half_open_boundaries` | §6 boundaries |
| 14 | `test_asian_window_wraps_midnight` | `in_asian` helper |
| 15 | `test_invalid_session_hours_raise_at_config_construction` | config validator |
| 16 | `test_strategy_imports_no_broker_modules` | grep / `ast` |
| 17 | `test_strategy_module_has_no_lookahead_antipattern` | grep for `.shift(-` |
| 18 | `test_signal_id_is_deterministic_across_repeated_calls` | reproducibility |
| 19 | `test_min_atr_pips_floor_blocks_when_set` | R8 |
| 20 | `test_features_dict_carries_required_keys` | features contract |
| 21 | `test_exit_model_is_time_stop_only` | exit-model string |
| 22 | `test_signal_carries_correct_version` | candidate identity |
| 23 | `test_strategy_does_not_mutate_config_dict` | param immutability |
| 24 | `test_candidate_independent_from_campaign_002_config` | no shared imports |

(Phase 3 may add more cases as warranted; the above is the
**floor**, not the ceiling.)

## 13. Explicit non-evidence warning

Every artifact this implementation emits is **research-only**.
Specifically:

- The `Signal` emitted by `SessionBreakoutStrategy.generate_signal`
  is a *signal*, not an order; it does not authorize a trade.
- The `SessionBreakoutStrategyConfig` is a config schema; loading
  it does not approve the strategy.
- The CAMPAIGN_010 YAML is a candidate config; loading it via
  `Settings` does not approve the strategy.
- A successful unit test, a config-load smoke test, a fixture
  smoke backtest, or a walk-forward dry-run plan **do not**
  approve the strategy.
- Approval is **only** the human action of adding
  `session_breakout` to
  [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
  per
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md),
  which requires the full six-evidence ladder per
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §8.

## 14. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- CAMPAIGN_002 remains **REJECT**.
- Paper / demo / live remain **blocked**.
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 15. Cross-links

- Sprint plan:
  [`ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md)
- Preferred candidate design:
  [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- Discovery protocol:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- Framework inventory:
  [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
- Walk-forward protocol:
  [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- Financing protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Strategy status registry:
  [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
