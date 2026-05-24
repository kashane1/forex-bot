# Next Preferred Candidate — Implementation & Evaluation Design (Sprint 004)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-004`
`strategy_evidence: false`

Phase 6 detailed implementation + evaluation design for **C6 —
`cross_pair_currency_strength_rotation 0.1.0-c013` (CAMPAIGN_013)**
per the Phase 5 selection in
[`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md).
**This design is binding for the future scaffold + evidence sprints;
no strategy code is written here.**

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
> CAMPAIGN_012 remain REJECT. `configs/approved_strategies.yaml`
> remains `approved: []`. **CAMPAIGN_013 cannot be approved by this
> sprint or by either the future scaffold sprint or the future
> evidence sprint.** Approval requires the full six-evidence ladder +
> a deliberate human approval action per
> [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 1. Strategy hypothesis (verbatim, frozen)

> The G7 USD-denominated H4 universe contains 4 USD-base pairs
> (EUR_USD, GBP_USD, AUD_USD, NZD_USD) and 3 USD-quote pairs
> (USD_JPY, USD_CAD, USD_CHF). For each USD-base pair, the
> non-USD currency's relative-performance can be inferred from
> the H4 close-to-close return. For each USD-quote pair, the
> non-USD currency's relative-performance is the inverse of the
> H4 close-to-close return. Aggregating across all 7 pairs over
> a fixed rolling window yields a **currency-strength rank**
> for each of the 8 currencies represented (USD plus the 7
> others). The C6 hypothesis is that the strongest-vs-weakest
> currency rank gap predicts the direction of *that pair* over
> the next ~6 H4 bars, *provided the rank gap exceeds a
> threshold large enough to overcome H4 cost drag*. CAMPAIGN_011
> demonstrated that random entry on this universe + cost model
> is essentially flat. CAMPAIGN_012 demonstrated that a single-
> pair vol-percentile regime gate does not produce edge. C6
> tests a *cross-pair* signal — fundamentally different
> mechanism — to see whether structural relative-strength
> persistence is recoverable from H4 data on the same cost
> model.

## 2. Universe + timeframe + data requirements

| dimension | value |
|---|---|
| universe (frozen) | `["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"]` |
| timeframe (execution) | H4 |
| timeframe (signal feature) | H4 (no D1AGG required — the cross-pair rank is H4-only) |
| data source | local SQLite store at `data/campaign_002.sqlite3` (gitignored symlink — matches CAMPAIGN_010 / 011 / 012) |
| required source label | `oanda-practice` (runner-enforced) |
| data span | 2020-01-01 → 2026-05-19 inclusive (matches CAMPAIGN_010 / 011 / 012) |
| new data fetch needed? | **no** |
| new credentials needed? | **no** |
| new external dependency? | **no** |

## 3. Currency-strength feature definition (binding)

### 3.1 Currencies and pair → currency mapping

The 7-pair universe represents 8 currencies: `USD`, `EUR`, `GBP`,
`JPY`, `AUD`, `CAD`, `CHF`, `NZD`.

Per-pair → non-USD currency:

| pair | non-USD currency | sign convention |
|---|---|---|
| EUR_USD | EUR | EUR strengthens when pair rises (USD-base pair) |
| GBP_USD | GBP | GBP strengthens when pair rises |
| AUD_USD | AUD | AUD strengthens when pair rises |
| NZD_USD | NZD | NZD strengthens when pair rises |
| USD_JPY | JPY | JPY strengthens when pair **falls** (USD-quote pair; invert sign) |
| USD_CAD | CAD | CAD strengthens when pair **falls** (invert sign) |
| USD_CHF | CHF | CHF strengthens when pair **falls** (invert sign) |

USD strength is the **negative mean** of the 7 non-USD currency
returns (since USD is on the other side of every pair). This is
equivalent to defining USD strength as `−sum(currency_strength[c]
for c in non-USD-currencies) / 7`.

### 3.2 Rolling-window currency-strength score

Let `n = currency_strength_lookback_bars` (frozen at **24** — see §5).

For each completed H4 bar `t` (taken from
`ctx.candles.completed_only().df`):

```python
# Per-pair n-bar return (close-to-close, log return for additive
# aggregation):
import numpy as np
ret_h4[t, pair] = np.log(close[t, pair]) - np.log(close[t - n, pair])

# Per-currency strength score (signed n-bar return aggregated across
# pairs where the currency appears):
strength[t, "EUR"] = ret_h4[t, "EUR_USD"]
strength[t, "GBP"] = ret_h4[t, "GBP_USD"]
strength[t, "AUD"] = ret_h4[t, "AUD_USD"]
strength[t, "NZD"] = ret_h4[t, "NZD_USD"]
strength[t, "JPY"] = -ret_h4[t, "USD_JPY"]  # invert (USD-quote)
strength[t, "CAD"] = -ret_h4[t, "USD_CAD"]
strength[t, "CHF"] = -ret_h4[t, "USD_CHF"]
strength[t, "USD"] = -sum(strength[t, c] for c in non_usd) / 7

# Rank (1 = strongest, 8 = weakest):
ranks = {c: rank for rank, c in
         enumerate(sorted(strength[t].items(), key=lambda kv: -kv[1]), start=1)}
```

### 3.3 Pair signal from currency ranks

For each pair, the signal is computed from the rank gap between its
two currencies:

```python
def pair_signal(pair: str, ranks: dict[str, int],
                rank_gap_threshold: int) -> str | None:
    base, quote = pair.split("_")
    gap = ranks[quote] - ranks[base]  # positive if base stronger than quote
    if abs(gap) < rank_gap_threshold:
        return None
    return "long" if gap > 0 else "short"
```

**Example:** if `EUR` ranks 1 (strongest) and `USD` ranks 8 (weakest),
then for `EUR_USD`: `gap = ranks["USD"] - ranks["EUR"] = 8 - 1 = 7`.
Signal: `long` (buy EUR, sell USD) — the pair is expected to rise.

## 4. R1–R8 signal rules (binding)

The strategy's `generate_signal(ctx) -> Signal | None` MUST implement
the following 8 rules in order. Each rule returns `None` if its
condition is not satisfied; only R8 emits a `Signal`.

### R1 — Warm-up

```python
df = ctx.candles.completed_only().df
if len(df) < self.warmup_bars_required():
    return None
```

`warmup_bars_required()` returns at least `max(currency_strength_lookback_bars + 1, atr_lookback + 2)` = `max(25, 16)` = **25**. Pinned at **50** for safety (matches CAMPAIGN_010 / 011 / 012 convention of generous warm-up margin).

### R2 — Block re-entry while a position is open

```python
if any(
    not pos.is_flat and pos.instrument == ctx.instrument.name
    for pos in ctx.open_positions
):
    return None
```

Mirrors CAMPAIGN_010 / 011 / 012 R2 and the engine's single-instrument single-position invariant.

### R3 — Read sibling-pair H4 closes from shared context

```python
# The runner provides cross_pair_closes via ctx.config["cross_pair_closes"]:
#   {pair: pd.Series of completed H4 closes ending at t-1 inclusive}
# This is the binding integration contract between the strategy and
# the per-bar runner. The runner ensures all 7 pairs' close-only
# series are aligned to the same H4 bar timestamps (resampled to a
# common index) before the strategy is invoked.
cross_pair_closes = ctx.config.get("cross_pair_closes")
if cross_pair_closes is None:
    return None  # fail-closed: runner must supply
if set(cross_pair_closes.keys()) != set(EXPECTED_PAIRS):
    return None  # fail-closed: pair-set mismatch
```

**Binding invariant.** The strategy NEVER reaches into the engine /
broker / loops / data layer directly; it relies on `ctx.config` to
receive the sibling-pair close series. The Phase 3 unit tests will
inject fixture series for testing.

### R4 — Compute the 8-currency strength scores

```python
import numpy as np

def _log_return_n(closes: pd.Series, n: int) -> float | None:
    if len(closes) <= n:
        return None
    try:
        return float(np.log(closes.iloc[-1]) - np.log(closes.iloc[-1 - n]))
    except (ValueError, FloatingPointError):
        return None

strength: dict[str, float] = {}
for pair, ret in [
    ("EUR_USD", _log_return_n(cross_pair_closes["EUR_USD"], n)),
    ...
]:
    if ret is None or not math.isfinite(ret):
        return None  # R4 fail-closed

strength["EUR"] = ret_EUR_USD
strength["GBP"] = ret_GBP_USD
strength["AUD"] = ret_AUD_USD
strength["NZD"] = ret_NZD_USD
strength["JPY"] = -ret_USD_JPY
strength["CAD"] = -ret_USD_CAD
strength["CHF"] = -ret_USD_CHF
strength["USD"] = -sum(strength[c] for c in ("EUR", "GBP", "AUD", "NZD", "JPY", "CAD", "CHF")) / 7
```

**Fail-closed conditions:** any pair's `_log_return_n` is `None` /
non-finite → return `None`. Insufficient history is a fail-closed
return, not a raise.

### R5 — Compute ranks and the current-pair gap

```python
sorted_strength = sorted(strength.items(), key=lambda kv: -kv[1])
ranks = {c: r for r, (c, _) in enumerate(sorted_strength, start=1)}

base, quote = ctx.instrument.name.split("_")
gap = ranks[quote] - ranks[base]
if abs(gap) < self.rank_gap_threshold:
    return None
side: str = "long" if gap > 0 else "short"
```

### R6 — Fail-closed on insufficient / non-finite H4 ATR (for stop sizing)

```python
from forex_bot.strategies.indicators import atr
atr_series_h4 = atr(df["high"], df["low"], df["close"], self.atr_lookback)
prior_atr = float(atr_series_h4.iloc[-2])
if not math.isfinite(prior_atr) or prior_atr <= 0:
    return None
```

Mirrors CAMPAIGN_010 R5 / CAMPAIGN_011 R5 / CAMPAIGN_012 R4 verbatim.

### R7 — Stop placement

```python
last_close = float(df["close"].iloc[-1])
if side == "long":
    stop = last_close - self.atr_stop_multiple * prior_atr
else:
    stop = last_close + self.atr_stop_multiple * prior_atr
if stop == last_close:
    return None  # defensive
```

`close[t]` is used for stop placement only; the entry decision (side
from R5; gate from R5's threshold) is fully determined before
`close[t]` is consulted.

### R8 — Emit deterministic `Signal`

```python
import hashlib
from datetime import UTC
import pandas as pd
from decimal import Decimal

idx_t = df.index[-1]
bar_timestamp_iso = pd.Timestamp(idx_t).tz_convert(UTC).isoformat()
signal_id = _stable_signal_id(
    self.name,                 # "cross_pair_currency_strength_rotation"
    self.version,              # "0.1.0-c013"
    ctx.instrument.name,
    timeframe,
    bar_timestamp_iso,
    side,
)
return Signal(
    signal_id=signal_id,
    strategy_name="cross_pair_currency_strength_rotation",
    strategy_version="0.1.0-c013",
    instrument=ctx.instrument.name,
    timeframe=timeframe,
    timestamp=pd.Timestamp(idx_t).tz_convert(UTC).to_pydatetime(),
    side=side,
    entry_intent="market",
    stop_model=f"ATR{atr_lookback}*{atr_stop_multiple}",
    stop_price=ctx.instrument.round_price(Decimal(str(stop))),
    exit_model="time_stop_only",
    features={
        "currency_strength_lookback_bars": int(self.currency_strength_lookback_bars),
        "rank_gap_threshold": int(self.rank_gap_threshold),
        "rank_gap": int(gap),
        "base_currency": base,
        "quote_currency": quote,
        "base_rank": int(ranks[base]),
        "quote_rank": int(ranks[quote]),
        "prior_atr_h4": float(prior_atr),
        "last_close": float(last_close),
        "strength_EUR": float(strength["EUR"]),
        "strength_GBP": float(strength["GBP"]),
        "strength_USD": float(strength["USD"]),
        "strength_JPY": float(strength["JPY"]),
        "strength_AUD": float(strength["AUD"]),
        "strength_CAD": float(strength["CAD"]),
        "strength_CHF": float(strength["CHF"]),
        "strength_NZD": float(strength["NZD"]),
    },
    reason=(
        f"Cross-pair currency strength rotation {side}: "
        f"{base}(rank={ranks[base]}) vs {quote}(rank={ranks[quote]}) "
        f"gap={gap} >= threshold={self.rank_gap_threshold}"
    ),
)
```

## 5. Frozen parameter set (binding pre-commit; pre-implementation)

| parameter | value | rationale |
|---|---|---|
| `version` | `"0.1.0-c013"` | candidate id |
| `timeframe` | `"H4"` | execution timeframe |
| `currency_strength_lookback_bars` | **24** | 24 H4 bars = ~4 trading days (96 hours); long enough to filter noise, short enough to remain responsive to regime shifts |
| `rank_gap_threshold` | **4** | requires the base / quote currency rank gap to span at least half the 8-currency spectrum; informally "top-half vs bottom-half" — chosen pre-implementation from independent reasoning (a quartile-style band, not a result-fit) |
| `atr_lookback` | **14** | project-standard exit-sizing constant (matches CAMPAIGN_010 / 011 / 012) |
| `atr_stop_multiple` | **2.0** | project-standard exit-sizing constant (matches CAMPAIGN_010 / 011 / 012) |
| `max_bars_in_trade` | **6** | engine-enforced time stop (≈ 1 trading day; matches CAMPAIGN_010 / 011 / 012) |
| `trailing_stop_atr_multiple` | `null` | forbidden in v1; validator rejects non-None |
| `min_atr_pips` | `{}` | per-pair ATR floor; default empty |

**Any deviation from any value above constitutes a NEW candidate**
that requires its own discovery + design cycle. The runner / config
loader must reject any deviation.

**`currency_strength_lookback_bars = 24` and `rank_gap_threshold = 4`
are chosen here in this Phase 6 from independent reasoning, BEFORE
any code, BEFORE any backtest, BEFORE any view of CAMPAIGN_011 / 012
output.** Sweeping or "tuning" these to improve the result is the
canonical overfitting anti-pattern (Pattern G in the base guardrails).

## 6. No-lookahead rules (binding)

| safeguard | enforcement |
|---|---|
| **Cross-pair closes are completed-only** | The runner builds `cross_pair_closes` from each pair's `completed_only().df` BEFORE invoking any pair's strategy. Phase 3 unit test asserts the strategy's `_log_return_n` cannot reach incomplete bars. |
| **Log returns use `iloc[-1]` and `iloc[-1 - n]`** | Both are closed bars; n bars back; structural-audit test asserts. |
| **No future bars** | The walk-forward harness drives the strategy bar-by-bar in chronological order; the runner aligns all pairs to the same `t` timestamp. |
| **Rank computation uses the trailing n-bar return only** | Not a global rank; per-bar computation; no module-level cache; helper is purely functional. |
| **Per-pair signal uses the pair's own `close[t]` for stop placement only** | R7; close[t] is read only for stop placement. The entry decision (rank gap → side) is fully determined by R3–R5 before close[t] is consulted. |
| **H4 ATR uses `iloc[-2]`** | Matches CAMPAIGN_010 / 011 / 012 convention; bar `t-1`'s ATR. |
| **No bar-`t` reads of `high` / `low` / `open` / `volume`** | Phase 3 source-grep test forbids `df["high"|"low"|"open"|"volume"].iloc[-1]`. |
| **Strategy module imports nothing from `forex_bot.broker` / `.execution` / `.loops`** | Source-grep unit test. |
| **Strategy module does not import `random` / `numpy.random` / `secrets`** | Source-grep unit test. Uses `numpy` for `log` only. |
| **Strategy module does not reference CAMPAIGN_002 / 010 / 011 / 012 strategy-specific parameter keys** | Source-grep unit test (binding from the addendum). |
| **Strategy does not mutate `ctx.config` during signal generation** | Phase 3 unit test diffs config dict. |
| **Strategy exposes no approval-shaped public attribute** | Phase 3 introspection test. |

## 7. Missing-data behavior

The strategy returns `None` (no signal; no exception) under any of:

| condition | rule |
|---|---|
| `len(df) < warmup_bars_required()` | R1 |
| `ctx.open_positions` already has an active position for the instrument | R2 |
| `cross_pair_closes` missing from `ctx.config` | R3 |
| `cross_pair_closes` keys don't match `EXPECTED_PAIRS` | R3 |
| any pair's `_log_return_n` is None / non-finite | R4 |
| `|gap| < rank_gap_threshold` | R5 |
| H4 ATR at `iloc[-2]` is NaN / non-finite / ≤ 0 | R6 |
| `stop == last_close` (defensive; unreachable given R6) | R7 |

The strategy **never raises** on bad data. Consistent with CAMPAIGN_010 / 011 / 012 convention.

## 8. Config schema needs

Add to `src/forex_bot/config.py`:

```python
class CrossPairCurrencyStrengthRotationStrategyConfig(BaseModel):
    """Frozen-parameter config for the cross_pair_currency_strength_rotation
    research candidate (CAMPAIGN_013)."""
    model_config = ConfigDict(extra="forbid")
    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    currency_strength_lookback_bars: int = 24
    rank_gap_threshold: int = 4
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = None
    max_bars_in_trade: int = 6
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> CrossPairCurrencyStrengthRotationStrategyConfig:
        if self.currency_strength_lookback_bars < 2:
            raise ConfigError("currency_strength_lookback_bars must be >= 2")
        if self.rank_gap_threshold < 1 or self.rank_gap_threshold > 7:
            raise ConfigError("rank_gap_threshold must be in [1, 7]")
        if self.atr_lookback < 2:
            raise ConfigError("atr_lookback must be >= 2")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        if self.max_bars_in_trade < 1:
            raise ConfigError("max_bars_in_trade must be >= 1")
        if self.trailing_stop_atr_multiple is not None:
            raise ConfigError(
                "trailing_stop_atr_multiple must be None in v1 — "
                "the cross-pair rotator uses time-stop only"
            )
        return self
```

Add to `StrategyConfig`:

```python
cross_pair_currency_strength_rotation: (
    CrossPairCurrencyStrengthRotationStrategyConfig | None
) = None
```

Plus the enabled-list check.

## 9. Strategy module location

`src/forex_bot/strategies/cross_pair_currency_strength_rotation.py` —
implements the `Strategy` protocol. Estimated size: ~280 LOC (signal
computation + helpers + `_stable_signal_id`).

Add to `src/forex_bot/strategies/__init__.py`:

```python
from forex_bot.strategies.cross_pair_currency_strength_rotation import (
    CrossPairCurrencyStrengthRotationStrategy,
)
```

## 10. Tests required (`tests/unit/test_cross_pair_currency_strength_rotation.py`)

Minimum **30 cases** covering:

- **Config defaults / validation** (≥ 8): defaults match the frozen spec; rejects invalid bounds (`currency_strength_lookback_bars`, `rank_gap_threshold` in [1, 7], `atr_lookback`, `atr_stop_multiple`, `max_bars_in_trade`, non-None `trailing_stop_atr_multiple`); rejects extra fields; `StrategyConfig._check_enabled` rejects missing nested config.
- **Currency-strength feature — happy path** (≥ 4): EUR strongest + USD weakest → EUR_USD long; USD strongest + JPY weakest → USD_JPY long; rank gap exactly = threshold passes (inclusive at threshold); rank gap < threshold returns None.
- **Currency-strength feature — sign convention** (≥ 3): USD-base pair returns map to base-currency strength positively; USD-quote pair returns invert (positive USD_JPY return → JPY weaker → JPY rank deeper); USD strength = `−mean(non-USD strengths)`.
- **R1 / R2 / R3 / R4 / R6 / R7 / R8 fixtures** (≥ 7): warm-up; open position; missing `cross_pair_closes`; pair-set mismatch; non-finite log return; H4 ATR <= 0; stop placement long/short.
- **No-lookahead structural audit** (≥ 4): source does not read `df["high"|"low"|"open"|"volume"].iloc[-1]`; reads `df["close"].iloc[-1]` only in R7; deterministic signal id; no config mutation.
- **Forbidden imports / usages** (≥ 3): no `random` / `numpy.random` / `secrets`; no builtin `hash()`; no `forex_bot.broker` / `.execution` / `.loops` imports.
- **Rejected-family contamination audit** (≥ 4): no CAMPAIGN_002 keys (donchian, ema_*, adx_threshold, trend_following); no CAMPAIGN_010 keys (asian_session_hours, london_session_hours, min_asian_range_atr_fraction, session_breakout); no CAMPAIGN_011 keys (master_seed, entry_probability_per_bar, random_entry_anchor); no CAMPAIGN_012 keys (daily_atr_lookback, regime_lookback_days, regime_percentile_threshold, min_close_move_atr_fraction, trend_lookback_h4_bars, regime_switcher_atr_percentile).
- **Approval / safety regression** (≥ 4): `approved_strategies.yaml` still `approved: []`; `cross_pair_currency_strength_rotation` NOT in `configs/paper.yaml` / `configs/practice.yaml`; strategy class exposes no approval-shaped public attribute.

**Test-count target:** 818 baseline → **≥ 848 after scaffold Phase 3**.

## 11. Walk-forward requirements

Inherited verbatim from CAMPAIGN_010 / 011 / 012:

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
| expected fold count | **8** |

### 11.1 Per-fold gates (inherited verbatim)

| level | gate | threshold |
|---|---|---|
| test fold | `expectancy_R_net_of_stress_financing` | ≥ 0.05 R |
| test fold | `profit_factor_net_of_stress_financing` | ≥ 1.10 |
| test fold | `pairs_positive_net_of_stress_financing` | ≥ 4 of 7 |
| test fold | `trade_count` | ≥ 30 |
| test fold | `single_pair_dominance` | ≤ 60 % |

### 11.2 Aggregate gates (inherited)

Same as CAMPAIGN_010 / 011 / 012 §10.2 (8 gates total). Plus the
null-baseline comparison gate (binding):

## 12. Null-baseline comparison (binding; CAMPAIGN_011-derived)

| metric | CAMPAIGN_011 floor | CAMPAIGN_013 must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 | by ≥ **+0.0524** |
| aggregate profit factor | 0.91 | by ≥ **+0.19** |
| aggregate return % (4 y) | −0.53 % | meaningfully positive (≥ **+5 %**) |
| `pairs_positive` | 3 / 7 | ≥ **4 / 7** |
| `fold_pass_rate` | 0 / 8 | **100 %** |

"Indistinguishable from null" REJECT band: ± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair.

## 13. Financing requirements

- **Expected holding period.** ≤ 6 H4 bars (matches CAMPAIGN_010 / 011 / 012).
- **ESTIMATED + conservative stress** — the only authorized source.
- **MODELED remains refused at four layers.**
- **Whether financing flips the verdict.** Required to pass the `conservative_stress_run_does_not_flip_verdict` gate.

Note: cross-pair rotation creates *systematic* long/short balance
(e.g. long EUR_USD usually implies short USD_JPY when EUR is strong
and JPY is weak). The financing overlay must record this balance —
expected to be approximately neutral on net, but the per-pair financing
recording must still pass.

## 14. Portfolio-risk diagnostics

| diagnostic | expected value |
|---|---|
| max concurrent open positions per instrument | 1 (engine-enforced) |
| per-pair trade count | depends on rank-gap frequency; could be uneven across pairs (some pair gaps may rarely exceed threshold) |
| aggregate notional | bounded by `risk_per_trade_pct = 0.25 %` |
| pair concentration | informational; gate ≤ 40 % aggregate; cross-pair rotation may produce *high concentration* on certain pairs if currency-strength persists |
| **rank-gap clustering** | trades cluster when rank gaps are extreme (e.g. major macro events); the diagnostics doc must report rank-gap distribution |
| **cross-pair concurrent exposure** | informational only — engine enforces 1-per-pair, but the runner's multi-pair loop may produce *concurrent positions across 2–7 pairs simultaneously* (e.g. long EUR_USD + short USD_JPY + short USD_CAD when EUR/JPY/CAD ranks diverge from USD); RiskEngine's `max_open_positions = 1` will cap this — **possibly producing severe rejection rates that depress trade count** |
| session-of-day distribution | informational |
| RiskEngine rejection profile | same spread + session filters as CAMPAIGN_010 / 011 / 012 |

### 14.1 Risk-engine concurrency note (IMPORTANT)

The CAMPAIGN_013 config will inherit
`risk.max_open_positions = 1`. Cross-pair rotation naturally
generates *multiple simultaneous signals* (3–5 pairs may signal at
the same H4 bar). With `max_open_positions = 1`, only the first-
encountered pair's signal would fill; subsequent signals would be
rejected as `MAX_OPEN_POSITIONS_EXCEEDED` (or whatever the engine's
rejection code is — Phase 7 evidence sprint will discover this).

**This is a known behavior, NOT a bug to fix.** The evidence sprint
records the rejection rate honestly and does not relax
`max_open_positions` to "rescue" the trade count. If C6 cannot
produce enough trades under the existing risk cap to clear the
`trade_count_min = 200` aggregate gate, that itself is part of the
research evidence (the candidate is operationally infeasible under
the project's current risk envelope).

## 15. Independent-verifier requirements

- **Verifier extension is not required for the REJECT verdict.** Item 5 of the six-evidence ladder is a paper-promotion gate.
- **Verifier extension is REQUIRED for a paper-promotion verdict.** If CAMPAIGN_013 unexpectedly passes every gate, `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001` must run before any human approval consideration.
- **Verifier scope** (if/when required): independently re-implement the currency-strength rank computation; compare per-pair-per-fold trade counts within WARN-band tolerances.

## 16. Rejection criteria before paper/demo consideration

CAMPAIGN_013's verdict is **REJECT** if any of:

| level | criterion |
|---|---|
| any per-fold | any gate from §11.1 fails on any test fold |
| aggregate | any gate from §11.2 fails |
| financing | conservative-stress overlay flips a passing verdict |
| null-baseline | metrics cluster within ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair of CAMPAIGN_011 |
| no-lookahead | any structural-audit unit test fails |
| pipeline | the runner aborts before completion (BLOCKED) |

If verdict is **PASS** on every gate AND meets meaningful-improvement-over-null:

- Verdict classified `RESEARCH_PASS_UNAPPROVED` (not approved; awaiting human action).
- Verifier extension via `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001` required for paper consideration.
- Human approval per `STRATEGY_APPROVAL_PROCESS.md` remains required.

## 17. Required artifacts (committed by the future evidence sprint)

The future
`research-cross-pair-currency-strength-rotation-walk-forward-001`
evidence sprint must commit:

- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/plan.{json,md}`
- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.{json,md}`
- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/fold_detail.json`
- per-fold per-pair `summary.json` + `trades.csv`
- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/*`
- `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/risk/*`
- `docs/research/CAMPAIGN_013_DATA_PROVENANCE.md`
- `docs/research/CAMPAIGN_013_WALK_FORWARD_PLAN.md`
- `docs/research/CAMPAIGN_013_WALK_FORWARD_EXECUTION.md`
- `docs/research/CAMPAIGN_013_WALK_FORWARD_RESULT.md` (with null-baseline section)
- `docs/research/CAMPAIGN_013_FINANCING_OVERLAY.md`
- `docs/research/CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`
- `docs/research/CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`
- `docs/research/CAMPAIGN_013_EVIDENCE_SUMMARY.md`
- `docs/research/CAMPAIGN_013_STATUS.md` (updated)
- `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md`

## 18. Future scaffold sprint cannot approve

Forbidden in the future scaffold sprint:

- Adding `cross_pair_currency_strength_rotation` to `configs/approved_strategies.yaml`.
- Running `paper-loop` / `demo-loop` against the candidate's config.
- Creating any `live-loop` command.
- Changing any frozen parameter from §5.
- Modifying any rejected-family strategy module.

## 19. Future evidence sprint cannot approve

Same as §18. Even a clean PASS produces `RESEARCH_PASS_UNAPPROVED`.

## 20. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 818 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |

## 21. Pre-flight checklist for the future scaffold sprint

- [ ] Repo state clean.
- [ ] `configs/approved_strategies.yaml` reads `approved: []`.
- [ ] CAMPAIGN_002 / 010 / 011 / 012 verdicts unchanged.
- [ ] 818 pytests pass (Phase 0 baseline).
- [ ] 3 pre-existing ruff findings (unchanged).
- [ ] Archive validator + freeze checker + secret scanner PASS.
- [ ] Loops refuse; no `live-loop`.
- [ ] No `cross_pair_currency_strength_rotation.py` exists yet.
- [ ] No `CrossPairCurrencyStrengthRotationStrategyConfig` in `src/forex_bot/config.py`.
- [ ] No `backtests/CAMPAIGN_013_*` artifact directory.
- [ ] All Phase 5 (this) frozen parameter values match the pre-commit verbatim.

## 22. Cross-links

- [`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md) (Phase 5 selection)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md) (Phase 4 shortlist)
- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md) (off-limits surface)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) (binding patterns)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md) (gate vector inherited)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md) (same gate vector)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md) (same gate vector)
- `src/forex_bot/strategies/random_entry_anchor.py` (Strategy protocol reference)
- `src/forex_bot/strategies/regime_switcher_atr_percentile.py` (Strategy protocol reference)
