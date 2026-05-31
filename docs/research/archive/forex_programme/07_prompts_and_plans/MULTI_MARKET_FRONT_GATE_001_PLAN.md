# Multi-Market Front Gate 001 — Plan

**Branch:** `research-multi-market-front-gate-and-nonusd-crosses-001`
**Type:** research infrastructure + preparation. Docs-only this sprint.
No strategy, no campaign, no backtest, no ingestion, no broker calls.
**Date:** 2026-05-29.

## Why this sprint exists

The forex corpus viability review
(`FOREX_CORPUS_VIABILITY_AND_MARKET_SELECTION_001_SUMMARY.md`) reached a
clear strategic decision:

- The OANDA seven-major FX corpus remains a useful **control/baseline**.
- Broad strategy mining on the current corpus is **paused**; re-tuning
  rejected ideas is **prohibited**.
- Future work should **expand the search space**, not mine the same one.
- Recommended direction: **build a multi-market front-gate discovery lab
  and add non-USD FX crosses as the first expansion**
  (`NEXT_MARKET_SELECTION_DECISION.md`).

This sprint produces the **design and preparation artifacts** for that
direction. It does **not** implement data ingestion or any strategy — it
makes the next implementation sprint cheap, uniform, and safe.

## Current state (baseline audit)

### Research corpus (data model)
- **Instruments:** 7 USD-legged majors — EUR_USD, GBP_USD, USD_JPY,
  AUD_USD, NZD_USD, USD_CAD, USD_CHF. **No non-USD crosses; no other
  asset classes.**
- **Granularity:** ~6.4y of H4 (bid/ask), with M1-derived lower
  timeframes materialized and verified; D1 via next-bar-open aggregation
  (`D1AGG`). Non-time bars (range/volatility) builders exist in
  `src/forex_bot/data/non_time_bars.py` (lookahead-free, tested).
- **Cross-asset features:** FRED ingest is wired (DXY-proxy/yields/VIX
  style features) for confluence/diagnostics — features, not tradables.
- **Cost model:** per-instrument spread at decision bar (bid/ask),
  fill slippage, and a financing overlay (modeled/observed paths);
  conservative-but-realistic retail.

### Ingestion model
- OANDA candle ingestion + a research candle store, with export /
  rehydrate / M1-materialization scripts under `scripts/` (e.g.
  `ingest_oanda_candles_postgres.py`, `export_postgres_research_candles.py`,
  `materialize_m1_derived_timeframes.py`). Read-only OANDA health-check
  exists; **no order APIs are used in research.**
- Data lives outside git (gitignored store); the repo carries the
  loaders, schema, parity, and validation — not the raw candles.

### Front-gate infrastructure (the lab)
- The import-isolated edge-discovery lab at `research/edge_discovery/`
  is the **mandated front gate** for any new idea. It provides:
  - **matched-null benchmark** (is the effect distinguishable from a
    structure-matched random baseline?),
  - **filter-ablation** (does each filter add value or is it a
    forking path?),
  - **multiple-comparison correction** (is the best-of-N just
    best-of-N noise?),
  - **cost-feasibility** (does the gross effect survive realistic
    spread + slippage + financing?).
- It has correctly demoted real-looking results to selection noise
  (C028) and "loses less than random" (C027), and is the reason the
  programme's negative findings are trustworthy.

### Freeze / approval state
- `configs/approved_strategies.yaml` is **empty**; `forex_bot.approval`
  fails closed; every paper/demo/live loop refuses.
  `STRATEGY_STATUS.md` asserts NO-GO. `scripts/check_research_freeze.py`
  and `scripts/validate_research_archive.py` enforce this.

## Expansion goals (this sprint, docs-only)

1. **Design a multi-market research universe** (current majors + the
   eight candidate non-USD crosses + future asset classes), with a
   per-instrument expected cost/liquidity/feasibility profile.
2. **Generalize the front-gate framework** so the same
   discovery → factor-validation → front-gate → campaign → promotion
   pipeline applies to FX majors, FX crosses, futures, metals, and
   crypto — with required evidence defined at each stage.
3. **Assess non-USD cross feasibility** — cost profile, advantages over
   USD majors, whether they address USD-leg crowding, and whether they
   are worth adding (design only, no ingestion).
4. **Write a data-acquisition roadmap** (sources, free/local options,
   storage, preprocessing, integration complexity), prioritized
   crosses → other FX → crypto → futures → rest.
5. **Choose exactly one next expansion path** and write the **next
   implementation prompt** for it — which itself stops before strategy
   research and campaign creation.

## Assumptions

- The cost wall is the binding constraint (viability review): any new
  market is judged first on whether its cost/structure plausibly changes
  the two-sided spread+financing squeeze, not on idea cleverness.
- Same execution-realism discipline carries over: lookahead-free,
  parity-checked candles and **instrument-specific** cost models (a
  cross's spread is *not* EUR_USD's).
- Free/local data only; no broker calls, no credentials, no paid feeds
  in the implementation that follows — if a market needs paid data, that
  is a documented blocker, not an action.
- The edge-discovery lab is the single front gate; new markets plug into
  it rather than spawning bespoke gates.

## Non-goals (explicitly out of scope)

- **No CAMPAIGN_032 or any campaign.** No strategy. No entry/exit logic.
- **No backtests; no train/validation/test evidence; no parameter
  tuning.** No reviving rejected ideas.
- **No ingestion this sprint** — this is design/preparation; ingestion is
  the *next* sprint, behind its own prompt.
- **No approval; no paper/demo/live enablement; no broker/credential
  use.** Freeze stays intact.

## Deliverables (one per phase)

| Phase | Document |
|-------|----------|
| 0 | `MULTI_MARKET_FRONT_GATE_001_PLAN.md` (this) |
| 1 | `MULTI_MARKET_RESEARCH_UNIVERSE.md` |
| 2 | `MULTI_MARKET_FRONT_GATE_FRAMEWORK.md` |
| 3 | `NON_USD_CROSS_FEASIBILITY_STUDY.md` |
| 4 | `MULTI_MARKET_DATA_ACQUISITION_ROADMAP.md` |
| 5 | `NEXT_DATA_EXPANSION_DECISION.md` |
| 6 | `NEXT_PROMPT_AFTER_MULTI_MARKET_FRONT_GATE.md` |
| 7 | `MULTI_MARKET_FRONT_GATE_AND_NONUSD_CROSSES_001_SUMMARY.md` |

## Success criteria

The repo is prepared to explore new markets and datasets — a designed
universe, a generalized front-gate framework, a non-USD-cross
feasibility verdict, a prioritized data-acquisition roadmap, a single
chosen expansion path, and the exact next implementation prompt — **with
no strategy, no campaign, and no trading system created, and the freeze
intact.**
