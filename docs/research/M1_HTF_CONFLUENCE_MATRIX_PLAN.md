# M1 / HTF Confluence Response-Matrix — Plan

**Status:** PLANNED
**Date:** 2026-05-29
**Branch:** `research-m1-htf-confluence-sampling-matrix-001`
**Owner:** research
**Freeze state:** intact — this is a research-only factor-discovery / response-analysis
exercise. No campaign, no strategy, no approval, no paper/demo/live, no OANDA, no credentials.

---

## 0. What this is (and is not)

This sprint is a **factor-discovery and response-analysis exercise**. It asks one narrow
question:

> Do specific higher-timeframe (HTF) confluence *states* produce a statistically
> meaningful, repeatable directional bias in **1-minute (M1) forward movement**?

It is explicitly **NOT**:

- not a campaign (does **not** create `CAMPAIGN_032` or any campaign),
- not a strategy (no entry/exit rules, no stops, no position sizing, no PnL),
- not a backtest (no trades, no ledger, no equity curve),
- not an optimization (no parameter search, no train/validation/test split),
- not an approval (the approved-strategies registry stays empty; paper/demo/live stay blocked),
- not networked (runs entirely on the **local research Postgres** corpus; no OANDA, no credentials).

The deliverable is **knowledge**: a response matrix that characterises what (if anything)
happens to M1 price in the minutes after a given HTF context state occurs, and whether any
such effect exceeds random variation. The terminal decision (Phase 7) is one of
`NO_EDGE_FOUND` / `NEED_MORE_RESEARCH` / `FRONT_GATE_CANDIDATE_EXISTS`. Even a
`FRONT_GATE_CANDIDATE_EXISTS` verdict only *recommends a future front-gate screen* — it does
not start one.

## 1. Why this sprint, why now

The directional / microstructure **non-time-bar lane is retired** on the current corpus
(`NON_TIME_BAR_LANE_FINAL_DECISION.md`). Recent terminal results:

- CAMPAIGN_029 (10-pip USD_JPY range bars) → REJECT (cost-defeated).
- H16 overshoot-exhaustion fade → FAIL_FRONT_GATE (null-indistinguishable).
- H03 thin-move fade → FAIL_FRONT_GATE (cost-defeated, null-internal).
- No strategy approved; paper/demo/live blocked.

Those efforts repeatedly failed at the *monetisation* step (cost) or the *null* step
(indistinguishable from random). A recurring open question is more fundamental and upstream of
any trade construction: **is there any conditional structure in short-horizon FX returns at
all** once we condition on multi-timeframe context? This sprint deliberately strips away
trade mechanics (stops, costs-as-a-gate, PnL) and measures the **raw conditional forward
response** so that a "no signal anywhere" finding and a "signal exists but is uneconomic"
finding can be told apart. Spread is *recorded and reported* (spread-awareness), but it is a
descriptive axis here, not a pass/fail gate — gating belongs to a future front-gate screen,
not to factor discovery.

## 2. Baseline audit — infrastructure available

### 2.1 M1 source data (local research Postgres)

PostgreSQL store `market_data.candles`, keyed `(instrument, granularity, time_utc)`.
Loader: `forex_bot.data.postgres_candle_store.PostgresCandleStore.query_candles(...)`.
Config: `forex_bot.data.research_db.get_research_database_config()`.

Native M1 is stored under `source='oanda-practice-m1'`. Verified counts and coverage:

| Pair | M1 bars | Coverage (UTC) |
|---|---|---|
| USD_JPY | 1,844,454 | 2021-05-27 → 2026-05-26 (~5.0y) |
| EUR_USD | 1,843,476 | 2021-05-27 → 2026-05-26 (~5.0y) |

Each row carries `bid_o/h/l/c`, `ask_o/h/l/c`, `mid_o/h/l/c`, and `spread_open/high/low/close`
(= ask − bid), so **per-bar spread is available** for spread-awareness. (Tick/volume is *not*
returned by `query_candles`; volatility is therefore measured via ATR, not volume.)

### 2.2 Materialized higher timeframes

Built deterministically and lookahead-free from M1 by
`forex_bot.data.m1_timeframe_materialization` (`source='m1_materialized'`). H4 is stored
under granularity label **`H4M1`** (= "H4 aggregated from M1", to distinguish from any native
H4). Aggregation aligns to 17:00 America/New_York (OANDA convention),
`missing_policy='omit'`. Verified materialized counts:

| Pair | M5 | M15 | H1 | H4M1 |
|---|---|---|---|---|
| USD_JPY | 362,519 | 118,035 | 28,013 | 5,448 |
| EUR_USD | 360,972 | 116,628 | 27,249 | 5,234 |

These are the structure/trend timeframes this sprint conditions on. M1 is the **execution /
response** timeframe.

### 2.3 Reusable analysis components

- Indicators (`forex_bot.strategies.indicators`): `ema(series,length)`,
  `atr(high,low,close,length=14)`,
  `donchian_high/low(series,length)`, `rsi`, `sma`, `zscore`. Reused for the simple,
  explicit state primitives — no bespoke pattern recognition.
- C021 multi-timeframe loader (`forex_bot.research.campaign_021_loader`) demonstrates the
  **lookahead-safe "align last completed HTF bar onto the decision timestamp"** pattern. This
  sprint re-implements an equivalent as-of alignment (HTF feature usable on an M1 bar only
  after the HTF bar has *completed*), kept self-contained in the new module.
- Edge-discovery lab (`research.edge_discovery`): `windows.compute_forward_returns`,
  `matched_nulls.matched_null_baseline`, `cost_feasibility`. Conceptually reused for the
  Phase 5 null comparison (unconditional / randomized-timestamp / matched-null), though the
  M1-response framework implements its own self-contained null helpers for clarity, since the
  lab's matched-null API is shaped around H4 trade ledgers.
- Forward-excursion precedent: `forex_bot.research.mfe_mae` and
  `forex_bot.research.volatility_compression_expansion` (forward MFE/MAE in pips) — confirms
  the house convention for measuring excursions; the new module computes MFE/MAE directly on
  M1 mid paths.

### 2.4 Post-non-time-bar reset findings carried forward

- Effects in this corpus repeatedly collapse to ~0.50 reversion / within-null once cost and
  selection are accounted for. The bar for "interesting" is therefore: **bias must exceed a
  matched null**, not merely be non-zero.
- Selection noise is the dominant failure mode (best-of-N). Phase 5 must compare the
  *strongest* states against best-of-N expectations, not in isolation.
- Spread is materially correlated with the very conditions that look exciting (fast/large
  moves have wider spreads). Hence spread is recorded per event and reported alongside every
  effect, even though it does not gate factor discovery.

## 3. Method (overview; detail locked per phase)

1. **States (Phase 1).** A small, explicit set of HTF confluence states across three
   families (A: M5 structure + M15 trend; B: M15 structure + H1 trend; C: M15 structure +
   H1 + H4 trend). Primitives only: above/below EMA50, EMA50 slope sign, simple pullback,
   volatility compression (ATR percentile), breakout (Donchian). Each state carries a
   **context direction** (+1 long-context / −1 short-context) so forward returns can be
   signed *in the direction the state implies* and tested for bias.

2. **Response framework (Phase 2).** `src/forex_bot/research/m1_response_matrix.py`. Given a
   state's signed event series, record per event: timestamp, pair, state, session, spread,
   volatility. Measure **forward response** over 5/10/15/30/60 minutes: forward return, MFE,
   MAE, MFE/MAE, directional hit rate, P(positive), P(negative). No positions, no PnL.
   Lookahead-safe HTF alignment; events de-overlapped via rising-edge onset + a cooldown so
   forward windows are (near-)independent; weekend/data gaps handled by a horizon tolerance.

3. **Discovery passes (Phases 3–4).** USD_JPY first, then EUR_USD identically. Which states
   are strongest / random / sufficiently sampled / survive spread-awareness; cross-pair
   stability.

4. **Null comparison (Phase 5).** For the strongest states: unconditional baseline,
   randomized-timestamp null, and matched null (same session / count). Does the observed
   effect exceed random variation?

5. **Shortlist + decision (Phases 6–7).** ≤5 states tabulated; terminal verdict; at most one
   recommended future front-gate screen. No campaign, no strategy.

6. **Validation (Phase 8).** Full test suite, lint, and all three freeze guards
   (`check_research_freeze`, `validate_research_archive`, `scan_artifacts_for_secrets`) must
   pass; freeze remains intact.

## 4. Hard rules (restated, binding for every phase)

Do **not**: create CAMPAIGN_032 or any campaign; build a strategy; run train/validation/test;
create entry/exit rules; optimize parameters; approve any strategy; enable paper/demo/live;
call OANDA APIs; use credentials; produce trading recommendations.

Success = we learn *whether* any HTF confluence state creates statistically meaningful M1
forward response. Success does **not** require finding one, and explicitly does not include
building or approving anything tradable.

## 5. Artifacts by phase

| Phase | Artifact |
|---|---|
| 0 | `docs/research/M1_HTF_CONFLUENCE_MATRIX_PLAN.md` (this doc) |
| 1 | `docs/research/M1_HTF_CONFLUENCE_STATE_DEFINITIONS.md` |
| 2 | `src/forex_bot/research/m1_response_matrix.py` + tests |
| 3 | `docs/research/USDJPY_M1_RESPONSE_MATRIX_RESULT.md` |
| 4 | `docs/research/EURUSD_M1_RESPONSE_MATRIX_RESULT.md` |
| 5 | `docs/research/M1_RESPONSE_MATRIX_NULL_COMPARISON.md` |
| 6 | `docs/research/M1_CONFLUENCE_STATE_SHORTLIST.md` |
| 7 | `docs/research/M1_RESPONSE_MATRIX_DECISION.md` |
| 8 | `docs/research/M1_HTF_CONFLUENCE_MATRIX_SUMMARY.md` |
