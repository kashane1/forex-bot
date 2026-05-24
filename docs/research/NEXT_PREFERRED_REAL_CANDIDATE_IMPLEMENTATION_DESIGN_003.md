# Next Preferred Real Candidate — Implementation & Evaluation Design (Sprint 003)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-003`
`strategy_evidence: false`

Phase 5 detailed implementation + evaluation design for the
selected next preferred real candidate, **C3 —
`regime_switcher_atr_percentile 0.1.0-c012` (CAMPAIGN_012)** —
per the Phase 4 selection in
[`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md)
and the Phase 3 feasibility deep dive in
[`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md).
**This design is binding for the future scaffold + evidence
sprints; no strategy code is written here.**

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_012 cannot be approved by this
> sprint or by either the future scaffold sprint or the future
> evidence sprint.** Approval requires the full six-evidence
> ladder + a deliberate human approval action per
> [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 1. Strategy hypothesis (verbatim, frozen)

> **Trend persistence on H4 OANDA practice majors is
> regime-conditional. CAMPAIGN_002 / CAMPAIGN_003 demonstrated
> that unconditional EMA-Donchian momentum lost to costs.
> CAMPAIGN_010 demonstrated that liquidity-flow session
> momentum also lost. CAMPAIGN_011 demonstrated that random
> entry on the same universe + cost model is essentially
> flat. The C3 hypothesis is that a simple regime gate — only
> trade trend signals when the prior completed day's D1AGG
> ATR-14 is in the top 30 % of the trailing 60 completed
> days — turns the cost-drag headwind into a survivable
> tailwind during high-vol periods, while suppressing trades
> during low-vol regimes when costs dominate. The headline
> gate vector is inherited verbatim from CAMPAIGN_010 /
> CAMPAIGN_011's pre-commit so the comparison is on the
> regime-gate hypothesis alone, not on a shifted goalpost.
> CAMPAIGN_011's metrics provide the null-baseline floor that
> a passing CAMPAIGN_012 must beat by a meaningful margin.**

## 2. Universe + timeframe + data requirements

| dimension | value |
|---|---|
| universe (exact, frozen) | `["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"]` |
| timeframe (execution) | H4 |
| timeframe (regime feature) | D1AGG (computed in-strategy from H4 via existing aggregator) |
| data source | local SQLite store at `data/campaign_002.sqlite3` (gitignored symlink — matches CAMPAIGN_010 / CAMPAIGN_011) |
| required source label | `oanda-practice` (runner-enforced) |
| data span | 2020-01-01 → 2026-05-19 inclusive (matches CAMPAIGN_010 / CAMPAIGN_011) |
| new data fetch needed? | **no** |
| new credentials needed? | **no** |
| new external dependency? | **no** |

## 3. R1–R8 signal rules (binding)

The strategy's `generate_signal(ctx) -> Signal | None` MUST
implement the following 8 rules in order. Each rule returns
`None` if its condition is not satisfied; only R8 emits a
`Signal`.

### R1 — Warm-up

The strategy requires sufficient H4 history to produce
`regime_lookback_days + daily_atr_lookback = 60 + 14 = 74`
emitted D1AGG candles. With 6 H4 bars per trading day and
weekend gaps, ~80–95 trading days × 6 H4 bars = ~480–570 H4
bars. Set `warmup_bars_required()` to **500** for safety.

```python
df = ctx.candles.completed_only().df
if len(df) < self.warmup_bars_required():
    return None
```

### R2 — Block re-entry while a position is open

```python
if any(
    not pos.is_flat and pos.instrument == ctx.instrument.name
    for pos in ctx.open_positions
):
    return None
```

Mirrors CAMPAIGN_010 / CAMPAIGN_011 R2 and the engine's
single-instrument single-position invariant.

### R3 — Compute the regime label from D1AGG ATR percentile

```python
from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1

h4_candles_completed = _df_to_candle_list(df, ctx.instrument.name)
agg = aggregate_h4_to_d1(h4_candles_completed)
d1_candles = agg.candles  # only `aggregated` days — never current day in progress

if len(d1_candles) < self.regime_lookback_days + self.daily_atr_lookback:
    return None  # insufficient D1AGG history

d1_atr = _wilder_atr_over_d1agg(d1_candles, self.daily_atr_lookback)
reference = d1_atr[-1]  # most recent completed day's ATR
trailing = d1_atr[-(self.regime_lookback_days + 1):-1]
assert len(trailing) == self.regime_lookback_days

pct_value = numpy.percentile(trailing, self.regime_percentile_threshold * 100)
regime = "HIGH_VOL" if reference >= pct_value else "LOW_VOL"

if regime != "HIGH_VOL":
    return None  # only trade in high-vol regime
```

**Binding invariants** (Phase 5 unit tests will enforce):

- The aggregator is called only on `df.completed_only()` —
  never on incomplete H4 bars.
- The reference D1AGG candle is the most recent emitted
  (`d1_candles[-1]`) — never includes the current trading day.
- The trailing window is **exactly**
  `d1_atr[-(regime_lookback_days + 1):-1]` — 60 days strictly
  preceding the reference, excluding the reference itself.
- The percentile is computed over the trailing window only —
  never global / cross-fold.
- Fail-closed under insufficient history.

### R4 — Fail-closed on insufficient H4 ATR (for stop sizing)

```python
atr_series_h4 = atr(df["high"], df["low"], df["close"], self.atr_lookback_h4)
prior_atr = float(atr_series_h4.iloc[-2])
if not math.isfinite(prior_atr) or prior_atr <= 0:
    return None
```

Mirrors CAMPAIGN_010 / 011 R5. Bar `t-1`'s H4 ATR is used; bar
`t`'s OHLC is not consulted.

### R5 — Trend sub-signal from `close[t]` vs `close[t−4]`

```python
last_close = float(df["close"].iloc[-1])
anchor_close = float(df["close"].iloc[-5])
if not (math.isfinite(last_close) and math.isfinite(anchor_close)):
    return None

move = last_close - anchor_close
min_move = self.min_close_move_atr_fraction * prior_atr
if abs(move) < min_move:
    return None  # filter bar-to-bar drift

side: str = "long" if move > 0 else "short"
```

`close[t]` is read only here and in R6; never for the regime
feature.

### R6 — Spread filter (delegated to RiskEngine)

The candidate does not implement its own spread filter; the
existing `RiskEngine`'s per-pair `spread_filter` gates apply
identically to CAMPAIGN_010 / CAMPAIGN_011. The runner uses
`RiskEngine(settings, mode="backtest")`.

### R7 — Stop placement

```python
if side == "long":
    stop = last_close - self.atr_stop_multiple * prior_atr
else:
    stop = last_close + self.atr_stop_multiple * prior_atr
if stop == last_close:
    return None
```

`close[t]` is used for stop placement only; the entry decision
was fully determined by R3 / R5 before `close[t]` was consulted
for stop placement.

### R8 — Emit deterministic `Signal`

```python
signal_id = _stable_signal_id(
    "regime_switcher_atr_percentile",
    "0.1.0-c012",
    ctx.instrument.name,
    timeframe,
    bar_timestamp_iso,
    side,
)

return Signal(
    signal_id=signal_id,
    strategy_name="regime_switcher_atr_percentile",
    strategy_version="0.1.0-c012",
    instrument=ctx.instrument.name,
    timeframe=timeframe,
    timestamp=bar_timestamp_utc,
    side=side,
    entry_intent="market",
    stop_model=f"ATR{atr_lookback_h4}*{atr_stop_multiple}",
    stop_price=ctx.instrument.round_price(Decimal(str(stop))),
    exit_model="time_stop_only",
    features={
        "regime": "HIGH_VOL",
        "d1agg_atr_reference": float(reference),
        "d1agg_atr_percentile_value": float(pct_value),
        "trend_move": float(move),
        "min_move_threshold": float(min_move),
        "prior_atr_h4": float(prior_atr),
        "last_close": float(last_close),
        "anchor_close": float(anchor_close),
    },
    reason=(
        f"Regime-conditional trend {side}: HIGH_VOL "
        f"(d1agg_atr {reference:.5f} >= P70 trailing-60 {pct_value:.5f}); "
        f"trend move {move:+.5f} >= {min_move:.5f} threshold"
    ),
)
```

## 4. Frozen parameter set (verbatim from Phase 3 §2; pre-commit-bound)

| parameter | value |
|---|---|
| `version` | `"0.1.0-c012"` |
| `timeframe` | `"H4"` |
| `atr_lookback_h4` | `14` (stop-sizing only) |
| `atr_stop_multiple` | `2.0` |
| `max_bars_in_trade` | `6` |
| `trailing_stop_atr_multiple` | `None` |
| `min_atr_pips` | `{}` |
| `daily_atr_lookback` | `14` (D1AGG ATR-14) |
| `regime_lookback_days` | `60` |
| `regime_percentile_threshold` | `0.70` |
| `min_close_move_atr_fraction` | `0.25` |
| `trend_lookback_h4_bars` | `4` |

**Any change to any of these parameters constitutes a NEW
candidate** that requires its own discovery + design cycle.
Any deviation in the loaded YAML aborts the runner before any
backtest fires.

## 5. No-lookahead rules (binding)

| safeguard | enforcement |
|---|---|
| **Regime feature input contains only completed prior H4 candles** | Phase 5 unit test asserts `_df_to_candle_list` is called only on `df.completed_only()`; AST-level check that the regime-feature helper does not read `df["close"]` / `df["high"]` / `df["low"]` / `df["open"]` / `df["volume"]` for any bar `t` index |
| **Regime feature uses only `aggregated` D1AGG candles** | Phase 5 unit test asserts `_compute_regime` consumes only `agg.candles` (which the aggregator's contract guarantees are completed trading days) |
| **Percentile window is the trailing 60 days *strictly preceding* the reference day** | Phase 5 unit test asserts the slice is `d1_atr[-(60+1):-1]` exactly; rejects any global / inclusive variant |
| **No global percentile cached across runs** | Per-bar computation; Phase 5 unit test verifies regime-feature helper is purely functional with no module-level state |
| **`close[t]` is read only for the trend sub-signal (R5) and stop placement (R7)** | Phase 5 unit test source-greps for the exact patterns `df["close"].iloc[-1]` (R5/R7) and `df["close"].iloc[-5]` (R5 anchor); rejects any other bar-`t` field read |
| **H4 ATR uses index `-2`** | matches CAMPAIGN_010 / 011 convention; Phase 5 unit test verifies `atr_series_h4.iloc[-2]` |
| **No future bars** | `completed_only()` filter; harness drives bar-by-bar |
| **Strategy module imports nothing from `forex_bot.broker` / `.execution` / `.loops`** | source-grep unit test |
| **Strategy module does not reference CAMPAIGN_010 keys** (`asian_session_hours`, `london_session_hours`, `min_asian_range_atr_fraction`, `session_breakout`) | source-grep unit test |
| **Strategy module does not reference CAMPAIGN_011 keys** (`master_seed`, `entry_probability_per_bar`, `random_entry_anchor`) | source-grep unit test |
| **Strategy module does not reference CAMPAIGN_002 keys** (`donchian`, `ema_fast`, `ema_slow`, `adx_threshold`) | source-grep unit test |

## 6. Missing-data behavior

- A bar with `NaN` `prior_atr_h4` returns `None` (R4).
- A bar where the pair's row count is < warm-up returns
  `None` (R1).
- A bar where `ctx.open_positions` already has an active
  position for the instrument returns `None` (R2).
- A bar where insufficient D1AGG aggregated days exist
  (< 74) returns `None` (R3).
- A bar where the regime is `LOW_VOL` returns `None` (R3 gate).
- A bar where the trend sub-signal magnitude is below
  threshold returns `None` (R5 gate).
- A bar where `anchor_close` (`close[-5]`) is `NaN` /
  non-finite returns `None` (R5).

The strategy never raises an exception on bad data; it
fail-closes by emitting no signal. Consistent with CAMPAIGN_010
/ CAMPAIGN_011.

## 7. Config schema needs

Add to `src/forex_bot/config.py`:

```python
class RegimeSwitcherAtrPercentileStrategyConfig(BaseModel):
    """Frozen-parameter config for the regime_switcher_atr_percentile
    research candidate (CAMPAIGN_012)."""
    model_config = ConfigDict(extra="forbid")
    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    atr_lookback_h4: int = 14
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = None
    max_bars_in_trade: int = 6
    min_atr_pips: dict[str, float] = Field(default_factory=dict)
    daily_atr_lookback: int = 14
    regime_lookback_days: int = 60
    regime_percentile_threshold: float = 0.70
    min_close_move_atr_fraction: float = 0.25
    trend_lookback_h4_bars: int = 4

    @model_validator(mode="after")
    def _check(self) -> RegimeSwitcherAtrPercentileStrategyConfig:
        if self.atr_lookback_h4 < 2:
            raise ConfigError("atr_lookback_h4 must be >= 2")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        if self.max_bars_in_trade < 1:
            raise ConfigError("max_bars_in_trade must be >= 1")
        if self.daily_atr_lookback < 2:
            raise ConfigError("daily_atr_lookback must be >= 2")
        if self.regime_lookback_days < 10:
            raise ConfigError("regime_lookback_days must be >= 10 for stable percentile")
        if not (0.0 < self.regime_percentile_threshold < 1.0):
            raise ConfigError("regime_percentile_threshold must be in (0, 1) (exclusive)")
        if self.min_close_move_atr_fraction <= 0:
            raise ConfigError("min_close_move_atr_fraction must be > 0")
        if self.trend_lookback_h4_bars < 1:
            raise ConfigError("trend_lookback_h4_bars must be >= 1")
        if self.trailing_stop_atr_multiple is not None:
            raise ConfigError(
                "trailing_stop_atr_multiple must be None in v1 — "
                "the regime switcher uses time-stop only"
            )
        return self
```

Add to `StrategyConfig`:

```python
regime_switcher_atr_percentile: RegimeSwitcherAtrPercentileStrategyConfig | None = None
```

Plus the matching enabled-list check in
`StrategyConfig._check_enabled`:

```python
if (
    "regime_switcher_atr_percentile" in self.enabled
    and self.regime_switcher_atr_percentile is None
):
    raise ConfigError(
        "strategy.regime_switcher_atr_percentile config required when enabled"
    )
```

## 8. Strategy module location

`src/forex_bot/strategies/regime_switcher_atr_percentile.py` —
implements the `Strategy` protocol identically in shape to
`session_breakout.py` / `random_entry_anchor.py`. Estimated
size: ~250 LOC (slightly larger than session_breakout because
it includes the D1AGG aggregation helper and a Wilder ATR over
D1AGG-typed candles).

Add to `src/forex_bot/strategies/__init__.py`:

```python
from forex_bot.strategies.regime_switcher_atr_percentile import (
    RegimeSwitcherAtrPercentileStrategy,
)
__all__ = [
    ...,
    "RegimeSwitcherAtrPercentileStrategy",
]
```

## 9. Tests required (`tests/unit/test_regime_switcher_atr_percentile.py`)

Minimum 25 cases covering:

- **Config defaults / validation** (≥ 6): defaults match the
  frozen spec; rejects invalid bounds + extra fields;
  `StrategyConfig._check_enabled` slot.
- **Regime feature — happy path** (≥ 3): HIGH_VOL when
  reference > P70; LOW_VOL when reference < P70; boundary
  exactly at P70 → HIGH_VOL (inclusive).
- **Regime feature — no-lookahead structural audit** (≥ 4):
  helper signature contains only documented args; helper body
  reads no bar-`t` `df["close"]` / `df["high"]` / `df["low"]`
  / `df["open"]` / `df["volume"]`; trailing-window slice is
  exactly `[-(N+1):-1]`; INSUFFICIENT_HISTORY returns None
  when D1AGG count < 74.
- **D1AGG aggregator integration** (≥ 2): strategy passes
  only completed H4 candles; aggregator returns only
  `aggregated` days; the strategy uses `agg.candles` only.
- **Strategy core** (≥ 5): R1 warm-up; R2 block re-entry; R4
  fail-closed on NaN ATR; R5 trend sub-signal long / short
  directions; R7 stop placement long / short.
- **R5 minimum-move filter** (≥ 2): close move below threshold
  returns None; equal-to threshold passes.
- **No forbidden imports / usages** (≥ 2): no
  `forex_bot.broker` / `.execution` / `.loops` imports; no
  random / numpy.random; uses `numpy.percentile` only.
- **Rejected-family contamination audit** (≥ 3): no `donchian`
  / `ema_fast` / `ema_slow` / `adx_threshold` / `trend_following`;
  no `asian_session_hours` / `london_session_hours` /
  `min_asian_range_atr_fraction` / `session_breakout`;
  no `master_seed` / `entry_probability_per_bar` /
  `random_entry_anchor`.
- **Approval / safety regression** (≥ 2):
  `approved_strategies.yaml` still empty;
  `regime_switcher_atr_percentile` NOT in
  `configs/paper.yaml` / `configs/practice.yaml`.

## 10. Walk-forward requirements

Inherited verbatim from CAMPAIGN_010 / CAMPAIGN_011:

| field | value |
|---|---|
| `--style` | `rolling` |
| `--parameter-mode` | `frozen` |
| `--train-days` | `540` |
| `--validation-days` | `180` |
| `--test-days` | `180` |
| `--step-days` | `180` |
| `--universe-start` | `2020-01-01` |
| `--universe-end` | `2026-05-20` |
| expected fold count | **8** (same as CAMPAIGN_010 / CAMPAIGN_011) |
| min fold count gate | **≥ 6** |

### 10.1 Per-fold gates (inherited from CAMPAIGN_010 §10 / CAMPAIGN_011 §11)

| level | gate | threshold |
|---|---|---|
| test fold | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| test fold | `profit_factor_net_of_stress_financing` | ≥ 1.10 |
| test fold | `pairs_positive_net_of_stress_financing` | ≥ 4 of 7 |
| test fold | `trade_count` | ≥ 30 |
| test fold | `single_pair_dominance` | ≤ 60 % |

### 10.2 Aggregate gates (inherited)

| level | gate | threshold |
|---|---|---|
| aggregate | `fold_pass_rate` | 100 % (strict) |
| aggregate | `fold_count` | ≥ 6 |
| aggregate | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| aggregate | `profit_factor_net_of_stress_financing` | ≥ 1.10 |
| aggregate | `pairs_positive` | ≥ 4 of 7 |
| aggregate | `trade_count` | ≥ 200 |
| aggregate | `single_fold_dominance` | ≤ 60 % |
| aggregate | `single_pair_dominance` | ≤ 40 % |
| financing | `conservative_stress_run_does_not_flip_verdict` | PASS |
| financing | `modeled_refused` | PASS |
| financing | `missing_rate_event_count` | 0 |

### 10.3 Null-baseline comparison gate (binding; CAMPAIGN_011-derived)

Per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§3, in addition to the inherited gates, CAMPAIGN_012's verdict
doc must include a **"Null-baseline comparison"** section with
explicit "meaningful improvement over null?" verdicts:

| metric | CAMPAIGN_011 floor | CAMPAIGN_012 must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 R | by ≥ +0.0524 R → reach ≥ 0.05 R |
| aggregate profit factor | 0.91 | by ≥ +0.19 → reach ≥ 1.10 |
| aggregate return % (4y) | −0.53 % | meaningfully positive (≥ +5 %) |
| `pairs_positive` | 3 / 7 | ≥ 4 / 7 |
| `fold_pass_rate` | 0 / 8 | 100 % (strict-pass) |
| `single_fold_dominance` | 40.1 % | ≤ 60 % (CAMPAIGN_010 gate) |

If CAMPAIGN_012's metrics cluster within
**±0.005 R / ±0.10 PF / ±2 pp / ±1 pair** of CAMPAIGN_011's,
the verdict doc must classify it as
**REJECT (indistinguishable from null)**.

## 11. Financing requirements

- **Expected holding period.** ≤ 6 H4 bars (matches CAMPAIGN_010
  / 011). Most trades incur 0–1 daily rollover events.
- **Expected financing sensitivity.** Modest. The regime gate
  reduces total trade count (only HIGH-VOL bars qualify), so
  cashflow_home_stress_total should scale roughly with
  trade-count × ~$0.023 per event (per CAMPAIGN_010 / 011
  consistency).
- **ESTIMATED + conservative stress** — the only authorized
  source. **MODELED remains refused at four layers.**
- **Whether MODELED financing blocks promotion.** Yes — per the
  existing `financing_treatment_blocks_approval` gate. A
  passing CAMPAIGN_012 would still require MODELED financing
  for live promotion (paper is acceptable under ESTIMATED with
  explicit human override per the existing rule); the
  evidence sprint reports the ESTIMATED result + the gate
  status; the human approval action decides.
- **Whether financing flips the verdict.** Required to pass the
  `conservative_stress_run_does_not_flip_verdict` gate: if
  pre-financing is PASS but post-financing flips to fail, the
  verdict is REJECT.

## 12. Portfolio-risk diagnostics

| diagnostic | expected value (regime-gated trend) |
|---|---|
| max concurrent open positions per instrument | 1 (engine-enforced) |
| per-pair trade count | reduced vs CAMPAIGN_011 (only HIGH-VOL bars qualify); should still satisfy per-fold trade-count ≥ 30 + aggregate ≥ 200 |
| aggregate notional | bounded by `risk_per_trade_pct = 0.25 %` |
| pair concentration (single-pair dominance %) | informational; gate ≤ 40 % aggregate |
| **regime-period clustering** | trades cluster in HIGH-VOL periods (e.g. central-bank announcement weeks, geopolitical-event months); the diagnostics doc should report which fold's HIGH-VOL periods drove the trades |
| session-of-day distribution | similar to CAMPAIGN_011 (diffuse across UTC hours) since the regime filter is daily, not session-of-day |
| loss streaks per pair | depends on regime persistence; expected similar order of magnitude to CAMPAIGN_010 / 011 |
| drawdown clustering | should be moderate; the regime gate's purpose is to avoid the cost-drag traps |
| RiskEngine rejection profile | same spread filter as CAMPAIGN_010 / 011; same SESSION_BLOCKED rejections |

## 13. Independent-verifier requirements

- **Verifier extension is not required for the REJECT verdict.**
  Item 5 of the six-evidence ladder is a paper-promotion gate;
  a CAMPAIGN_012 REJECT only needs items 1–3.
- **Verifier extension is REQUIRED for a paper-promotion verdict.**
  If CAMPAIGN_012 unexpectedly passes every gate, the
  `infra-free-local-parity-verifier-regime-switcher-001` sprint
  must run before any human approval consideration.
- **Verifier scope** (if/when extension is required):
  - Re-implement `_compute_regime` from
    `RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC`-style
    spec text (not copied from the strategy module).
  - Re-implement the D1AGG aggregation independently (using
    only `hashlib` / `datetime` / `numpy` — no `forex_bot`
    imports).
  - Compare per-pair-per-fold trade counts within the existing
    WARN-band tolerances; the regime gate's *binary*
    classification means trade-count exact-equivalence is
    achievable in principle (subject to floating-point
    determinism).

## 14. Rejection criteria before paper/demo consideration

CAMPAIGN_012's verdict is **REJECT** if any of the following hold:

| level | criterion |
|---|---|
| any per-fold | any gate from §10.1 fails on any test fold |
| aggregate | any gate from §10.2 fails |
| financing | conservative-stress overlay flips a passing verdict |
| null-baseline | metrics cluster within ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair of CAMPAIGN_011 (classified `REJECT (indistinguishable from null)`) |
| no-lookahead | any structural-audit unit test fails |
| pipeline | the runner aborts before completion (BLOCKED) |

If the verdict is **PASS** on every per-fold + aggregate +
financing gate AND meets the meaningful-improvement-over-null
criteria:

- The evidence sprint's verdict doc classifies it
  `RESEARCH_PASS_UNAPPROVED` (not approved; awaiting human
  action).
- The candidate becomes the first ever evidence-passing
  candidate; the next-step path requires items 5
  (verifier extension via
  `infra-free-local-parity-verifier-regime-switcher-001`) and
  6 (deliberate human approval per
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)).

## 15. Required artifacts (committed by the future evidence sprint)

The future
`research-regime-switcher-atr-percentile-walk-forward-001`
evidence sprint must commit:

- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.json`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/plan.md`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.json`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.md`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/fold_detail.json`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds/fold_NN/fold_NN_<PAIR>_summary.json`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/folds/fold_NN/fold_NN_<PAIR>_trades.csv`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_run.{json,md}`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_summary.json`
- `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/risk/diagnostics.{json,md}`
- `docs/research/CAMPAIGN_012_DATA_PROVENANCE.md`
- `docs/research/CAMPAIGN_012_WALK_FORWARD_PLAN.md`
- `docs/research/CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`
- `docs/research/CAMPAIGN_012_WALK_FORWARD_RESULT.md` (with null-baseline comparison section)
- `docs/research/CAMPAIGN_012_FINANCING_OVERLAY.md`
- `docs/research/CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`
- `docs/research/CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`
- `docs/research/CAMPAIGN_012_EVIDENCE_SUMMARY.md`
- `docs/research/CAMPAIGN_012_STATUS.md` (updated to `rejected` or `research_pass_unapproved`)
- `docs/research/REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md`

The pattern strictly mirrors CAMPAIGN_010 / CAMPAIGN_011's
evidence sprints.

## 16. Future scaffold sprint cannot approve

Forbidden in the future scaffold sprint:

- Adding `regime_switcher_atr_percentile` to
  `configs/approved_strategies.yaml`.
- Running `paper-loop` or `demo-loop` against the candidate's
  config.
- Creating any `live-loop` command.
- Changing any frozen parameter from §4.
- Changing the D1AGG aggregator.

## 17. Future evidence sprint cannot approve

Same as §16. Even a clean PASS produces *research evidence* —
the candidate becomes `RESEARCH_PASS_UNAPPROVED` pending the
verifier-extension sprint + human approval action.

## 18. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 remain REJECT**
  (untouched).
- **Paper / demo / live remain blocked.**
- No strategy code edited this phase.
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 19. Pre-flight checklist for the future scaffold sprint

The future `research-regime-switcher-atr-percentile-001`
sprint's Phase 0 audit should verify:

- [ ] Repo state clean.
- [ ] `configs/approved_strategies.yaml` reads `approved: []`.
- [ ] CAMPAIGN_002 / 010 / 011 verdicts unchanged.
- [ ] 771 pytests pass (Phase 0 baseline).
- [ ] 11 pre-existing UP042 ruff findings in untouched files
      (unchanged).
- [ ] Archive validator + freeze checker + secret scanner PASS.
- [ ] Loops refuse; no `live-loop`.
- [ ] No `regime_switcher_atr_percentile.py` exists yet.
- [ ] No `RegimeSwitcherAtrPercentileStrategyConfig` in
      `src/forex_bot/config.py` yet.
- [ ] No `CAMPAIGN_012_*` artifact directory under
      `backtests/` yet.
- [ ] `src/forex_bot/backtesting/d1_aggregation.py` exists and
      its public API (`aggregate_h4_to_d1`, `D1AggregationResult`,
      `AGG_GRANULARITY`, `rollover_safe`) matches the C3 spec.
- [ ] All Phase 3 §2 frozen parameter values match the
      pre-commit verbatim.

## 20. Cross-links

- [`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md)
  (Phase 4 selection)
- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md)
  (Phase 2 scoring)
- [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
  (Phase 3 feasibility + binding frozen parameters)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
  (binding null-baseline comparison rules)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  (the gate vector C3 inherits)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
  (same gate vector inherited)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`D1_AGGREGATION_DESIGN.md`](D1_AGGREGATION_DESIGN.md)
- [`src/forex_bot/backtesting/d1_aggregation.py`](../../src/forex_bot/backtesting/d1_aggregation.py)
- [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md)
  (Phase 6 future scaffold-branch spec)
- [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md)
  (Phase 6 future evidence-branch spec)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
