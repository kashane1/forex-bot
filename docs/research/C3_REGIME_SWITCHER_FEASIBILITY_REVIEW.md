# C3 — Daily-ATR-Percentile Regime Switcher Feasibility Review

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-003`
`strategy_evidence: false`

Phase 3 feasibility review for candidate **C3 — Daily-ATR-percentile
regime switcher** before selecting it in Phase 4. **This document
does not approve any strategy.** It verifies the regime-feature
computation can be done safely (no lookahead, no D1-backtest
blocker, no broad parameter search), pre-commits one specific
parameter set, and confirms structural distinctness from every
prior rejected family.

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## 1. C3 — precise specification (frozen at this Phase 3)

| dimension | value |
|---|---|
| candidate name | Daily-ATR-percentile regime switcher |
| family category | Volatility-regime switching (per protocol §4 whitelist) |
| direction | symmetric (long / short, conditional on a *trend* sub-signal) |
| primary feature | the latest **completed prior day's** D1AGG ATR-14 expressed as a **percentile** of the prior N completed days' D1AGG ATR-14 values |
| regime classification | **two regimes**: HIGH-VOL (percentile ≥ threshold) and LOW-VOL (percentile < threshold) |
| entry signal | **only fires in HIGH-VOL regime**: a trend-direction entry, defined as `close[t] vs close[t−4]` (one prior trading day's worth of H4 bars, ≈ a 1-day momentum proxy) |
| direction rule | long if `close[t] > close[t−4] + min_close_move`, short if `close[t] < close[t−4] − min_close_move`, else `None` |
| timeframe | H4 execution (the strategy fires per H4 bar); D1AGG is consumed read-only via the existing aggregator |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (same as CAMPAIGN_010 / CAMPAIGN_011) |
| data source | `data/campaign_002.sqlite3` (gitignored symlink); same H4 store reused |
| approval path | none from this sprint; only via the future scaffold + evidence + verifier + human-approval ladder |

The candidate is distinct from CAMPAIGN_002 (no Donchian, no
EMA crossover), from CAMPAIGN_010 (no session windows), from
CAMPAIGN_011 (deterministic feature-driven entry vs random),
and from MR / PB / VB by mechanism. See §6 for the explicit
distinctness check.

## 2. Frozen parameter pre-commit (this Phase 3)

The values below are **fixed in this Phase 3** before any code,
before any backtest, before any pilot. Any deviation in a future
scaffold sprint constitutes a NEW candidate requiring its own
discovery + design cycle. The Phase 5 implementation design and
Phase 6 future-branch specs will inherit these verbatim; the
future runner script will assert them.

| parameter | value | rationale |
|---|---|---|
| `version` | `0.1.0-c012` | candidate id; matches the CAMPAIGN_012 label proposed in Phase 4 |
| `timeframe` | `H4` | matches CAMPAIGN_010 / CAMPAIGN_011 (only authorized intraday timeframe) |
| `atr_lookback_h4` | `14` | project-standard exit-sizing constant (used by CAMPAIGN_002 / 010 / 011); used only for the **stop** placement, not the regime feature |
| `atr_stop_multiple` | `2.0` | project-standard exit-sizing constant; same as CAMPAIGN_010 / 011 |
| `max_bars_in_trade` | `6` | matches CAMPAIGN_010 / CAMPAIGN_011 — ≈ 1 trading day on H4 |
| `trailing_stop_atr_multiple` | `None` | no trail in v1; matches CAMPAIGN_010 / 011 |
| `min_atr_pips` | `{}` | no per-pair minimum |
| **`daily_atr_lookback`** (DAYS used inside the **D1AGG ATR**) | **`14`** | standard Wilder daily ATR; matches the H4 ATR lookback for conceptual consistency |
| **`regime_lookback_days`** (rolling window for the ATR-percentile reference) | **`60`** | ≈ 3 trading months; long enough for distribution shape, short enough to reflect regime; chosen *before* any backtest from economic-cycle reasoning, not from prior campaign output |
| **`regime_percentile_threshold`** | **`0.70`** | "top 30 % of trailing-60-day ATR distribution" — pre-committed *before* any code; not from CAMPAIGN_011 output |
| **`min_close_move_atr_fraction`** (trend sub-signal minimum) | **`0.25`** (= 25 % of `prior_atr_h4`) | filters bar-to-bar drift from a real directional move; matches CAMPAIGN_010's `min_asian_range_atr_fraction = 0.30` flavour |
| **`trend_lookback_h4_bars`** (the `close[t−4]` comparison) | **`4`** | one trading day's worth of H4 bars (4 × 4 h = 16 h ≈ the alignment-day's research window) |
| `risk.risk_per_trade_pct` | `0.25` | matches CAMPAIGN_010 / 011 |
| `risk.max_positions_per_instrument` | `1` | matches CAMPAIGN_010 / 011 |
| `master_seed` | (none — C3 has no random component) | strategy is fully deterministic from price data |

**Binding rule:** the Phase 5 implementation design and the
future scaffold sprint must pre-commit these values verbatim.
The runner must assert them. **The regime gate parameters
(`regime_lookback_days = 60`, `regime_percentile_threshold = 0.70`)
are chosen here in Phase 3 from independent reasoning, before any
backtest and before any view of CAMPAIGN_011 output.** Sweeping
or "tuning" these to improve the result is the canonical
overfitting anti-pattern.

## 3. Required data — verified

| requirement | available? |
|---|:---:|
| 7-pair H4 OANDA practice candles, 2020-01-01 → 2026-05-19 | ✓ — existing gitignored symlink (used by CAMPAIGN_010 / 011 verbatim) |
| H4 → D1AGG aggregator with `rollover_safe` clearance | ✓ — `src/forex_bot/backtesting/d1_aggregation.py` already implements this (see `aggregate_h4_to_d1` + `D1AggregationResult` + `rollover_safe`) |
| Walk-forward harness | ✓ — `research/walk_forward/` (used by CAMPAIGN_010 / 011) |
| Financing calculator | ✓ — `research/financing/` (used by CAMPAIGN_010 / 011) |
| Risk-engine in `mode='backtest'` | ✓ — used by CAMPAIGN_010 / 011 runners |
| New data fetch | **not needed** |
| New credentials | **not needed** |
| New external dependency | **not needed** |

## 4. Required indicators / features

| feature | source | how computed |
|---|---|---|
| H4 ATR-14 (for stop placement) | `forex_bot.strategies.indicators.atr` (existing) | over `ctx.candles.completed_only().df`, take `iloc[-2]` to use bar `t-1`'s value (mirrors CAMPAIGN_010 / 011 convention) |
| H4 close at bar `t` (for stop reference + trend sub-signal) | `df["close"].iloc[-1]` | only the close is read at bar `t`; never `high[-1]` / `low[-1]` / `open[-1]` / `volume[-1]` (mirrors CAMPAIGN_010 / 011 R7 / R8 convention) |
| H4 close at bar `t-4` (trend sub-signal anchor) | `df["close"].iloc[-5]` | a prior-bar read; trivially no-lookahead |
| **D1AGG ATR-14** for prior completed days | `forex_bot.backtesting.d1_aggregation.aggregate_h4_to_d1` over the **H4 history up to the most recent completed trading day**, then a Wilder ATR-14 over the resulting D1AGG bars | only completed trading days are emitted (the aggregator drops `incomplete`/`ambiguous` days); the current trading-day-in-progress contributes nothing |
| **D1AGG ATR percentile over the trailing 60 completed days** | `numpy.percentile` (or equivalent) over the last 60 D1AGG ATR-14 values immediately preceding the most-recent-completed-day | rolling window only; never a global / full-sample percentile |
| **Regime label** | `HIGH-VOL` if `most_recent_completed_day_atr >= percentile_threshold * trailing_60_day_atr_distribution_value`; else `LOW-VOL` | binary; computed once per H4 bar; structurally cannot leak future data |

## 5. Leakage / no-lookahead risk analysis

### 5.1 Risk: using the current incomplete day's high / low to compute "today's" ATR

- **Mitigation.** The strategy *never* asks the aggregator for the
  current trading day. It calls
  `aggregate_h4_to_d1(h4_completed_only)` only on H4 bars whose
  timestamp is strictly inside a completed trading day; the
  aggregator's own rule is that a trading day is "aggregated"
  only when all 6 well-formed H4 candles are present
  (`_aggregate_day` returns `incomplete` for partial days). The
  strategy then takes the **most recent emitted D1AGG candle**
  as "most-recent-completed-day" — this is structurally **prior**
  to the current trading day in progress.

### 5.2 Risk: computing percentile using future data (full-sample percentile)

- **Mitigation.** The regime calculation explicitly uses a
  **rolling 60-day window of past completed days only**. The
  implementation must build the window from the trailing-60
  D1AGG entries strictly preceding the most-recent-completed-day
  reference value, **never** including the reference value
  itself, **never** the current day, **never** any future day.
  Phase 5 implementation spec will codify this with the exact
  Python slice: `dagg_atr_series.iloc[-61:-1]` (60 trailing days
  excluding the reference day) or equivalent.

### 5.3 Risk: leaking test-window stats into train / validation / test

- **Mitigation.** The walk-forward harness already enforces
  fold-boundary leakage rules; the strategy itself uses only
  **prior** bars within each fold's test window. The strategy's
  warmup is `regime_lookback_days + daily_atr_lookback ≈ 60 + 14
  ≈ 74 completed trading days` worth of H4 history; under H4
  (~5 days per week × 4 weeks per month × 14 months for 74
  trading days at 6 H4 bars per day), that's ~440 H4 bars of
  warmup before the strategy can emit a signal in any fold's
  test window. The runner already discards `warmup_bars`
  per the engine convention; the strategy's
  `warmup_bars_required()` will return ≥ 500 to be safe.

### 5.4 Risk: recalculating percentile across the full sample

- **Mitigation.** The strategy runs **per H4 bar**; each call
  computes the regime label from the **immediately-trailing
  60 completed days** of D1AGG ATR. No global computation, no
  cross-fold sharing, no caching that could include
  out-of-window data.

### 5.5 Risk: using bar-`t` close to construct the regime feature

- **Mitigation.** Bar `t`'s close is read **only** for stop
  placement (mirrors CAMPAIGN_010 / 011 convention). The regime
  feature uses only **prior-completed-day** D1AGG ATR values —
  never bar `t`'s OHLC. Phase 5 spec will codify this with a
  source-grep structural test in `tests/unit/test_<candidate>.py`
  that the regime-feature helper does not consult `df["close"]`
  / `df["high"]` / `df["low"]` / `df["open"]` / `df["volume"]`
  past index `-2` (which is the last fully completed prior bar).

### 5.6 Risk: weekend / holiday handling

- **Mitigation.** The aggregator already classifies trading
  days as `aggregated` / `incomplete` / `ambiguous` and
  `missing_weekdays` is reported separately. The strategy
  consumes only `aggregated` D1AGG candles, so weekend gaps and
  data holes never count toward the 60-day window. Under
  insufficient history (< 60 + 14 emitted D1AGG candles), the
  strategy fails closed and returns `None`.

### 5.7 Summary

All 6 lookahead risks have concrete, structurally-enforced
mitigations. The Phase 5 implementation spec will codify each
mitigation as a unit-test target (mirroring the
`tests/unit/test_session_breakout.py` and
`tests/unit/test_random_entry_anchor.py` patterns).

## 6. Safe implementation pattern (binding for Phase 5)

```python
# Pseudocode — Phase 5 will translate this into the binding spec.

from forex_bot.backtesting.d1_aggregation import (
    aggregate_h4_to_d1,
    AGG_GRANULARITY,
)

def _compute_regime(
    h4_candles_completed_only: list[Candle],
    *,
    daily_atr_lookback: int = 14,
    regime_lookback_days: int = 60,
    regime_percentile_threshold: float = 0.70,
) -> Literal["HIGH_VOL", "LOW_VOL", "INSUFFICIENT_HISTORY"]:
    """Return regime label from the most recent completed trading
    day's D1AGG ATR vs the trailing-window percentile.

    Invariants (Phase 5 unit tests will enforce):
    - Uses only completed H4 candles.
    - Uses only `aggregated` D1AGG days emitted by the aggregator.
    - The reference D1AGG day is the latest emitted day; the
      window is the *trailing* `regime_lookback_days` days
      *strictly preceding* the reference.
    - Returns INSUFFICIENT_HISTORY (caller treats as None signal)
      if fewer than (regime_lookback_days + daily_atr_lookback)
      aggregated days are available.
    """
    agg = aggregate_h4_to_d1(h4_candles_completed_only)
    d1_candles = agg.candles
    if len(d1_candles) < regime_lookback_days + daily_atr_lookback:
        return "INSUFFICIENT_HISTORY"

    # Wilder ATR-14 over the D1AGG candle series.
    d1_atr = wilder_atr(d1_candles, daily_atr_lookback)

    # Reference value = most recent completed day's ATR.
    reference = d1_atr[-1]
    # Trailing window = the regime_lookback_days values immediately
    # preceding the reference (exclusive of the reference itself,
    # because percentile against itself is degenerate).
    trailing = d1_atr[-(regime_lookback_days + 1):-1]
    assert len(trailing) == regime_lookback_days

    pct_value = numpy.percentile(trailing, regime_percentile_threshold * 100)
    if reference >= pct_value:
        return "HIGH_VOL"
    return "LOW_VOL"


def generate_signal(self, ctx: StrategyContext) -> Signal | None:
    df = ctx.candles.completed_only().df

    # R1: H4 warm-up + D1AGG history.
    if len(df) < self._warmup_bars():
        return None
    # R2: block re-entry.
    if any(not p.is_flat and p.instrument == ctx.instrument.name
           for p in ctx.open_positions):
        return None

    # R3: regime gate.
    h4_candle_list = _df_to_candles(df, ctx.instrument.name)
    regime = _compute_regime(h4_candle_list)
    if regime != "HIGH_VOL":
        return None  # only trade in high-vol regime

    # R4: H4 ATR for stop sizing (fail-closed if missing).
    atr_h4 = atr(df["high"], df["low"], df["close"], self.atr_lookback_h4)
    prior_atr = float(atr_h4.iloc[-2])
    if not math.isfinite(prior_atr) or prior_atr <= 0:
        return None

    # R5: trend sub-signal from close[t] vs close[t-4].
    last_close = float(df["close"].iloc[-1])
    anchor_close = float(df["close"].iloc[-5])  # one trading day prior
    if not (math.isfinite(last_close) and math.isfinite(anchor_close)):
        return None
    move = last_close - anchor_close
    min_move = self.min_close_move_atr_fraction * prior_atr
    if abs(move) < min_move:
        return None
    side: str = "long" if move > 0 else "short"

    # R6: stop placement (mirrors CAMPAIGN_010 / 011 R7 convention).
    if side == "long":
        stop = last_close - self.atr_stop_multiple * prior_atr
    else:
        stop = last_close + self.atr_stop_multiple * prior_atr
    if stop == last_close:
        return None

    # R7: emit Signal (deterministic signal_id; same pattern as 010/011).
    return Signal(...)
```

The full R-rule table will be codified in the Phase 5
implementation design.

## 7. Distinctness vs every rejected family (≥ 3 of 6 required)

| dim | C3 (regime switcher) | TF (CAMPAIGN_002) | distinct? |
|---:|---|---|:---:|
| 1 theoretical bucket | volatility-regime-conditional trend | unconditional momentum (EMA + Donchian break) | ✓ |
| 2 entry signal | regime-gated `close[t] vs close[t-4]` + ATR-fraction threshold | EMA-50 vs EMA-200 + Donchian-20 break | ✓ |
| 3 exit signal | ATR stop + 6-bar time stop | ATR-trailing + N-bar time stop | ≈ (both ATR-stop families; the *only* dim that overlaps) |
| 4 timeframe / universe | H4 / 7 pairs | H4 / 7 pairs | ≈ |
| 5 data inputs | D1AGG ATR percentile + H4 close-momentum | EMA + Donchian + ATR | ✓ |
| 6 failure-mode hypothesis | "trend persistence is regime-conditional" | "EMA-Donchian momentum captures trend persistence" | ✓ |

**Score: 5 / 6 — clears the threshold.**

| dim | C3 vs CAMPAIGN_010 (session_breakout) | distinct? |
|---:|---|:---:|
| 1 theoretical bucket | volatility-regime conditional vs liquidity-flow event | ✓ |
| 2 entry signal | regime-gated trend close vs London-bar close penetrating prior Asian high/low | ✓ |
| 3 exit signal | ATR stop + 6-bar time stop | ≈ |
| 4 timeframe / universe | H4 / 7 pairs | ≈ |
| 5 data inputs | D1AGG ATR percentile + H4 close-momentum | session windows + Asian-range + ATR | ✓ |
| 6 failure-mode hypothesis | regime-conditional trend | session-conditional continuation | ✓ |

**Score: 5 / 6.**

| dim | C3 vs CAMPAIGN_011 (random_entry_anchor null model) | distinct? |
|---:|---|:---:|
| 1 theoretical bucket | regime-conditional trend | null model (no theoretical edge) | ✓ |
| 2 entry signal | deterministic regime + trend rule | deterministic-seed coin flip | ✓ |
| 3 exit signal | ATR stop + 6-bar time stop | ≈ |
| 4 timeframe / universe | H4 / 7 pairs | ≈ |
| 5 data inputs | D1AGG ATR percentile + H4 close-momentum | bar-timestamp + ATR-for-stop only | ✓ |
| 6 failure-mode hypothesis | regime-conditional trend has edge | null hypothesis | ✓ |

**Score: 5 / 6.** C3 clears the distinctness gate vs the null
anchor by a wide margin — the entry mechanic is fundamentally
feature-driven, not random.

Against the other rejected families (VB, PB, MR) the same
≥ 5 / 6 scores hold; the mechanic is structurally different in
every case (different theoretical bucket; different entry; same
exit; same timeframe / universe; different data inputs;
different failure-mode hypothesis).

## 8. Infrastructure changes required — none

| infrastructure | needed? | status |
|---|:---:|---|
| `aggregate_h4_to_d1` | ✓ | already exists (`src/forex_bot/backtesting/d1_aggregation.py`) |
| H4 OANDA practice candle store | ✓ | already exists via symlink |
| `RiskEngine(mode='backtest')` | ✓ | already used by CAMPAIGN_010 / 011 runners |
| Walk-forward harness | ✓ | already exists |
| Financing calculator | ✓ | already exists |
| `BacktestEngine` single-instrument-single-position | ✓ | already correct |
| Wilder ATR helper (over D1AGG bars) | small in-strategy implementation; equivalent to existing `atr(...)` but typed for `list[Candle]` | new ~30 LOC inside the strategy module — no new package needed |

**No infrastructure prerequisite sprint is required.**

## 9. Why C3 should be selected

| factor | C3 status |
|---|---|
| structurally feasible today | ✓ (no engine change; no D1 backtest semantics involved; D1AGG aggregator already exists) |
| no MODELED-financing dependency | ✓ (ESTIMATED + conservative-stress is sufficient for research-grade evidence) |
| no broad parameter search | ✓ (regime gate parameters pre-committed in §2 above before any code) |
| distinctness from every rejected family ≥ 5 / 6 | ✓ |
| plausibility of beating CAMPAIGN_011 null floor | medium — the regime gate is a structural filter that conditionally suppresses unprofitable trend trades; whether this passes the +0.05 R aggregate gate or merely fails by less than CAMPAIGN_010 is the question the evidence sprint will answer |
| can produce a verdict in one scaffold + one evidence sprint | ✓ |
| reproducible (no random component) | ✓ |
| supports null-baseline comparison cleanly | ✓ (CAMPAIGN_012's metrics will be reported side-by-side with CAMPAIGN_011's) |

## 10. Caveats

- **C3 inherits the H4-majors cost drag** identified in
  CAMPAIGN_002, CAMPAIGN_005, CAMPAIGN_010. The regime gate's
  *only* job is to suppress trades during the most cost-unsafe
  windows; whether it does this well enough to clear the
  +0.05 R aggregate gate is empirically open.
- **The regime gate carries the soft warning from
  [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md)
  §3.9** ("medium overfit risk" via parameter overlap with
  TF / VB / CAMPAIGN_010 / 011). The mitigation — pre-committing
  `regime_lookback_days = 60` and
  `regime_percentile_threshold = 0.70` in §2 above, before any
  code — is the binding rule.
- **The `close[t] vs close[t-4]` trend sub-signal** is
  structurally adjacent to a 1-day momentum filter. The
  `min_close_move_atr_fraction = 0.25` gate prevents bar-to-bar
  drift from firing weak signals; the directionality test is
  whether the regime gate adds value over no regime gating
  (vs CAMPAIGN_002's unconditional momentum).
- **Verifier extension** is not required for the REJECT verdict
  (item 5 of the six-evidence ladder is a paper-promotion gate);
  recommended follow-up if CAMPAIGN_012 surprises with a PASS.

## 11. Feasibility status — **GREEN; select C3 as CAMPAIGN_012**

C3 is feasible to implement today with zero infrastructure
prerequisites, zero MODELED dependency, zero engine change.
The Phase 4 selection should proceed with C3 as CAMPAIGN_012
and proposed strategy id `regime_switcher_atr_percentile
0.1.0-c012`.

## 12. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
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

## 13. Cross-links

- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`D1_AGGREGATION_DESIGN.md`](D1_AGGREGATION_DESIGN.md)
- [`src/forex_bot/backtesting/d1_aggregation.py`](../../src/forex_bot/backtesting/d1_aggregation.py)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  (the gate vector C3 will inherit)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
  (the gate vector C3 will inherit; same set inherited by
  CAMPAIGN_011 from CAMPAIGN_010)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
