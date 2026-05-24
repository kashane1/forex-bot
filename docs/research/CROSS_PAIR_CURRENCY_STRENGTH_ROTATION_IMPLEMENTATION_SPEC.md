# Cross-Pair Currency Strength Rotation — Implementation Spec (Phase 1)

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-001`
`strategy_evidence: false`

Phase 1 binding implementation spec for **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`**, the C6 cross-pair
currency-strength rotation candidate. **Spec only — no strategy code
written here.** The Phase 2 scaffold implementation, Phase 3 unit
tests, Phase 4 candidate YAML, and the future evidence sprint must
all conform to the rules below verbatim.

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. CAMPAIGN_011 is the **null
> baseline only**, not a trading candidate.

Sources of truth (all binding, conformant):

- [`NEXT_PREFERRED_DIRECTION_004.md`](NEXT_PREFERRED_DIRECTION_004.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (null-baseline gate)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md) (binding Patterns H–L)

## 1. Strategy hypothesis (verbatim, frozen)

> The G7 USD-denominated H4 universe contains 4 USD-base pairs
> (EUR_USD, GBP_USD, AUD_USD, NZD_USD) and 3 USD-quote pairs
> (USD_JPY, USD_CAD, USD_CHF). For each USD-base pair, the non-USD
> currency's relative-performance can be inferred from the H4
> close-to-close return. For each USD-quote pair, the non-USD
> currency's relative-performance is the inverse of the H4
> close-to-close return. Aggregating across all 7 pairs over a fixed
> rolling window yields a currency-strength rank for each of the 8
> currencies represented (USD plus the 7 others). The C6 hypothesis
> is that the strongest-vs-weakest currency rank gap predicts the
> direction of that pair over the next ~6 H4 bars, provided the
> rank gap exceeds a threshold large enough to overcome H4 cost
> drag.

## 2. Frozen parameters (binding — pre-commit-bound)

| parameter | value | role |
|---|---|---|
| `version` | `"0.1.0-c013"` | candidate id |
| `timeframe` | `"H4"` (default; literal `"H1" \| "H4" \| "D"`) | execution timeframe |
| `currency_strength_lookback_bars` | `24` | rolling window (≈ 4 trading days) for log returns |
| `rank_gap_threshold` | `4` | minimum `\|rank(quote) − rank(base)\|` to fire a signal (~half of 8-currency spectrum) |
| `atr_lookback` | `14` | H4 ATR for **stop sizing** (Wilder, via `forex_bot.strategies.indicators.atr`) |
| `atr_stop_multiple` | `2.0` | stop = `close[t] ± atr_stop_multiple × prior_atr_h4` |
| `max_bars_in_trade` | `6` | engine-enforced time stop (≈ 1 trading day) |
| `trailing_stop_atr_multiple` | `None` | **forbidden in v1**; rejected by validator |
| `min_atr_pips` | `{}` | per-pair ATR floor; default empty |
| `warmup_bars_required()` | `50` (effective) | covers `currency_strength_lookback_bars + 1 = 25` + `atr_lookback + 2 = 16` + slack |

**Any deviation from any value above constitutes a NEW candidate** that
requires its own discovery + design cycle. The runner / config loader
must reject any deviation.

## 3. Cross-pair universe + currency mapping (binding)

### 3.1 Universe (frozen)

```python
EXPECTED_PAIRS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)
```

### 3.2 Currency set + per-pair mapping

The 7-pair universe represents 8 currencies: `USD`, `EUR`, `GBP`,
`JPY`, `AUD`, `CAD`, `CHF`, `NZD`.

| pair | non-USD currency | sign convention for non-USD currency strength |
|---|---|---|
| EUR_USD | EUR | EUR strength **=** `+log_return(EUR_USD)` (USD-base pair: pair rises → EUR strengthens) |
| GBP_USD | GBP | GBP strength **=** `+log_return(GBP_USD)` |
| AUD_USD | AUD | AUD strength **=** `+log_return(AUD_USD)` |
| NZD_USD | NZD | NZD strength **=** `+log_return(NZD_USD)` |
| USD_JPY | JPY | JPY strength **=** `−log_return(USD_JPY)` (USD-quote pair: pair rises → USD strengthens → JPY weakens; invert sign) |
| USD_CAD | CAD | CAD strength **=** `−log_return(USD_CAD)` |
| USD_CHF | CHF | CHF strength **=** `−log_return(USD_CHF)` |

USD strength is the **negative mean of the 7 non-USD currency strengths**:

```python
strength["USD"] = -sum(
    strength[c] for c in ("EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD")
) / 7
```

This is the unique definition consistent with USD being on the other
side of every pair.

### 3.3 Log return computation (per pair, per bar `t`)

```python
import numpy as np

n = currency_strength_lookback_bars  # 24
# closes is the completed-only H4 close series for the pair
log_return = float(np.log(closes.iloc[-1]) - np.log(closes.iloc[-1 - n]))
```

**Both `closes.iloc[-1]` and `closes.iloc[-1 - n]` are closed bars.**
Fail-closed if either is non-finite / ≤ 0 or if the series is too
short.

## 4. R-rule table (binding)

Each rule returns `None` if its condition is not met. Only R8 emits a
`Signal`. Rules execute in order at the latest *completed* H4 bar `t`
taken from `ctx.candles.completed_only().df`.

### R1 — Warm-up

```python
df = ctx.candles.completed_only().df
if len(df) < self.warmup_bars_required():
    return None
```

`warmup_bars_required()` returns at least:

- `currency_strength_lookback_bars + 1 = 25` H4 bars (for `iloc[-1]` + `iloc[-1 - 24]` access)
- `atr_lookback + 2 = 16` H4 bars (for `prior_atr` at `iloc[-2]`)

→ pinned at **`50`** for safety (matches `regime_switcher` scaffold
convention of generous warm-up margin).

### R2 — Block re-entry while a position is open

```python
if any(
    not pos.is_flat and pos.instrument == ctx.instrument.name
    for pos in ctx.open_positions
):
    return None
```

Same rule as `session_breakout` R2 / `random_entry_anchor` R2 /
`regime_switcher_atr_percentile` R2; respects the engine's
single-instrument single-position invariant.

### R3 — Read sibling-pair H4 closes from `ctx.config["cross_pair_closes"]`

```python
cross_pair_closes = ctx.config.get("cross_pair_closes")
if cross_pair_closes is None:
    return None  # fail-closed: runner must supply
if set(cross_pair_closes.keys()) != set(EXPECTED_PAIRS):
    return None  # fail-closed: pair-set mismatch
```

**Binding integration contract.** The strategy NEVER reaches into
the engine / broker / loops / data layer directly; it relies on
`ctx.config` to receive the sibling-pair close series. The runner
(in the future evidence sprint) is responsible for:

1. Loading all 7 pairs' completed H4 candles for the relevant
   window + warm-up margin.
2. Aligning all 7 pairs to a common H4 timestamp index (intersection).
3. Building per-pair closes-only series indexed by the common index.
4. Injecting the dict `{pair: pd.Series}` into `strategy_config["cross_pair_closes"]`
   for each pair's engine invocation.

The Phase 3 unit tests will inject fixture series.

### R4 — Compute 8-currency strength scores

```python
import math
import numpy as np

def _log_return_n(closes, n: int) -> float | None:
    """Return log(close[-1] / close[-1-n]); None on insufficient/bad data."""
    if len(closes) <= n:
        return None
    last = float(closes.iloc[-1])
    prior = float(closes.iloc[-1 - n])
    if not (math.isfinite(last) and math.isfinite(prior)):
        return None
    if last <= 0 or prior <= 0:
        return None
    return float(np.log(last) - np.log(prior))

# Compute per-pair n-bar log returns:
n = self.currency_strength_lookback_bars  # 24
returns: dict[str, float] = {}
for pair in EXPECTED_PAIRS:
    r = _log_return_n(cross_pair_closes[pair], n)
    if r is None or not math.isfinite(r):
        return None  # R4 fail-closed
    returns[pair] = r

# Currency strength scores (8 currencies):
strength: dict[str, float] = {
    "EUR": +returns["EUR_USD"],
    "GBP": +returns["GBP_USD"],
    "AUD": +returns["AUD_USD"],
    "NZD": +returns["NZD_USD"],
    "JPY": -returns["USD_JPY"],
    "CAD": -returns["USD_CAD"],
    "CHF": -returns["USD_CHF"],
}
strength["USD"] = -sum(
    strength[c] for c in ("EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD")
) / 7
```

**Fail-closed conditions:** any pair's `_log_return_n` is `None` /
non-finite → return `None`. Insufficient history is a fail-closed
return, not an exception.

### R5 — Compute ranks + per-pair rank gap; pick side

```python
# Rank 1 = strongest, 8 = weakest. Sort descending by strength;
# ties broken by alphabetic currency code for determinism.
sorted_currencies = sorted(strength.items(), key=lambda kv: (-kv[1], kv[0]))
ranks = {c: r for r, (c, _) in enumerate(sorted_currencies, start=1)}

# For this strategy's instrument (the pair being evaluated):
base, quote = ctx.instrument.name.split("_")  # e.g. "EUR", "USD"
rank_gap = ranks[quote] - ranks[base]  # positive when base stronger than quote

if abs(rank_gap) < self.rank_gap_threshold:
    return None
side: str = "long" if rank_gap > 0 else "short"
```

**Binding invariants:**

- **Determinism.** Tie-breaking by alphabetic currency code ensures
  identical inputs produce identical ranks across runs / processes /
  pair iteration orders.
- **Rank gap interpretation.** `rank_gap = ranks[quote] - ranks[base]`
  is positive when base is stronger than quote (lower rank number =
  stronger). Long the base means buying base-vs-quote, i.e. the pair
  rises → consistent with the hypothesis.
- **Inclusivity at threshold.** `abs(rank_gap) < threshold` returns
  None; equality `abs(rank_gap) == threshold` passes. (Phase 3 unit
  test enforces.)

### R6 — Fail-closed on insufficient / non-finite H4 ATR (for stop sizing)

```python
from forex_bot.strategies.indicators import atr
atr_series_h4 = atr(df["high"], df["low"], df["close"], self.atr_lookback)
prior_atr = float(atr_series_h4.iloc[-2])
if not math.isfinite(prior_atr) or prior_atr <= 0:
    return None
```

Mirrors CAMPAIGN_010 R5 / CAMPAIGN_011 R5 / CAMPAIGN_012 R4 verbatim.
Bar `t-1`'s H4 ATR is used; bar `t`'s OHLC is **not** consulted for
this calculation.

### R7 — Stop placement

```python
from decimal import Decimal
last_close = float(df["close"].iloc[-1])
if side == "long":
    stop = last_close - self.atr_stop_multiple * prior_atr
else:
    stop = last_close + self.atr_stop_multiple * prior_atr
if stop == last_close:
    # Defense in depth — unreachable given prior_atr > 0 in R6.
    return None
stop_price = ctx.instrument.round_price(Decimal(str(stop)))
```

`close[t]` is used **only** for stop placement here; the entry
decision (side from R5; gate from R5's threshold) is fully determined
before `close[t]` is read for stop placement.

### R8 — Emit deterministic `Signal`

```python
import hashlib
from datetime import UTC
from typing import Any
import pandas as pd

idx_t = df.index[-1]
bar_timestamp_iso = pd.Timestamp(idx_t).tz_convert(UTC).isoformat()

signal_id = _stable_signal_id(
    self.name,         # "cross_pair_currency_strength_rotation"
    self.version,      # "0.1.0-c013"
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
    side=side,                  # "long" or "short"
    entry_intent="market",
    stop_model=f"ATR{atr_lookback}*{atr_stop_multiple}",
    stop_price=stop_price,
    exit_model="time_stop_only",
    features={
        "currency_strength_lookback_bars": int(currency_strength_lookback_bars),
        "rank_gap_threshold": int(rank_gap_threshold),
        "rank_gap": int(rank_gap),
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
        f"gap={rank_gap} (|gap| >= threshold={rank_gap_threshold})"
    ),
)
```

The `signal_id` is a SHA-1 of the canonical `"|"`-joined input string —
deterministic across runs and processes (no `hash()`, no PRNG).

## 5. No-lookahead safeguards (binding — Phase 3 unit tests will enforce)

| safeguard | enforcement |
|---|---|
| **`cross_pair_closes` is completed-only** | The runner (future evidence sprint) builds the dict from each pair's `completed_only().df` BEFORE invoking any pair's strategy. The strategy itself uses `ctx.candles.completed_only().df` for the focal pair. |
| **Log returns use `iloc[-1]` and `iloc[-1 - n]`** | Both are closed bars; structural-audit test asserts. |
| **Rank computation uses the trailing n-bar return only** | Not a global / full-sample rank; per-bar computation; helper is purely functional with no module-level state. |
| **No future bars** | The walk-forward harness drives the strategy bar-by-bar in chronological order; the runner aligns all pairs to the same `t` timestamp. |
| **H4 ATR uses `iloc[-2]`** | Matches CAMPAIGN_010 / 011 / 012 convention; bar `t-1`'s ATR. |
| **`close[t]` is read only in R7 (stop placement)** | R5 uses the *rank gap* (which is derived from cross-pair `cross_pair_closes`); R7 uses `df["close"].iloc[-1]` for the focal pair's stop level. Phase 3 source-grep test confirms. |
| **No bar-`t` reads of `high` / `low` / `open` / `volume`** | The strategy reads `df["high"]` / `df["low"]` only through `forex_bot.strategies.indicators.atr(...)` over the full series, then takes `.iloc[-2]`. No `iloc[-1]` is taken on those columns. Phase 3 source-grep test confirms. |
| **Strategy module imports nothing from `forex_bot.broker` / `.execution` / `.loops`** | Source-grep unit test. |
| **Strategy module does not import `random` / `numpy.random` / `secrets`** | Source-grep unit test. The strategy uses `numpy` for `log` only. |
| **Strategy module does not use builtin `hash()`** | Source-grep unit test. Only `hashlib.sha1` for signal-id derivation. |
| **Strategy module does not reference CAMPAIGN_002 / 010 / 011 / 012 strategy-specific parameter keys** | Source-grep unit test (binding per the addendum). |
| **Strategy does not mutate `ctx.config` during signal generation** | Phase 3 unit test diffs the config dict before/after the call. |
| **Strategy exposes no approval-shaped public attribute** | Phase 3 introspection test. |
| **Rank-gap computation is independent of pair iteration order** | Tie-breaking by alphabetic currency code; Phase 3 unit test verifies by permuting `cross_pair_closes` key order. |
| **Helper functions do not depend on global mutable state** | All helpers are pure; Phase 3 unit test verifies by calling helpers without any strategy instance / class state. |

## 6. Fail-closed rules (binding)

The strategy returns `None` (no signal; no exception) under any of:

| condition | rule |
|---|---|
| `len(df) < warmup_bars_required()` | R1 |
| `ctx.open_positions` already has an active position for the instrument | R2 |
| `cross_pair_closes` missing from `ctx.config` | R3 |
| `cross_pair_closes` keys don't match `EXPECTED_PAIRS` | R3 |
| any pair's `_log_return_n` returns None / non-finite | R4 |
| any pair's `close` is ≤ 0 | R4 (via `_log_return_n`) |
| any pair's close series is shorter than `n + 1 = 25` bars | R4 (via `_log_return_n`) |
| `|rank_gap| < rank_gap_threshold` | R5 |
| H4 ATR at `iloc[-2]` is NaN / non-finite / ≤ 0 | R6 |
| `stop == last_close` (defensive; unreachable given R6) | R7 |

The strategy **never raises an exception** on bad data. Consistent
with CAMPAIGN_010 / 011 / 012 convention.

## 7. Tests expected (Phase 3 — at least 40 deterministic unit tests)

The breakdown below is a *minimum*; Phase 3 may add more tests as
implementation needs surface. Section labels match the planned test
file structure.

### 7.1 Config defaults / validation (≥ 10 cases)

1. defaults match the frozen spec verbatim
2. rejects non-positive `currency_strength_lookback_bars`
3. rejects `rank_gap_threshold` below 1
4. rejects `rank_gap_threshold` above 7
5. rejects non-positive `atr_lookback`
6. rejects non-positive `atr_stop_multiple`
7. rejects non-positive `max_bars_in_trade`
8. rejects non-None `trailing_stop_atr_multiple` in v1
9. rejects extra fields (`extra="forbid"`)
10. `StrategyConfig._check_enabled` rejects missing nested config when `cross_pair_currency_strength_rotation` is in `enabled`

### 7.2 Pair parser / universe validation (≥ 2 cases)

11. parses `BASE_QUOTE` correctly (e.g. EUR_USD → ("EUR", "USD"))
12. rejects malformed pair names

### 7.3 Currency-strength mapping (≥ 4 cases)

13. USD-base pairs contribute positive sign to non-USD currency strength (e.g. EUR_USD rising → EUR strength positive)
14. USD-quote pairs contribute inverted sign to non-USD currency strength (e.g. USD_JPY rising → JPY strength negative)
15. USD strength = `−mean(non-USD strengths)`
16. Strength scores are deterministic for the same input

### 7.4 Rank computation (≥ 3 cases)

17. Ranks are deterministic (sorted descending; ties broken alphabetically)
18. Rank computation is independent of pair iteration order (permute `cross_pair_closes` key order; ranks unchanged)
19. Helper purely functional (no module-level mutable state)

### 7.5 Rank-gap rule (≥ 3 cases)

20. `|rank_gap| < threshold` → None
21. `|rank_gap| == threshold` → signal (inclusive at threshold)
22. `|rank_gap| > threshold` → signal

### 7.6 Side selection (≥ 2 cases)

23. base stronger than quote (positive `rank_gap`) → `long`
24. base weaker than quote (negative `rank_gap`) → `short`

### 7.7 Strategy core — R1 / R2 / R6 / R7 (≥ 4 cases)

25. R1: no signal before warm-up (`< 50` bars)
26. R2: no signal when position already open
27. R6: no signal when H4 ATR is NaN / non-finite / ≤ 0
28. R7: long-stop at `close[t] - 2 × prior_atr_h4`; short-stop at `close[t] + 2 × prior_atr_h4`

### 7.8 R3 / R4 fail-closed (≥ 5 cases)

29. R3: `cross_pair_closes` missing → None
30. R3: `cross_pair_closes` key-set mismatch → None
31. R4: any pair has insufficient lookback → None
32. R4: any pair's close is non-finite → None
33. R4: any pair's close is ≤ 0 → None

### 7.9 No-lookahead structural audit (≥ 4 cases)

34. source does NOT read `df["high"|"low"|"open"|"volume"].iloc[-1]`
35. source DOES read `df["close"].iloc[-1]` (R7 only)
36. signal id is deterministic across runs
37. strategy does not mutate `ctx.config` during signal generation

### 7.10 Forbidden imports / usages (≥ 3 cases)

38. no `import random` / `from random import` / `import secrets` / `from secrets`
39. no `import numpy.random` / `from numpy.random` / `np.random` / `numpy.random`
40. no `forex_bot.broker` / `forex_bot.execution` / `forex_bot.loops` imports
41. no builtin `hash()` for entry / signal-id derivation (only `hashlib.sha*`)

### 7.11 Rejected-family contamination audit (≥ 4 cases)

42. no CAMPAIGN_002 keys (donchian, ema_fast, ema_slow, adx_threshold, trend_following)
43. no CAMPAIGN_010 keys (asian_session_hours, london_session_hours, min_asian_range_atr_fraction, session_breakout, in_asian_window, in_london_window)
44. no CAMPAIGN_011 keys (master_seed, entry_probability_per_bar, random_entry_anchor)
45. no CAMPAIGN_012 keys (daily_atr_lookback, regime_lookback_days, regime_percentile_threshold, min_close_move_atr_fraction, trend_lookback_h4_bars, regime_switcher_atr_percentile)

### 7.12 Approval / safety regression (≥ 4 cases)

46. `configs/approved_strategies.yaml` remains `approved: []`
47. `configs/paper.yaml` does NOT enable `cross_pair_currency_strength_rotation`
48. `configs/practice.yaml` does NOT enable `cross_pair_currency_strength_rotation`
49. strategy class exposes no public attribute whose name contains `approve` / `approval` / `promote` / `promotion`

### 7.13 Signal emission shape (≥ 2 cases)

50. signal contains expected `features` dict keys (rank_gap, base/quote currencies/ranks, 8 strengths, prior_atr_h4, last_close)
51. signal `reason` string describes the cross-pair rotation

**Test-count target:** at least **40 tests** (per this sprint's
prompt; the discovery-004 design required ≥ 30). Aiming for **51
test functions** based on the breakdown above. Full repo test count:
`818 → ≥ 858` after Phase 3.

## 8. Null-baseline comparison expectations (NOT enforced this sprint)

The future evidence sprint
(`research-cross-pair-currency-strength-rotation-walk-forward-001`)
must include a verdict-doc section comparing CAMPAIGN_013's per-fold +
aggregate metrics to CAMPAIGN_011's null-baseline floor per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md):

| metric | CAMPAIGN_011 floor | CAMPAIGN_013 must beat to count as "real edge" |
|---|---|---|
| aggregate expectancy R | −0.0024 | by ≥ **+0.0524** (→ ≥ 0.05 R) |
| aggregate profit factor | 0.91 | by ≥ **+0.19** (→ ≥ 1.10) |
| aggregate return (4 y) | −0.53 % | meaningfully positive (≥ **+5 %**) |
| `pairs_positive` | 3 / 7 | ≥ **4 / 7** |
| `fold_pass_rate` | 0 / 8 | **100 %** |

"Indistinguishable from null" REJECT band: within
± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair of CAMPAIGN_011.

**This sprint does not enforce or evaluate this comparison.** It
only codifies the rule into the binding precommit doc (Phase 4); the
future evidence sprint runs the comparison.

## 9. Strategy module structure (Phase 2 will implement)

| element | location | role |
|---|---|---|
| `CrossPairCurrencyStrengthRotationStrategy` | `src/forex_bot/strategies/cross_pair_currency_strength_rotation.py` | implements the `Strategy` protocol |
| `EXPECTED_PAIRS` | module constant | the 7-pair universe |
| `_parse_pair(name)` | private helper | parses `"BASE_QUOTE"` → `("BASE", "QUOTE")`; raises `ValueError` on malformed |
| `_log_return_n(closes, n)` | private helper | computes `log(close[-1]/close[-1-n])`; None on bad data |
| `_compute_strength(returns)` | private helper | maps per-pair returns to 8-currency strength scores |
| `_compute_ranks(strength)` | private helper | sorts descending with alphabetic tiebreak; returns `{currency: rank}` |
| `_stable_signal_id(*parts)` | private helper | SHA-1-based deterministic id (mirrors session_breakout / random_entry_anchor / regime_switcher) |
| `CrossPairCurrencyStrengthRotationStrategyConfig` | `src/forex_bot/config.py` | Pydantic v2 `BaseModel` with `model_config = ConfigDict(extra="forbid")` and `@model_validator(mode="after")` |
| `StrategyConfig.cross_pair_currency_strength_rotation` | `src/forex_bot/config.py` | optional nested config (`= None`) |
| enabled-list check | `StrategyConfig._check_enabled` | rejects `cross_pair_currency_strength_rotation` in `enabled` without the nested config |
| `__init__` re-export | `src/forex_bot/strategies/__init__.py` | adds `CrossPairCurrencyStrengthRotationStrategy` to `__all__` |

Estimated total LOC: ~280 (strategy module) + ~50 (config edits) +
~5 (`__init__.py` edits). Tests file: ~900–1100 LOC for ≥ 40 cases.

## 10. What this spec explicitly does NOT do

- Does not run any backtest.
- Does not run walk-forward / financing / risk / verifier evidence.
- Does not fetch data.
- Does not read `.env` or print credentials.
- Does not submit / query any broker call.
- Does not approve any strategy.
- Does not modify `configs/approved_strategies.yaml`.
- Does not edit any historical campaign verdict.
- Does not tune any parameter (the values in §2 are pre-committed
  pre-implementation; the strategy must use these exact values).
- Does not use CAMPAIGN_011 as a trading candidate (null baseline only).
- Does not implement the cross-pair runner (that is the future
  evidence sprint's deliverable; this spec only documents the
  integration contract in §4 R3).

## 11. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md) (Phase 0)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md) (binding design)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md) (binding scaffold spec)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md) (future evidence sprint's cross-pair runner integration contract)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- `src/forex_bot/strategies/regime_switcher_atr_percentile.py` (sibling reference for Phase 2 implementation)
