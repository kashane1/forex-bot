# Random-Entry Diagnostic Anchor — Implementation Spec

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-001`
`strategy_evidence: false`

Phase 1 machine-facing implementation specification for
**CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011`**. This is the
binding spec the Phase 2 strategy module + config + the Phase 3
unit tests must satisfy. **No strategy code is written in this
phase; this document fixes the contract.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_011 is a null model — cannot be
> approved by design.**

## 1. Candidate identity (frozen)

| field | value |
|---|---|
| campaign label | `CAMPAIGN_011` |
| strategy name | `random_entry_anchor` |
| version | `0.1.0-c011` |
| role | **diagnostic anchor / null model** (NOT a paper candidate) |
| timeframe | `H4` |
| universe (7 pairs) | `EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD` |
| approval path | **none** (null model by design) |

## 2. Hypothesis (verbatim, frozen)

> A deterministic-seed coin-flip H4 entry on the 7-pair OANDA
> practice universe, executed under the same RiskEngine gates
> and the same ATR-stop / time-stop exit logic as CAMPAIGN_010,
> has *no edge by construction*. Its per-fold and aggregate
> expectancy under rolling walk-forward will set the
> falsifiability bar that every subsequent candidate must beat.
> The headline gate vector is inherited verbatim from
> CAMPAIGN_010's pre-commit so the comparison is on the entry
> signal alone, not on a shifted goalpost.

## 3. Frozen parameters (verbatim — pre-commit-bound)

| parameter | value | type |
|---|---|---|
| `version` | `"0.1.0-c011"` | `str` |
| `timeframe` | `"H4"` | `Literal["H1", "H4", "D"]` |
| `master_seed` | `20260523` | `int` |
| `entry_probability_per_bar` | `0.05` | `float` ∈ (0, 1) |
| `atr_lookback` | `14` | `int` ≥ 2 |
| `atr_stop_multiple` | `2.0` | `float` > 0 |
| `trailing_stop_atr_multiple` | `None` | `float | None` (must be `None` in v1) |
| `max_bars_in_trade` | `6` | `int` ≥ 1 |
| `min_atr_pips` | `{}` | `dict[str, float]` (empty by default) |

**Any change to any of these parameters constitutes a NEW
candidate** that requires its own discovery + design cycle.
The Phase 4 YAML config + Phase 4 pre-commit must record the
exact values; the future evidence sprint's runner must
verify them verbatim before any backtest fires.

### 3.1 Why these exact values

| parameter | rationale |
|---|---|
| `master_seed = 20260523` | Single integer chosen *before* writing the strategy module. Encodes today's date for traceability; no semantic meaning. Frozen for all CAMPAIGN_011 runs. |
| `entry_probability_per_bar = 0.05` | Calibrated to produce per-fold trade counts comparable to CAMPAIGN_010's regime (~50–80 per pair per fold). Not "tuned" — derived from CAMPAIGN_010's reference frequency and the protocol's `trade_count ≥ 30 per fold` gate. |
| `atr_lookback = 14` | Standard Wilder ATR; matches CAMPAIGN_010 / CAMPAIGN_002 / CAMPAIGN_004 — the project's standard. Deliberately matched for clean entry-signal comparison. |
| `atr_stop_multiple = 2.0` | Matches CAMPAIGN_010 verbatim. The stop is not a hidden variable. |
| `max_bars_in_trade = 6` | Matches CAMPAIGN_010 (≈ 1 trading day on H4). |
| `trailing_stop_atr_multiple = None` | No trail in v1 — matches CAMPAIGN_010. |
| `min_atr_pips = {}` | No per-pair minimum — matches CAMPAIGN_010. |

## 4. R1–R8 signal rule table (binding)

The strategy's `generate_signal(ctx) -> Signal | None` MUST
implement the following 8 rules in order. Each rule returns
`None` if its condition is not satisfied; only R8 emits a
`Signal`.

### R1 — Warm-up

The strategy requires at least `atr_lookback + 2 = 16` H4 bars
of history (matches CAMPAIGN_010's R1 for clean exit-mechanics
comparison; ATR(14) needs ≥ 15 bars + 1 buffer for accessing
index `-2`).

```python
df = ctx.candles.completed_only().df
if len(df) < atr_lookback + 2:
    return None
```

### R2 — Block re-entry while a position is open

If `ctx.open_positions` contains a flat-False position for
`ctx.instrument`, return `None`. Mirrors CAMPAIGN_010's R2 and
the engine's single-instrument single-position invariant.

```python
if any(
    not pos.is_flat and pos.instrument == ctx.instrument.name
    for pos in ctx.open_positions
):
    return None
```

### R3 — Deterministic seed input + score derivation

At completed bar `t`:

1. Build the seed input as a UTF-8 string in the exact form:
   `f"{master_seed}|{instrument_name}|{bar_timestamp_iso}"`
   where `bar_timestamp_iso = pd.Timestamp(df.index[-1]).tz_convert(UTC).isoformat()`.
2. Hash via SHA-256:
   `digest = hashlib.sha256(seed_input.encode("utf-8")).digest()`.
3. Extract two independent 64-bit integers from disjoint
   halves of the digest:
   - `bar_random = int.from_bytes(digest[:8], "big")` — used
     for direction selection.
   - `gate_random = int.from_bytes(digest[8:16], "big")` —
     used for the entry-probability gate.

The remaining bytes are deliberately unused (reserved for
future test-determinism inspection).

**Binding invariant:** the seed input contains **only**
`(master_seed, instrument_name, bar_timestamp_iso)`. It MUST
NOT contain any bar-`t` price data (close, high, low, open,
volume) or any ATR value or any derived feature. This is the
key no-lookahead rail for a null-model strategy.

### R4 — Entry-probability gate

The strategy must not fire on every bar (which would dwarf any
"real" candidate's trade count). Apply a deterministic gate:

```python
gate_value = gate_random / (2**64 - 1)  # in [0, 1]
if gate_value >= entry_probability_per_bar:
    return None
```

Equivalent integer form: `gate_random < int(entry_probability_per_bar * (2**64 - 1))`.

The implementation MAY use either; the contract is "deterministic
gate keyed on `gate_random`".

### R5 — Fail-closed on insufficient ATR

Compute the standard ATR over completed candles and use the
value as of bar `t-1`:

```python
atr_series = atr(df["high"], df["low"], df["close"], atr_lookback)
prior_atr = float(atr_series.iloc[-2])
if not math.isfinite(prior_atr) or prior_atr <= 0:
    return None
```

This mirrors CAMPAIGN_010's R5. Bar `t` reads `close[t]` only
for the stop-placement reference price (see R7); bar `t`'s
`high`, `low`, `open`, and `volume` are deliberately not read.

### R6 — Spread filter (delegated to RiskEngine)

The candidate does **not** implement its own spread filter; the
existing `RiskEngine`'s per-pair `spread_filter` gates apply
identically to CAMPAIGN_010. The runner uses
`RiskEngine(settings, mode="backtest")` (same as CAMPAIGN_010's
runner) so that gate's behavior is shared.

This rule is "structurally satisfied" by the engine wiring; no
code in `random_entry_anchor.py` enforces it.

### R7 — Direction selection + ATR-stop placement

Direction is derived from `bar_random`:

```python
side = "long" if (bar_random & 1) == 0 else "short"
```

The reference price for stop placement is `close[t]` (matches
CAMPAIGN_010's R8; the only bar-`t` field consulted, used as the
hypothetical executable reference):

```python
last_close = float(df["close"].iloc[-1])

if side == "long":
    stop = last_close - atr_stop_multiple * prior_atr
else:
    stop = last_close + atr_stop_multiple * prior_atr

if stop == last_close:
    # Defense in depth — unreachable given prior_atr > 0 in R5.
    return None
```

**Important:** `last_close` is used for stop placement only, NOT
for the seed-input or gate-input. R3's invariant remains intact.

### R8 — Emit deterministic `Signal`

```python
signal_id = _stable_signal_id(
    "random_entry_anchor",
    "0.1.0-c011",
    instrument_name,
    timeframe,
    bar_timestamp_iso,
    side,
)

return Signal(
    signal_id=signal_id,
    strategy_name="random_entry_anchor",
    strategy_version="0.1.0-c011",
    instrument=instrument_name,
    timeframe=timeframe,
    timestamp=bar_timestamp_utc,
    side=side,
    entry_intent="market",
    stop_model=f"ATR{atr_lookback}*{atr_stop_multiple}",
    stop_price=ctx.instrument.round_price(Decimal(str(stop))),
    exit_model="time_stop_only",
    features={
        "bar_random": int(bar_random),
        "gate_random": int(gate_random),
        "gate_value": float(gate_value),
        "prior_atr": float(prior_atr),
        "last_close": float(last_close),
    },
    reason=(
        f"Random null-model entry: side={side} "
        f"(bar_random={bar_random}, gate_value={gate_value:.6f} "
        f"< entry_probability={entry_probability_per_bar:.4f})"
    ),
)
```

`_stable_signal_id(*parts)` uses `sha256("|".join(str(p) for p in parts))[:24]`
— same pattern as CAMPAIGN_010's `session_breakout.py`. The
sizing is delegated to the engine + `RiskEngine` exactly as in
CAMPAIGN_010.

## 5. No-lookahead safeguards (binding)

| safeguard | enforcement |
|---|---|
| **Seed input contains only `(master_seed, pair_name, bar_timestamp_iso)`** | code-time invariant; structural unit test asserts the seed-input-building helper does not accept any other argument |
| **No use of `close[t]`, `high[t]`, `low[t]`, `open[t]`, `volume[t]` in the seed** | code-time invariant; structural unit test greps for those names inside the seed helper |
| **ATR is computed once over the full series; the value at index `-2` is used** | matches CAMPAIGN_010 — no peek at bar-`t` ATR for the entry decision |
| **`close[t]` is read ONLY for stop placement (R7)** — never for the entry decision | structural assertion in the strategy module; the entry decision is determined by R3/R4 *before* `last_close` is read |
| **No future bars** | `completed_only()` filter on the candle frame; the engine drives the strategy bar-by-bar |
| **No same-bar high/low/open/volume read** | code-time invariant; structural unit test greps for those names outside the stop-placement path |
| **Strategy module imports nothing from `forex_bot.broker`** | structural unit test (source grep) |
| **Strategy module uses no `random.random()`, `numpy.random`, or built-in `hash()`** | structural unit test (source grep) |
| **Strategy module does not reference `CAMPAIGN_002` / `trend_following` / `Donchian` / `EMA` parameter keys** | structural unit test (source grep) — no parameter contamination |
| **Strategy module does not reference `CAMPAIGN_010` / `session_breakout` / `Asian` / `London` parameter keys** | structural unit test (source grep) — distinctness preserved |

## 6. Distribution and determinism expectations (binding)

| expectation | meaning |
|---|---|
| **Same `(master_seed, pair, bar_timestamp_iso)` → same `bar_random`, same `gate_random`, same decision** | deterministic-by-construction |
| **Different `bar_timestamp_iso` → different `bar_random` / `gate_random` with overwhelming probability** | SHA-256 collision resistance |
| **Different `pair` → different `bar_random` / `gate_random` with overwhelming probability** | same |
| **Different `master_seed` → completely different sequence** | NEVER change the master_seed during a CAMPAIGN_011 evidence run; doing so produces a different candidate |
| **Long-short distribution** | over a large bar sample (≥ 10,000 bars), the fraction of `bar_random & 1 == 0` is 0.5 ± 3σ |
| **Entry frequency** | over a large bar sample (≥ 10,000 bars), the fraction passing the R4 gate is `entry_probability_per_bar` ± 2σ |

## 7. Null-model restrictions (binding)

| restriction | enforcement |
|---|---|
| **Cannot be approved.** | `configs/approved_strategies.yaml` remains `approved: []`. The Phase 3 unit tests assert `random_entry_anchor` is NOT in any approved-strategy list. |
| **Cannot enable paper-loop / demo-loop.** | The existing `paper-loop` / `demo-loop` refusal via the empty registry is unchanged; the Phase 4 research config keeps `app.trading_enabled=false`, `app.allow_order_submission=false`, `app.allow_live_trading=false`. |
| **No seed optimization.** | `master_seed = 20260523` is fixed in this spec and the Phase 4 pre-commit. The future evidence sprint's runner must assert the loaded YAML's `master_seed` matches verbatim. |
| **No parameter tuning.** | `entry_probability_per_bar` and every other frozen parameter is fixed in this spec. The future evidence sprint's runner must assert the loaded YAML matches verbatim. |
| **Unexpected PASS triggers investigation, not promotion.** | If the future evidence sprint records `WalkForwardResults.overall_verdict == "PASS"`, the documented response is the investigation playbook from [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md) §14 — confirm seed input has no leakage; confirm fold-boundary rules pass; confirm structural audits pass; escalate to a separate investigation sprint; **never** add to `configs/approved_strategies.yaml`. |
| **No "improvement" loops.** | The strategy is deliberately as simple as possible. Refactoring it to "see if randomness can be made to work" is forbidden — that becomes parameter tuning. |

## 8. Config schema (Phase 2 contract)

The `RandomEntryAnchorStrategyConfig` Pydantic model must mirror
the shape of `SessionBreakoutStrategyConfig`:

```python
class RandomEntryAnchorStrategyConfig(BaseModel):
    # CAMPAIGN_011 research candidate (`random_entry_anchor 0.1.0-c011`).
    # CANDIDATE SCAFFOLD ONLY — null model; not approvable by design.
    # See docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md.
    model_config = ConfigDict(extra="forbid")

    version: str
    timeframe: Literal["H1", "H4", "D"] = "H4"
    master_seed: int = 20260523
    entry_probability_per_bar: float = 0.05
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.0
    trailing_stop_atr_multiple: float | None = None
    max_bars_in_trade: int = 6
    min_atr_pips: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> RandomEntryAnchorStrategyConfig:
        if self.atr_lookback < 2:
            raise ConfigError("atr_lookback must be >= 2")
        if self.atr_stop_multiple <= 0:
            raise ConfigError("atr_stop_multiple must be > 0")
        if self.max_bars_in_trade < 1:
            raise ConfigError("max_bars_in_trade must be >= 1")
        if not (0.0 < self.entry_probability_per_bar < 1.0):
            raise ConfigError(
                "entry_probability_per_bar must be in (0, 1) (exclusive)"
            )
        if self.trailing_stop_atr_multiple is not None:
            raise ConfigError(
                "trailing_stop_atr_multiple must be None in v1 — "
                "the null model uses time-stop only"
            )
        return self
```

Add the slot to `StrategyConfig`:

```python
random_entry_anchor: RandomEntryAnchorStrategyConfig | None = None
```

Plus the matching enabled-list check in `_check_enabled`:

```python
if (
    "random_entry_anchor" in self.enabled
    and self.random_entry_anchor is None
):
    raise ConfigError(
        "strategy.random_entry_anchor config required when enabled"
    )
```

## 9. Strategy module signature (Phase 2 contract)

```python
class RandomEntryAnchorStrategy:
    name: str = "random_entry_anchor"

    def __init__(self, version: str = "0.1.0-c011") -> None:
        self.version = version

    def warmup_bars_required(self) -> int:
        # ATR(14) + 1 for index -2 + small buffer; matches CAMPAIGN_010
        return 32

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        ...
```

The module imports must include:

```python
import hashlib
import math
from datetime import UTC
from decimal import Decimal

import pandas as pd

from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext
from forex_bot.strategies.indicators import atr
```

The module must NOT import:

- `random` (the Python stdlib random module)
- `numpy` (or any `numpy.random` access)
- Anything from `forex_bot.broker`
- Anything from `forex_bot.execution`
- Anything from `forex_bot.loops`

## 10. Expected test cases (Phase 3 contract; target ≥ 20)

Mirror the structure of
[`tests/unit/test_session_breakout.py`](../../tests/unit/test_session_breakout.py):

| group | minimum cases | what each asserts |
|---|---:|---|
| Config defaults / validation | 6 | defaults match the frozen spec; `entry_probability_per_bar ≤ 0` / `≥ 1` rejected; non-positive `atr_lookback` / `atr_stop_multiple` / `max_bars_in_trade` rejected; non-None `trailing_stop_atr_multiple` rejected |
| Determinism — seed dependence | 4 | same `(master_seed, pair, ts)` → same decision; different `master_seed` → different sequence; different pair → different sequence; different timestamp → different sequence |
| Determinism — content invariance | 2 | seed input does not contain `close` / `high` / `low` / `volume`; changing bar-`t` price data does not change the decision |
| Distribution / frequency | 2 | over 10,000 bars, long-share is 0.5 ± 0.03; entry rate is `entry_probability_per_bar ± 0.01` |
| Strategy core | 4 | R1 warm-up; R2 block re-entry; R5 fail-closed on NaN ATR; R7 stop placement long/short |
| No-lookahead structural audit | 3 | source-grep: no `random.random`, no `numpy.random`, no built-in `hash()`; no `forex_bot.broker` import; no future-bar reads |
| Rejected-family contamination audit | 2 | source-grep: no `CAMPAIGN_002` / `trend_following` / `Donchian` / `EMA` references; no `CAMPAIGN_010` / `session_breakout` / `Asian` / `London` references |
| Signal id / shape | 2 | signal id is deterministic across runs; emitted `Signal` has the expected fields + null-model `reason` |
| Approval / safety regression | 3 | `approved_strategies.yaml` remains empty; `random_entry_anchor` NOT in `configs/paper.yaml` enabled; NOT in `configs/practice.yaml` enabled |
| **TOTAL** | **≥ 28** | (target ≥ 28 for safety; minimum acceptance threshold = 20) |

## 11. Missing-data behavior

- A bar with `NaN` `prior_atr` returns `None` (R5).
- A bar where the pair's row count is < warm-up returns
  `None` (R1).
- A bar where `ctx.open_positions` already has an active
  position for the instrument returns `None` (R2).
- A bar where the R4 gate doesn't pass returns `None`
  (most bars — by `entry_probability_per_bar`).

The strategy never raises an exception on bad data; it
fail-closes by emitting no signal. Consistent with CAMPAIGN_010.

## 12. Engine + RiskEngine + financing interface (unchanged)

The strategy plugs into the existing infrastructure with no
modifications:

- **`BacktestEngine`** — same `mode='backtest'` invocation as
  CAMPAIGN_010; single-instrument single-position-at-a-time;
  ATR stop + max-bars-in-trade time-stop exit.
- **`RiskEngine`** — same `mode='backtest'` gates as
  CAMPAIGN_010; per-pair spread filter; correlation cap;
  daily/weekly loss limit; session-blackout config from the
  research YAML.
- **`research.financing`** — overlay computed by the future
  evidence sprint using `default_stress_rate_source()`
  (ESTIMATED + conservative-stress); MODELED refused at four
  layers; not invoked in this scaffold sprint.

## 13. What the scaffold sprint does NOT do

- Does **not** add a campaign runner (`scripts/run_campaign_011.py`).
  That is the future evidence sprint's job.
- Does **not** invoke `BacktestEngine` against the candidate.
- Does **not** generate `WalkForwardResults`.
- Does **not** compute the financing overlay.
- Does **not** compute risk diagnostics.
- Does **not** extend the parity verifier.
- Does **not** edit `configs/approved_strategies.yaml`.
- Does **not** edit `configs/paper.yaml` or `configs/practice.yaml`.

## 14. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **Paper / demo / live remain blocked.**
- No code edited this phase (Phase 1 is docs-only).
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 15. Cross-links

- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
  (the design this spec materializes)
- [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_002.md)
  (the prompt-spec the sprint follows)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
  (the prior implementation spec to mirror in structure)
- [`src/forex_bot/strategies/session_breakout.py`](../../src/forex_bot/strategies/session_breakout.py)
  (the closest existing module to copy *structure* from)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
