# Regime Switcher ATR-Percentile — Implementation Spec (Phase 1)

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-001`
`strategy_evidence: false`

Phase 1 binding implementation spec for **CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012`**, the C3
daily-ATR-percentile regime-switcher real candidate. **Spec only — no
strategy code written here.** The Phase 2 scaffold implementation,
Phase 3 unit tests, Phase 4 candidate YAML, and the future evidence
sprint must all conform to the rules below verbatim.

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_011
> is the **null baseline only**, not a trading candidate.

Sources of truth (all binding, conformant):

- [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md) §1, §2, §5, §6
- [`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md)
- [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md) §1–§17
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (null-baseline gate)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- `src/forex_bot/backtesting/d1_aggregation.py` (D1AGG aggregator)

## 1. Strategy hypothesis (verbatim, frozen)

> Trend persistence on H4 OANDA practice majors is regime-conditional.
> CAMPAIGN_002 / 003 demonstrated that unconditional EMA-Donchian
> momentum lost to costs. CAMPAIGN_010 demonstrated that liquidity-flow
> session momentum also lost. CAMPAIGN_011 demonstrated that random
> entry on the same universe + cost model is essentially flat. The C3
> hypothesis is that a simple regime gate — only trade trend signals
> when the prior completed day's D1AGG ATR-14 is in the top 30 % of
> the trailing 60 completed days — turns the cost-drag headwind into
> a survivable tailwind during high-vol periods, while suppressing
> trades during low-vol regimes when costs dominate.

## 2. Frozen parameters (binding — pre-commit-bound)

| parameter | value | role |
|---|---|---|
| `version` | `"0.1.0-c012"` | candidate id |
| `timeframe` | `"H4"` (default; literal `"H1" \| "H4" \| "D"`) | execution timeframe |
| `atr_lookback` | `14` | H4 ATR for **stop sizing** (Wilder, via `forex_bot.strategies.indicators.atr`) |
| `atr_stop_multiple` | `2.0` | stop = `close[t] ± atr_stop_multiple × prior_atr_h4` |
| `max_bars_in_trade` | `6` | engine-enforced time stop (≈ 1 trading day) |
| `trailing_stop_atr_multiple` | `None` | **forbidden in v1**; rejected by validator |
| `min_atr_pips` | `{}` | per-pair ATR floor; default empty |
| `daily_atr_lookback` | `14` | Wilder ATR over D1AGG candles for the regime feature |
| `regime_lookback_days` | `60` | trailing window length for the ATR-percentile reference |
| `regime_percentile_threshold` | `0.70` | "top 30 %"; HIGH-VOL gate is `reference >= P70` |
| `min_close_move_atr_fraction` | `0.25` | trend filter floor as fraction of `prior_atr_h4` |
| `trend_lookback_h4_bars` | `4` | `close[t]` vs `close[t-4]` (one trading day on H4) |
| `warm_up_bars` | `500` (effective — derived from `warmup_bars_required()`) | covers 60 d × 6 H4 bars/day + 14 ATR + 4 trend + slack |

**Any deviation from any value above constitutes a NEW candidate** that
requires its own discovery + design cycle. The runner / config loader
must reject any deviation.

**Naming clarification.** The Phase 5 design doc
([`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
§7) refers to the H4 ATR parameter as `atr_lookback_h4` for
descriptive clarity. The implementation keeps the existing
project-wide name `atr_lookback` (matching `SessionBreakoutStrategyConfig`
and `RandomEntryAnchorStrategyConfig`); the *value* is identical (`14`).
The D1AGG ATR parameter is `daily_atr_lookback` to make the
distinction explicit.

## 3. R-rule table (binding)

Each rule below returns `None` if its condition is not met. Only R8
emits a `Signal`. The rules execute in order at the latest *completed*
H4 bar `t` taken from `ctx.candles.completed_only().df`.

### R1 — Warm-up

```python
df = ctx.candles.completed_only().df
if len(df) < self.warmup_bars_required():
    return None
```

`warmup_bars_required()` returns at least the maximum of:

- `daily_atr_lookback + regime_lookback_days + 1 = 14 + 60 + 1 = 75` D1AGG
  candles' worth of H4 bars (≈ `75 × 6 = 450` H4 bars, plus weekend gaps
  → realistic minimum ~500);
- `atr_lookback + 2 = 16` H4 bars (mirrors session_breakout / random_entry_anchor);
- `trend_lookback_h4_bars + 1 = 5` H4 bars (for the `iloc[-5]` anchor);

→ pinned at **`500`** for safety (matches the discovery-003 design).

### R2 — Block re-entry while a position is open

```python
if any(
    not pos.is_flat and pos.instrument == ctx.instrument.name
    for pos in ctx.open_positions
):
    return None
```

Same rule as `session_breakout` R2 and `random_entry_anchor` R2;
respects the engine's single-instrument single-position invariant.

### R3 — Compute regime label from completed D1AGG ATR percentile

```python
from forex_bot.backtesting.d1_aggregation import aggregate_h4_to_d1

# Build Candle list from completed H4 bars (df is already completed_only).
h4_candles = _df_to_completed_h4_candle_list(df, ctx.instrument.name)
agg = aggregate_h4_to_d1(h4_candles)
d1_candles = agg.candles  # only `aggregated` (= completed + rollover_safe) days

if len(d1_candles) < (self.daily_atr_lookback + self.regime_lookback_days + 1):
    return None  # insufficient D1AGG history

# Wilder ATR-14 over the D1AGG bar mid OHLC (use bid/ask midpoint).
d1_atr_series = _wilder_atr_over_d1agg(d1_candles, self.daily_atr_lookback)
# d1_atr_series[-1] corresponds to the most recent COMPLETED trading day.
reference = float(d1_atr_series[-1])
if not math.isfinite(reference) or reference <= 0:
    return None

# Trailing window: exactly the regime_lookback_days values STRICTLY
# preceding the reference (so the reference is NOT in the window).
trailing = d1_atr_series[-(self.regime_lookback_days + 1):-1]
if len(trailing) != self.regime_lookback_days:
    return None
if not all(math.isfinite(v) and v > 0 for v in trailing):
    return None

# Percentile (numpy: inclusive linear interpolation by default).
import numpy
pct_value = float(numpy.percentile(trailing, self.regime_percentile_threshold * 100))
if not math.isfinite(pct_value):
    return None

# HIGH-VOL is inclusive at the threshold (reference == P70 → HIGH-VOL).
regime = "HIGH_VOL" if reference >= pct_value else "LOW_VOL"
if regime != "HIGH_VOL":
    return None
```

**Binding invariants** (Phase 3 unit tests enforce):

- H4 → D1AGG aggregator is called only on completed H4 bars.
- The reference value is the most recent emitted D1AGG ATR
  (`d1_atr_series[-1]`) — the aggregator's `aggregated` contract
  guarantees this is a *fully closed* trading day.
- The trailing window slice is **exactly**
  `d1_atr_series[-(regime_lookback_days + 1):-1]` — 60 values strictly
  preceding the reference. The reference is **not** in the window.
- The percentile is computed over the trailing window only — never
  global / full-sample / cross-fold.
- HIGH-VOL inclusivity at the threshold is binding (P70-inclusive).
- All values must be finite and positive; otherwise fail-closed → `None`.
- Regime computation has no module-level mutable state; the helper is
  purely functional.

### R4 — Fail-closed on insufficient / non-finite H4 ATR (for stop sizing)

```python
from forex_bot.strategies.indicators import atr
atr_series_h4 = atr(df["high"], df["low"], df["close"], self.atr_lookback)
prior_atr = float(atr_series_h4.iloc[-2])
if not math.isfinite(prior_atr) or prior_atr <= 0:
    return None
```

Mirrors CAMPAIGN_010 R5 / CAMPAIGN_011 R5 verbatim. Bar `t-1`'s H4 ATR
is used; bar `t`'s OHLC is **not** consulted for this calculation.

### R5 — Trend sub-signal from `close[t]` vs `close[t-4]`

```python
last_close = float(df["close"].iloc[-1])
anchor_close = float(df["close"].iloc[-(self.trend_lookback_h4_bars + 1)])  # iloc[-5]
if not (math.isfinite(last_close) and math.isfinite(anchor_close)):
    return None

move = last_close - anchor_close
min_move = self.min_close_move_atr_fraction * prior_atr  # 0.25 * prior_atr_h4
if abs(move) < min_move:
    return None  # filter bar-to-bar drift

side: str = "long" if move > 0 else "short"
```

`close[t]` is read in R5 and R7 **only**; never in the regime feature
(R3) and never for any other purpose. The anchor `close[t-4]` is
`df["close"].iloc[-(trend_lookback_h4_bars + 1)]` — i.e. `iloc[-5]`
when `trend_lookback_h4_bars = 4` (the frozen value). Bar `t`'s
`high` / `low` / `open` / `volume` are deliberately not consulted.

### R6 — Spread filter (delegated to RiskEngine)

The strategy does not implement its own spread filter. The existing
`RiskEngine` enforces per-pair spread gates identically to CAMPAIGN_010
/ CAMPAIGN_011. The runner uses `RiskEngine(settings, mode="backtest")`.
No change to the RiskEngine in this sprint.

### R7 — Stop placement

```python
from decimal import Decimal
if side == "long":
    stop = last_close - self.atr_stop_multiple * prior_atr
else:
    stop = last_close + self.atr_stop_multiple * prior_atr
if stop == last_close:
    # Defense in depth — unreachable given prior_atr > 0 in R4.
    return None
stop_price = ctx.instrument.round_price(Decimal(str(stop)))
```

`close[t]` is used **only** for stop placement here; the entry decision
(side from R5; gate from R3) is fully determined before `close[t]` is
read for stop placement.

### R8 — Emit deterministic `Signal`

```python
import hashlib
from datetime import UTC
import pandas as pd

idx_t = df.index[-1]
bar_timestamp_iso = pd.Timestamp(idx_t).tz_convert(UTC).isoformat()

signal_id = _stable_signal_id(
    self.name,            # "regime_switcher_atr_percentile"
    self.version,         # "0.1.0-c012"
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
    timestamp=pd.Timestamp(idx_t).tz_convert(UTC).to_pydatetime(),
    side=side,  # "long" or "short"
    entry_intent="market",
    stop_model=f"ATR{atr_lookback}*{atr_stop_multiple}",
    stop_price=stop_price,
    exit_model="time_stop_only",
    features={
        "regime": "HIGH_VOL",
        "d1agg_atr_reference": float(reference),
        "d1agg_atr_percentile_value": float(pct_value),
        "d1agg_count": int(len(d1_candles)),
        "trend_move": float(move),
        "min_move_threshold": float(min_move),
        "prior_atr_h4": float(prior_atr),
        "last_close": float(last_close),
        "anchor_close": float(anchor_close),
        "regime_lookback_days": int(self.regime_lookback_days),
        "regime_percentile_threshold": float(self.regime_percentile_threshold),
    },
    reason=(
        f"Regime-conditional trend {side}: HIGH_VOL "
        f"(d1agg_atr {reference:.5f} >= P{int(self.regime_percentile_threshold*100)} "
        f"trailing-{self.regime_lookback_days} {pct_value:.5f}); "
        f"trend move {move:+.5f} >= {min_move:.5f} threshold"
    ),
)
```

The signal_id is a SHA-1 of the canonical `"|"`-joined input string —
deterministic across runs and processes (no `hash()`, no PRNG).

## 4. No-lookahead safeguards (binding — Phase 3 unit tests will enforce)

| safeguard | enforcement |
|---|---|
| **D1AGG bars must be completed and `rollover_safe`** | The aggregator's `_aggregate_day` only emits a candle when all 6 H4 bars are well-formed and the timestamp clears the NY 16:45–17:15 rollover blackout (`rollover_safe()` defensive check). `agg.candles` contains only such bars. |
| **Trailing percentile excludes the current incomplete daily bar** | `d1_atr_series[-1]` is the *most recent emitted* D1AGG ATR; by the aggregator contract this is a fully closed trading day, never the in-progress day. |
| **Rolling percentile uses prior completed D1AGG bars only** | The trailing window is exactly `d1_atr_series[-(regime_lookback_days + 1):-1]`; structural-audit unit test confirms the slice. |
| **No full-sample / global / cross-fold percentile** | The regime helper is purely functional, takes only the most recent D1AGG ATR series as input, and uses only a trailing window. No module-level cache; no DataFrame mutation. |
| **No future test-window statistics** | The walk-forward harness drives the strategy bar-by-bar in chronological order; the strategy never reads future bars. |
| **H4 ATR uses closed bars only (`iloc[-2]`)** | `prior_atr = atr_series_h4.iloc[-2]` — bar `t-1`'s ATR. Matches CAMPAIGN_010 / 011 convention. |
| **Trend filter uses only closed H4 bars** | `last_close = df["close"].iloc[-1]` (bar `t`, closed); `anchor_close = df["close"].iloc[-5]` (bar `t-4`, closed). |
| **`close[t]` is read only in R5 (trend sub-signal) and R7 (stop placement)** | Phase 3 source-grep test confirms `df["close"].iloc[-1]` appears in the trend / stop blocks only; rejects `df["high"].iloc[-1]`, `df["low"].iloc[-1]`, `df["open"].iloc[-1]`, `df["volume"].iloc[-1]`. |
| **No bar-`t` reads of `high` / `low` / `open` / `volume`** | The strategy reads `df["high"]` / `df["low"]` only through `forex_bot.strategies.indicators.atr(...)` over the full series, then takes `.iloc[-2]`. No `iloc[-1]` is taken on those columns. |
| **Strategy module imports nothing from `forex_bot.broker` / `.execution` / `.loops`** | Source-grep unit test. |
| **Strategy module does not import `random`, `numpy.random`, or `secrets`** | Source-grep unit test. The strategy uses `numpy.percentile` only (a pure deterministic function); `numpy` is imported but `numpy.random` is forbidden. |
| **Strategy module does not reference CAMPAIGN_002 / `trend_following` / Donchian / EMA keys** | Source-grep unit test. |
| **Strategy module does not reference CAMPAIGN_010 / `session_breakout` / Asian / London keys** | Source-grep unit test. |
| **Strategy module does not reference CAMPAIGN_011 / `random_entry_anchor` / `master_seed` / `entry_probability` keys** | Source-grep unit test. |
| **Strategy does not mutate `ctx.config` during signal generation** | Phase 3 unit test diffs the config dict before/after the call. |
| **Strategy exposes no approval-shaped public attribute** | Phase 3 introspection test rejects any attribute name containing `approve`, `approval`, `promote`, `promotion`. |

## 5. Fail-closed rules (binding)

The strategy returns `None` (no signal; no exception) under any of:

| condition | rule |
|---|---|
| `len(df) < warmup_bars_required()` | R1 |
| `ctx.open_positions` already has an active position for the instrument | R2 |
| D1AGG candle count < `daily_atr_lookback + regime_lookback_days + 1` | R3 |
| reference D1AGG ATR is NaN / non-finite / ≤ 0 | R3 |
| any value in the trailing window is NaN / non-finite / ≤ 0 | R3 |
| percentile value is NaN / non-finite | R3 |
| regime classifies as LOW-VOL (`reference < P70`) | R3 |
| H4 ATR at `iloc[-2]` is NaN / non-finite / ≤ 0 | R4 |
| `last_close` or `anchor_close` is NaN / non-finite | R5 |
| `\|move\| < min_close_move_atr_fraction × prior_atr_h4` | R5 |
| `stop == last_close` (defense in depth; unreachable given R4) | R7 |

The strategy **never raises an exception** on bad data. Consistent with
CAMPAIGN_010 / CAMPAIGN_011 convention.

## 6. Tests expected (Phase 3 — at least 30 deterministic unit tests)

The breakdown below is a *minimum*; Phase 3 may add more tests as
implementation needs surface. Section labels match the planned test
file structure.

### 6.1 Config defaults / validation (≥ 12 cases)

1. defaults match the frozen spec verbatim
2. rejects `regime_percentile_threshold <= 0`
3. rejects `regime_percentile_threshold >= 1`
4. rejects non-positive `daily_atr_lookback`
5. rejects non-positive `regime_lookback_days` (and too-small e.g. `< 10`)
6. rejects negative `min_close_move_atr_fraction` (and zero)
7. rejects non-positive `trend_lookback_h4_bars`
8. rejects non-positive `atr_lookback`
9. rejects non-positive `atr_stop_multiple`
10. rejects non-positive `max_bars_in_trade`
11. rejects non-`None` `trailing_stop_atr_multiple` in v1
12. rejects extra fields (`extra="forbid"`)
13. `StrategyConfig._check_enabled` rejects missing nested config when `regime_switcher_atr_percentile` is in `enabled`

### 6.2 Strategy core — R1 / R2 / R4 / R7 (≥ 6 cases)

14. R1: no signal before warm-up (`< 500` bars)
15. R2: no signal when position already open
16. R3: no signal when D1AGG history is insufficient (< 75 days)
17. R4: no signal when H4 ATR is NaN / non-finite / ≤ 0
18. R7: long-stop placement at `close[t] - 2 × prior_atr_h4`
19. R7: short-stop placement at `close[t] + 2 × prior_atr_h4`

### 6.3 R3 — regime gate (≥ 4 cases)

20. no signal when reference D1AGG ATR is below P70 (LOW-VOL gate)
21. signal-eligible when reference D1AGG ATR is at or above P70 (HIGH-VOL gate; inclusive at threshold)
22. trailing window excludes the reference itself (slice `[-(N+1):-1]`)
23. percentile uses trailing window only — not full-sample (helper purely functional / no module state)

### 6.4 R5 — trend sub-signal (≥ 3 cases)

24. long when `close[t] > close[t-4] + min_move`
25. short when `close[t] < close[t-4] - min_move`
26. no signal when `|close[t] - close[t-4]| < min_move`

### 6.5 No-lookahead structural audit (≥ 4 cases)

27. strategy module source does NOT read `df["high"].iloc[-1]` / `df["low"].iloc[-1]` / `df["open"].iloc[-1]` / `df["volume"].iloc[-1]`
28. strategy module source DOES read `df["close"].iloc[-1]` (R5/R7) and `df["close"].iloc[-5]` (R5 anchor) — via the parameterized form `iloc[-(N+1)]`
29. signal id is deterministic across runs (same inputs → same `signal_id`)
30. strategy does not mutate `ctx.config` during signal generation

### 6.6 Forbidden imports / usages (≥ 3 cases)

31. no imports from `forex_bot.broker` / `forex_bot.execution` / `forex_bot.loops`
32. no `import random`, `from random import`, `import numpy.random`, `from numpy.random`, `np.random`, `numpy.random`, `import secrets`, `from secrets`
33. no use of built-in `hash()` for entry / signal-id derivation (only `hashlib.sha*`)

### 6.7 Rejected-family contamination audit (≥ 3 cases)

34. strategy source does not reference CAMPAIGN_002 / `trend_following` / `donchian` / `ema_fast` / `ema_slow` / `adx_threshold` keys
35. strategy source does not reference CAMPAIGN_010 / `session_breakout` / `asian_session_hours` / `london_session_hours` / `min_asian_range_atr_fraction` / `in_asian_window` / `in_london_window` keys
36. strategy source does not reference CAMPAIGN_011 / `random_entry_anchor` / `master_seed` / `entry_probability_per_bar` keys

### 6.8 Approval / safety regression (≥ 3 cases)

37. `configs/approved_strategies.yaml` remains `approved: []`
38. `configs/paper.yaml` does NOT enable `regime_switcher_atr_percentile`
39. `configs/practice.yaml` does NOT enable `regime_switcher_atr_percentile`
40. `RegimeSwitcherAtrPercentileStrategy` exposes no public attribute whose name contains `approve` / `approval` / `promote` / `promotion`

**Test-count target:** at least **30 tests** (per this sprint's prompt;
the discovery-003 spec required ≥ 25 — we aim higher). Full repo test
count: `771 → ≥ 801` after Phase 3.

## 7. Null-baseline comparison expectations (NOT enforced this sprint)

The future evidence sprint
(`research-regime-switcher-atr-percentile-walk-forward-001`) must
include a verdict-doc section comparing CAMPAIGN_012's per-fold +
aggregate metrics to CAMPAIGN_011's null-baseline floor per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md):

| metric | CAMPAIGN_011 floor | CAMPAIGN_012 must beat to count as "real edge" |
|---|---|---|
| aggregate expectancy R | −0.0024 | by ≥ +0.0524 (→ ≥ 0.05 R) |
| aggregate profit factor | 0.91 | by ≥ +0.19 (→ ≥ 1.10) |
| aggregate return (4 y) | −0.53 % | meaningfully positive (≥ +5 %) |
| `pairs_positive` | 3 / 7 | ≥ 4 / 7 |
| `fold_pass_rate` | 0 / 8 | 100 % |
| `single_fold_dominance` | 40.1 % | ≤ 60 % |

"Indistinguishable from null" REJECT band (within
±0.005 R / ±0.10 PF / ±2 pp / ±1 pair of CAMPAIGN_011): the verdict
doc must classify such an outcome as
**REJECT (indistinguishable from null)**, regardless of which
inherited gates technically pass.

**This sprint does not enforce or evaluate this comparison.** It only
codifies the rule into the binding precommit doc (Phase 4); the future
evidence sprint runs the comparison.

## 8. Strategy module structure (Phase 2 will implement)

| element | location | role |
|---|---|---|
| `RegimeSwitcherAtrPercentileStrategy` | `src/forex_bot/strategies/regime_switcher_atr_percentile.py` | implements the `Strategy` protocol |
| `_wilder_atr_over_d1agg(d1_candles, length) -> list[float]` | same module (private helper) | Wilder ATR-14 over the D1AGG mid OHLC |
| `_compute_regime(d1_atr_series, lookback_days, percentile_threshold)` | same module (private helper) | classifies HIGH-VOL vs LOW-VOL using a trailing window |
| `_df_to_completed_h4_candle_list(df, instrument)` | same module (private helper) | rebuilds `Candle` objects from a DataFrame for handing to `aggregate_h4_to_d1` |
| `_stable_signal_id(*parts)` | same module (private helper; copy of the pattern in `session_breakout.py` / `random_entry_anchor.py`) | SHA-1-based deterministic id |
| `RegimeSwitcherAtrPercentileStrategyConfig` | `src/forex_bot/config.py` | Pydantic v2 `BaseModel` with `model_config = ConfigDict(extra="forbid")` and `@model_validator(mode="after")` |
| `StrategyConfig.regime_switcher_atr_percentile` | `src/forex_bot/config.py` | optional nested config (`= None`) |
| enabled-list check | `StrategyConfig._check_enabled` | rejects `regime_switcher_atr_percentile` in `enabled` without the nested config |
| `__init__` re-export | `src/forex_bot/strategies/__init__.py` | adds `RegimeSwitcherAtrPercentileStrategy` to `__all__` |

Estimated total LOC: ~260 (strategy module) + ~45 (config edits) + ~10
(`__init__.py` edits). Tests file: ~700–900 LOC for ≥ 30 cases (mirrors
`test_random_entry_anchor.py` shape).

## 9. What this spec explicitly does NOT do

- Does not run any backtest.
- Does not run walk-forward, financing overlay, risk diagnostics, or
  verifier corroboration.
- Does not fetch data.
- Does not read `.env` or print credentials.
- Does not submit / query any broker call.
- Does not approve any strategy.
- Does not modify `configs/approved_strategies.yaml`.
- Does not edit any historical campaign verdict.
- Does not tune any parameter (the values in §2 are pre-committed
  pre-implementation; the strategy must use these exact values).
- Does not use CAMPAIGN_011 as a trading candidate (it is the null
  baseline ONLY).

## 10. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md) (Phase 0)
- [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
- [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- `src/forex_bot/backtesting/d1_aggregation.py`
- `src/forex_bot/strategies/session_breakout.py` (sibling reference)
- `src/forex_bot/strategies/random_entry_anchor.py` (sibling reference)
