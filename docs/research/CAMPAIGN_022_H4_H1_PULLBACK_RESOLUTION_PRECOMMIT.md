# CAMPAIGN_022 — H4/H1 Pullback Resolution Entry Precommit

**Date:** 2026-05-27
**Status:** PRECOMMITTED_NOT_EXECUTED — parameters frozen; scaffold sprint only

## Identity

| field | value |
|---|---|
| `campaign_id` | CAMPAIGN_022 |
| `strategy_name` | `h4_h1_pullback_resolution_entry` |
| `version` | `0.1.0-c022` |
| `working_name` | H4/H1 Pullback Resolution Entry |
| `promotion_eligible` | false |

## Hypothesis

C020 (rejected) and C021 both demand **strict same-direction alignment across every
timeframe** ("all green"). That pattern tends to enter *after* a move is already
extended. C022 tests the opposite, structurally-favored pattern:

> **H4 defines directional bias. H1 must be in a counter-trend pullback that still
> holds. M15 fires only when that pullback resolves back into the H4 direction.**

The defining contrast with C021: **H1 is NOT required to agree with H4.** It is required
to be *temporarily soft (pulled back) but structurally intact*. The edge is captured
when a lower-timeframe pullback resolves back into higher-timeframe structure, not when
all timeframes are simultaneously green.

## Scope decision — H4 is the top timeframe (no D1 / no D1AGG)

CAMPAIGN_022 deliberately removes the daily layer. Consequences, declared honestly:

- **No D1AGG**, no `native_h4_derived_d1agg` provenance, no `aggregate_h4_to_d1`
  dependency, no M1-derived-D1AGG rejection logic. Provenance is three `m1_derived`
  layers only.
- **Known limitation:** there is no macro risk-on/risk-off regime filter. H4 structure
  is the highest context available to this strategy. This is a scoping choice, not an
  oversight; a future campaign may layer a D1 regime gate on top.

## Universe and timeframes

- **Pairs:** EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (seven majors)
- **Execution:** M15 (completed bars only)
- **Context:** H4 (bias), H1 (pullback state) — both joined with
  `htf_align.align_last_completed`
- **Top timeframe:** H4 (no D1, no D1AGG)
- **Future optional:** M5 refinement — not in v1 evidence plan

## Data provenance (mandatory)

| layer | source | notes |
|---|---|---|
| M15 execution | `m1_derived` | aggregated from Postgres M1 corpus |
| H1 context | `m1_derived` | same |
| H4 context | `m1_derived` | same |
| D1 / D1AGG | **not used** | C022 has no daily layer |

Config block: `configs/campaign_022_h4_h1_pullback_resolution.yaml` → `data_provenance`.
Provenance validator must **reject** any config carrying a `d1agg_context` /
`d1_*` key (defensive: this campaign must not silently inherit a daily layer).

## H4 directional bias — multi-factor, slope-aware (not a bare EMA cross)

Computed on completed H4 bars, then read at the `align_last_completed` bar for the
decision time. Three directional votes plus one strength gate:

| factor | bullish vote | bearish vote |
|---|---|---|
| price vs EMA50 | `h4_close > h4_ema50` | `h4_close < h4_ema50` |
| EMA20 vs EMA50 | `h4_ema20 > h4_ema50` | `h4_ema20 < h4_ema50` |
| EMA50 slope over **3** completed H4 bars | slope > 0 | slope < 0 |

- **Strength gate:** ADX(14) on H4 ≥ **20** (textbook "a trend is present" threshold;
  raised from the draft's 18 per pre-execution review). Below threshold → `range` →
  no trade (ADX is a gate, never a directional vote).
- **Bias = bullish** if ≥ **2 of 3** votes bullish AND ADX ≥ 20.
- **Bias = bearish** if ≥ 2 of 3 votes bearish AND ADX ≥ 20.
- **Else:** `range` / neutral → no trade.

Rationale: scoring (notes' Method 4) + volatility gate (Method 5) avoids both C021's
brittle single-line cross and the over-strict "all EMAs aligned on all TFs" overfit.

## H1 pullback state — the differentiator

Computed on completed H1 bars, read at the `align_last_completed` bar for the decision
time. Lookback: **6** completed H1 bars before the aligned bar.

**For H4-bullish bias, H1 must show a pullback that holds:**

- **Pullback** (either): within lookback, `low` touched `h1_ema20`
  **OR** `h1_rsi(14)` dipped below **45** (momentum reset). (Same OR-pattern as the
  existing `h4_pullback_and_trigger`.)
- **Holds:** latest completed H1 `close ≥ h1_ema50` (slow line intact → pullback, not
  reversal).

**For H4-bearish bias:** mirror — `high` touched `h1_ema20` OR RSI > **55**, and latest
H1 `close ≤ h1_ema50`.

Using the EMA50-hold instead of swing-high/low detection deliberately avoids the
swing-detection ambiguity and parameter sensitivity flagged in the notes.

If H1 is not in a holding pullback in the H4 direction → no trade.

## M15 resolution trigger

Reuses the existing reclaim primitive (`m15_pullback_and_reclaim` pattern). Lookback:
**8** completed M15 bars before the decision bar (exclusive of decision).

**Long (all required):**

- H4 bias bullish AND H1 in holding bullish pullback
- In lookback window: `low` touched `ema20` or `ema50`
- Reclaim: `close[t] > ema20[t]` AND `close[t-1] <= ema20[t-1]`

**Short:** mirror on highs / bearish stack.

**M15 execution floors:** ADX(14) ≥ **18** on M15; per-pair `min_atr_pips` floor
(optional, empty default). Skip if warmup NaN.

## Side rules

- Long only on H4-bullish + H1 holding-bullish-pullback + M15 reclaim.
- Short only on H4-bearish + H1 holding-bearish-pullback + M15 reclaim.

## Cost / session

- Spread filter: enabled (`max_spread_to_atr_pct: 8.0`, per-pair caps).
- Session filter: rollover / Friday / Sunday blocks per campaign YAML.
- Strategy `min_atr_pips`: empty default (optional per-pair floor).

## Stop / exit

| rule | value |
|---|---|
| initial stop | **2.0 × M15 ATR(14)** (prior-bar ATR at index −2) |
| time stop | **32** M15 bars (~8 hours) |
| take-profit | none |
| trailing | none |
| exit_model | `hard_stop_or_time` |
| exit priority | stop → time → session/EOD (engine) |

Structure-based stop (below the H1 pullback low) is a documented future variant; v1
freezes the ATR stop for comparability with C021.

## Position sizing

- `risk_per_trade_pct: 0.25`, `max_risk_per_trade_pct: 0.50`
- `max_open_positions: 1`, `max_positions_per_instrument: 1`

## Execution realism metadata

```yaml
research_metadata:
  fill_timing: next_bar_open
  execution_realism: conservative
  evidence_use: approval_bound
  promotion_eligible: false
```

## Financing

| field | value |
|---|---|
| `financing_mode` | `none` (scaffold) |
| `financing_overlay_required` | true if future avg hold > 1 day |

## Warmup / alignment — no-lookahead requirements (non-negotiable)

- Strict indicator warmup (`nan` until ready; `rsi(..., warmup_policy="nan")`).
- Every H4 / H1 derived value — close, EMA20, EMA50, EMA slope, RSI, ADX — **must be
  read at the `align_last_completed` bar for the decision time, never from the tail of
  the context frame.** (This is the exact class of bug fixed in C021's
  `_aligned_h1_trend` EMA-slope computation; C022 must not reintroduce it. Slope/structure
  windows must be bounded to bars with `time <= aligned_feature_time`.)
- No signal if any HTF align returns `HTF_UNAVAILABLE` / `HTF_STALE` or a blocked reason.
- Incomplete H1/H4 bars must never affect the M15 decision (`complete=True` only).
- Record `htf_feature_times` (`h4`, `h1`) on every emitted signal;
  `validate_signal_provenance` must return `[]`.

## Scaffold deliverables (this sprint — no execution, no evidence)

1. `docs/research/CAMPAIGN_022_H4_H1_PULLBACK_RESOLUTION_PRECOMMIT.md` (this file).
2. `configs/campaign_022_h4_h1_pullback_resolution.yaml` (frozen parameters).
3. `src/forex_bot/strategies/h4_h1_pullback_resolution_entry.py`
   (class `H4H1PullbackResolutionEntryStrategy`, version `0.1.0-c022`). Reuses
   `htf_align.align_last_completed`, `indicators` (ema/atr/adx/rsi), and the C021 reclaim
   primitive. **No broker / executor / oanda / loops imports.** Emits `Signal` only.
4. `StrategyConfig` slot + `H4H1PullbackResolutionEntryStrategyConfig` model in
   `config.py`.
5. `tests/unit/test_h4_h1_pullback_resolution_entry.py` (see test plan below).

## Test plan (scaffold)

- Provenance: rejects any `d1agg_context` / daily key; requires three `m1_derived` layers.
- H4 bias scoring: 2/3 + ADX gate → bullish/bearish; <2 or ADX<20 → range/no-signal.
- H1 pullback-holds: pullback + close≥EMA50 → valid; pullback but close<EMA50 → blocked;
  no pullback → blocked.
- M15 resolution: reclaim without prior touch blocks; touch without reclaim blocks.
- **No-lookahead:** H4 and H1 trend functions, fed a frame with bars appended *after*
  the decision time that contradict the pre-decision slope/structure, must return the
  pre-decision result and `htf_feature_time <= decision_time` (mirrors the C021
  `test_h1_slope_ignores_future_bars` regression).
- Wrong execution granularity (non-M15) raises.
- Frozen config loads; `version == 0.1.0-c022`; `trading_enabled is False`.
- `approved_strategies.yaml` remains `approved: []`.
- No broker/execution/oanda imports in the strategy source.

## Future execution gates (not run in scaffold)

### Gate discipline (non-negotiable)

1. **Train/validation only first** — no test window until pre-test gates pass.
2. **No retuning** — frozen `0.1.0-c022`; no parameter changes after seeing any split.
3. **No test lockbox** unless **both** train gates **and** validation gates pass.
4. **Backtrader parity PASS** required **before** test lockbox opens.
5. **No validation rescue if train fails** — train expectancy < 0 or any train gate fail
   → immediate **REJECT**; do not run test; do not cite validation uplift; do not soften
   gates or retune (same discipline as CAMPAIGN_020 / CAMPAIGN_021).
6. **No approval under any outcome** — `approved_strategies.yaml` stays `approved: []`;
   paper/demo/live blocked.

### Metric gates

- Train expectancy ≥ 0 (`next_bar_open`).
- Validation expectancy > 0; PF ≥ 1.05; trades ≥ 150 (or documented lower).
- ≥ 4/7 validation pairs positive (or majority if fewer pairs).
- 2× cost stress validation expectancy ≥ 0.
- Beat C011 deduped null by +0.010R.
- **Beat C021's recorded outcome** (head-to-head: pullback-resolution vs all-green
  alignment on the same universe / windows).
- Financing overlay if avg hold > 1 day.
- Max status: RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED — **not approval**.

## No tuning rule

One frozen parameter set in YAML. No sweeps. No parameter choice from historical results
in this or future execution without a new precommit campaign.

## No approval

`configs/approved_strategies.yaml` remains `approved: []`. Paper/demo/live blocked.
