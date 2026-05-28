# CAMPAIGN_023 — H4/H1 Pullback Resolution Entry (ADX22) Precommit

**Date:** 2026-05-27
**Status:** PRECOMMITTED_NOT_EXECUTED — parameters frozen; scaffold sprint only

## Sibling declaration (read first)

CAMPAIGN_023 is an **ADX22 sibling / sensitivity** campaign of CAMPAIGN_022. It mirrors
C022 exactly. The **only intentional strategy-logic delta versus C022** is the H4
directional-bias strength gate:

| campaign | H4 ADX(14) gate |
|---|---|
| CAMPAIGN_022 | `h4_adx_min >= 20.0` |
| CAMPAIGN_023 | `h4_adx_min >= 22.0` |

Everything else is held constant: pairs, execution timeframe, context timeframes,
no-D1/no-D1AGG scope, M15 trigger, H1 pullback-holds logic, stop, time stop,
spread/session filters, execution realism, financing mode, gates, no-lookahead rules,
approved strategies, broker/executor behavior.

### Pre-registration, not tuning-after-results

C022 is **PRECOMMITTED_NOT_EXECUTED / SCAFFOLD_ONLY**. As of this precommit, **no C022
train/validation/test evidence has been generated or viewed** (C022 has no entry in
`docs/research/EVIDENCE_MANIFEST.json`; the freeze and archive validators PASS with no
C022 verdict). Selecting the ADX22 arm before any results exist is a legitimate
pre-registered sensitivity sibling, **not** parameter tuning after seeing outcomes.

> **Contamination guard.** If C022 evidence had already been executed or viewed before
> this work started, the correct action is to **STOP and document
> `BLOCKED_CONTAMINATED_BY_PRIOR_RESULTS`** instead of proceeding. That condition does
> **not** hold here — C022 has produced no evidence.

> **Update — 2026-05-28 (timeline clarification).** The statements above ("C022 has
> produced no evidence", "C022 is itself unexecuted") describe the state **at the time
> this precommit was authored, 2026-05-27**, which the Phase 0 audit verified (C022 was
> `SCAFFOLD_ONLY` and absent from `EVIDENCE_MANIFEST.json`). A **separate, concurrent**
> CAMPAIGN_022 *execution* sprint subsequently ran C022 to a **REJECT** verdict on the
> same branch, in parallel. This does **not** retroactively contaminate C023: the ADX22
> arm was frozen here **before** any C022 results existed or were viewed, so it remains a
> genuine pre-registration, not tuning on C022's outcome. C023 itself remains
> `SCAFFOLD_ONLY` — unexecuted. See `STRATEGY_STATUS.md` for the current C022 (REJECT)
> and C023 (scaffold) statuses.

## Identity

| field | value |
|---|---|
| `campaign_id` | CAMPAIGN_023 |
| `strategy_name` | `h4_h1_pullback_resolution_entry` |
| `version` | `0.1.0-c023` |
| `working_name` | H4/H1 Pullback Resolution Entry — ADX22 |
| `promotion_eligible` | false |

## Hypothesis

Identical to C022. C020 (rejected) and C021 demand **strict same-direction alignment
across every timeframe** ("all green") and tend to enter after a move is already extended.
The pullback-resolution family tests the opposite, structurally-favored pattern:

> **H4 defines directional bias. H1 must be in a counter-trend pullback that still holds.
> M15 fires only when that pullback resolves back into the H4 direction.**

C023 additionally asks a single sensitivity question: **does requiring a marginally
stronger H4 trend (ADX ≥ 22 instead of ≥ 20) change selectivity/outcome?** This is a
robustness probe of the C022 strength gate, not a new thesis.

## Scope decision — H4 is the top timeframe (no D1 / no D1AGG)

Identical to C022. The daily layer is deliberately removed:

- **No D1AGG**, no `native_h4_derived_d1agg` provenance, no `aggregate_h4_to_d1`
  dependency, no M1-derived-D1AGG rejection logic. Provenance is three `m1_derived`
  layers only.
- **Known limitation:** no macro risk-on/risk-off regime filter. H4 structure is the
  highest context available. This is a scoping choice, not an oversight.

## Universe and timeframes

Identical to C022.

- **Pairs:** EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (seven majors)
- **Execution:** M15 (completed bars only)
- **Context:** H4 (bias), H1 (pullback state) — both joined with
  `htf_align.align_last_completed`
- **Top timeframe:** H4 (no D1, no D1AGG)

## Data provenance (mandatory)

Identical to C022.

| layer | source | notes |
|---|---|---|
| M15 execution | `m1_derived` | aggregated from Postgres M1 corpus |
| H1 context | `m1_derived` | same |
| H4 context | `m1_derived` | same |
| D1 / D1AGG | **not used** | no daily layer |

Config block: `configs/campaign_023_h4_h1_pullback_resolution_adx22.yaml` →
`data_provenance`. The provenance validator (`validate_c022_data_provenance`, shared)
**rejects** any config carrying a `d1agg_context` / `d1_*` key.

## H4 directional bias — multi-factor, slope-aware (THE ONLY DELTA)

Computed on completed H4 bars, read at the `align_last_completed` bar for the decision
time. Three directional votes plus one strength gate:

| factor | bullish vote | bearish vote |
|---|---|---|
| price vs EMA50 | `h4_close > h4_ema50` | `h4_close < h4_ema50` |
| EMA20 vs EMA50 | `h4_ema20 > h4_ema50` | `h4_ema20 < h4_ema50` |
| EMA50 slope over **3** completed H4 bars | slope > 0 | slope < 0 |

- **Strength gate (DELTA vs C022):** ADX(14) on H4 ≥ **22** (C022 uses ≥ 20). Below
  threshold → `range` → no trade. ADX is a gate, never a directional vote.
- **Bias = bullish** if ≥ **2 of 3** votes bullish AND ADX ≥ 22.
- **Bias = bearish** if ≥ 2 of 3 votes bearish AND ADX ≥ 22.
- **Else:** `range` / neutral → no trade.

This single threshold is the entire intentional difference between C023 and C022.

## H1 pullback state — the differentiator (unchanged from C022)

Computed on completed H1 bars, read at the `align_last_completed` bar. Lookback: **6**
completed H1 bars before the aligned bar.

**For H4-bullish bias, H1 must show a pullback that holds:**

- **Pullback** (either): within lookback, `low` touched `h1_ema20` **OR** `h1_rsi(14)`
  dipped below **45** (momentum reset).
- **Holds:** latest completed H1 `close ≥ h1_ema50` (slow line intact).

**For H4-bearish bias:** mirror — `high` touched `h1_ema20` OR RSI > **55**, and latest
H1 `close ≤ h1_ema50`.

If H1 is not in a holding pullback in the H4 direction → no trade.

## M15 resolution trigger (unchanged from C022)

Reuses `m15_pullback_and_reclaim`. Lookback: **8** completed M15 bars before the decision
bar (exclusive).

**Long (all required):** H4 bias bullish AND H1 in holding bullish pullback; in lookback
`low` touched ema20/ema50; reclaim `close[t] > ema20[t]` AND `close[t-1] <= ema20[t-1]`.
**Short:** mirror. **M15 execution floors:** ADX(14) ≥ **18** on M15; optional per-pair
`min_atr_pips` (empty default).

## Side rules (unchanged)

- Long only on H4-bullish + H1 holding-bullish-pullback + M15 reclaim.
- Short only on H4-bearish + H1 holding-bearish-pullback + M15 reclaim.

## Cost / session (unchanged)

- Spread filter enabled (`max_spread_to_atr_pct: 8.0`, per-pair caps).
- Session filter: rollover / Friday / Sunday blocks per campaign YAML.

## Stop / exit (unchanged)

| rule | value |
|---|---|
| initial stop | **2.0 × M15 ATR(14)** (prior-bar ATR at index −2) |
| time stop | **32** M15 bars (~8 hours) |
| take-profit | none |
| trailing | none |
| exit_model | `hard_stop_or_time` |

## Position sizing (unchanged)

- `risk_per_trade_pct: 0.25`, `max_risk_per_trade_pct: 0.50`
- `max_open_positions: 1`, `max_positions_per_instrument: 1`

## Execution realism metadata (unchanged)

```yaml
research_metadata:
  fill_timing: next_bar_open
  execution_realism: conservative
  evidence_use: approval_bound
  promotion_eligible: false
```

## Financing (unchanged)

| field | value |
|---|---|
| `financing_mode` | `none` (scaffold) |
| `financing_overlay_required` | true if future avg hold > 1 day |

## Warmup / alignment — no-lookahead requirements (unchanged, non-negotiable)

- Strict indicator warmup (`nan` until ready).
- Every H4/H1 derived value read at the `align_last_completed` bar for the decision time,
  never from the tail of the context frame. Slope/structure windows bounded to
  `time <= aligned_feature_time`.
- No signal if any HTF align returns `HTF_UNAVAILABLE` / `HTF_STALE` / blocked.
- Incomplete H1/H4 bars must never affect the M15 decision (`complete=True` only).
- Record `htf_feature_times` (`h4`, `h1`) on every signal; `validate_signal_provenance`
  returns `[]`.

## Scaffold deliverables (this sprint — no execution, no evidence)

1. `docs/research/CAMPAIGN_023_H4_H1_PULLBACK_RESOLUTION_ADX22_PRECOMMIT.md` (this file).
2. `configs/campaign_023_h4_h1_pullback_resolution_adx22.yaml` (frozen, `h4_adx_min: 22.0`).
3. Reuse of `src/forex_bot/strategies/h4_h1_pullback_resolution_entry.py`
   (`H4H1PullbackResolutionEntryStrategy`) with version `0.1.0-c023` and
   `campaign_id="CAMPAIGN_023"` passed at construction. **No logic fork; no broker /
   executor / oanda / loops imports.** Emits `Signal` only.
4. `tests/unit/test_h4_h1_pullback_resolution_adx22.py`.
5. `scripts/run_campaign_023_h4_h1_pullback_resolution_adx22.py` (preflight-only).

## Test plan (scaffold)

- C023 frozen config loads; `version == 0.1.0-c023`; `trading_enabled is False`.
- Provenance remains three `m1_derived` layers (M15/H1/H4); rejects `d1agg_*` / `d1_*`.
- **H4 bias gate delta:** with directional votes passing, bias **blocks at ADX 21.9** and
  **passes at ADX 22.0** (the C023 threshold). C022's gate still passes at ADX 20.0.
- Same synthetic market data → no logic difference other than the threshold behavior
  (C022 and C023 share the strategy class; only `h4_adx_min` differs).
- Emitted signal carries `campaign_id == "CAMPAIGN_023"`.
- `approved_strategies.yaml` remains `approved: []`.
- No broker/execution/oanda imports in the strategy source.

## Future execution gates (not run in scaffold)

Same gate discipline as C022 (train/validation-only first; no retuning; no test lockbox
unless both train and validation gates pass; backtrader parity PASS required; no
validation rescue if train fails; no approval under any outcome). Additionally, if both
C022 and C023 are ever executed, they must be compared as a **pre-registered pair**; the
ADX threshold is the only permitted difference, and neither may be retuned after results.

## No tuning rule

One frozen parameter set in YAML (`h4_adx_min: 22.0`). No sweeps. No parameter choice from
historical results without a new precommit campaign.

## No approval

`configs/approved_strategies.yaml` remains `approved: []`. Paper/demo/live blocked.
