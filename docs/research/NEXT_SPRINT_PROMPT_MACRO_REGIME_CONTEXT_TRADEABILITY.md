# Next Sprint Prompt — Macro/Rates/Calendar **Slow-Regime Tradeability Context**

**Type:** read-only research + lookahead-safe data infrastructure. **NOT** a strategy,
**NOT** a campaign, **NOT** CAMPAIGN_024, **NOT** C023, **NOT** approval, **NOT**
paper/demo/live, **NOT** fast-news trading. Framing locked by
`MACRO_REGIME_CONTEXT_TRADEABILITY_THESIS_FRAMING.md`.

> Core correction: this is **slow regime/context classification of USD/JPY tradeability**,
> not reacting to macro faster than institutions. We have no latency edge and do not
> pretend to. Macro context is a tradeability *conditioner / no-trade filter*, never an
> entry signal.

---

## Copy-paste prompt for the next sprint

```
We are starting the next forex-bot research sprint from the latest origin/main.

Sync and branch:

    cd /Users/kashane/dev/forex-bot
    git checkout main
    git pull --ff-only

Create a fresh branch:

    research-usdjpy-macro-regime-context-tradeability-001

This is a read-only research + lookahead-safe data-infrastructure sprint.
This is NOT fast-news trading. NOT an immediate event-reaction strategy.
NOT tick-level rate-correlation trading. NOT an attempt to beat institutions
on speed. NOT a strategy implementation. NOT a campaign. NOT CAMPAIGN_024.
NOT C023 execution. NOT paper/demo/live. NOT approval.

Context:
The compression/expansion family is exhausted and the standing verdict is
PAUSE_STRATEGY_RESEARCH (see USDJPY_LONDON_COMPRESSION_CONTINUATION_*). No
internal USD_JPY price-structure lead survives a hardened test. The ONLY
sanctioned non-strategy direction being explored is whether SLOW macro/rates/
calendar CONTEXT can classify USD/JPY tradeability — i.e. when NOT to trade and
when technical setups are more/less likely to survive. Framing is locked in
docs/research/MACRO_REGIME_CONTEXT_TRADEABILITY_THESIS_FRAMING.md — read it first.

Read first:
  * docs/research/MACRO_REGIME_CONTEXT_TRADEABILITY_THESIS_FRAMING.md
  * docs/research/USDJPY_LONDON_COMPRESSION_CONTINUATION_READINESS_DECISION.md
  * docs/research/USDJPY_SESSION_VOLATILITY_SPREAD_ATLAS.md
  * docs/research/USDJPY_EXTERNAL_THESIS_CANDIDATE_SCORECARD.md

Main goal:
Determine whether slow, lookahead-safe macro/rates/calendar CONTEXT helps
classify USD/JPY tradeability over M15/H1/H4 horizons — especially when to
stand aside — without any fast-news reaction and without touching TEST.

Hard rules:
  * No fast-news trading; no immediate event-reaction; no tick-level rate
    correlation; no latency-dependent logic; no live headline reaction.
  * No predicting USD/JPY from fast rate ticks; macro is a tradeability
    CONDITIONER / no-trade filter, never an entry signal.
  * Do not create CAMPAIGN_024; do not execute C023; do not implement a
    strategy; do not run a campaign; do not alter any verdict; do not rewrite
    metrics.
  * Do not modify configs/approved_strategies.yaml except to verify approved:[].
  * Do not enable paper/demo/live; do not modify broker/executor/order/live.
  * Do not call OANDA mutation/order APIs; do not use live credentials.
  * Use local materialized USD_JPY M15/H1/H4 read-only; .env only for research
    DB access; never print credentials.
  * Event calendar = PUBLIC SCHEDULE DATES ONLY (lookahead-safe); do not trade
    the event outcome. Rates/risk features must use as-of/lagged joins (only
    values published on/before the decision bar). Daily/weekly cadence only.
  * Keep the TEST window (2025-07-01+) SEALED.
  * Do not commit .env, credentials, DBs, raw candle dumps, parquet, huge CSVs.
  * Do not present descriptive statistics as tradable edge; no threshold-mining.

Preferred diagnostic categories (all slow, all lookahead-safe):
  1. Macro event-avoidance windows (FOMC/BOJ/CPI/NFP): pre/post-event
     volatility, spread, whipsaw — when to stand aside.
  2. Delayed post-event stabilization at +4h/+8h/+24h/+48h vs normal periods.
  3. Rate-differential regime (US-Japan, daily/weekly alignment only):
     does the slow regime correlate with USD/JPY drift/volatility REGIMES.
  4. Risk-regime context (VIX/SP500 proxy, slow cadence) if available.
  5. No-trade filters: regimes/windows where technical systems are
     structurally untradeable (cost/whipsaw).
  6. Setup-conditioning: "macro context conditions whether a future technical
     setup is worth testing," not "macro is the entry."

Suggested phases (commit after each):
  Phase 0 — branch from latest origin/main; verify approved:[], guards, C023
            not executed, C024 absent, TEST sealed; baseline pytest/ruff/freeze/
            archive/secret; write the PLAN doc; commit.
  Phase 1 — lookahead-safe data infra: ingest a static public economic-event
            calendar fixture (FOMC/BOJ/CPI/NFP dates only) + build as-of/lagged
            rates/risk regime features from the FRED cache (DGS2/DGS10/VIX/SP500,
            + JP rate leg if sourced). Unit tests for the as-of join + no
            lookahead. Commit.
  Phase 2 — read-only tradeability-context diagnostic: condition the existing
            USD/JPY M15 spread/vol/whipsaw and breakout-survival measures on
            event windows, post-event stabilization, rate-diff regime, and risk
            regime; report on BOTH train and validation. Compact summaries
            committed; bulky outputs gitignored. Commit.
  Phase 3 — robustness/falsification: year/half-split stability, lookahead
            audit, latency-independence check (results must survive applying
            features with a deliberate delay), no-trade-filter value, TEST
            untouched. Commit.
  Phase 4 — readiness decision: READY_FOR_PRECOMMIT_DESIGN / MORE_DIAGNOSTICS_
            REQUIRED / NOT_READY / PAUSE_STRATEGY_RESEARCH, using the 8-point
            slow-regime readiness bar from the framing doc. No C024. Commit.
  Phase 5 — final validation + summary; verify no verdict/approval/guard
            changes, no C024/C023, TEST sealed, no large/secret artifacts.

A future precommit is allowed ONLY if the result is slow-regime based,
lookahead-safe, latency-independent, not news-reactive, not speed-competitive,
supported on both train and validation without touching TEST, and expressed as
tradeability conditioning / no-trade filtering rather than a macro entry.
Otherwise the verdict is NOT_READY or PAUSE_STRATEGY_RESEARCH.

Final response: branch, commit hashes/files by phase, data infra built + its
lookahead-safety proof, tradeability-context findings on train AND validation,
robustness + latency-independence results, readiness decision, and explicit
confirmation of no campaign/C024/C023/approval/paper-demo-live/TEST changes.
```

---

## Operator notes

- The **highest-value, lowest-overfit** output is the **no-trade filter** (category 5):
  it withholds trades in structurally hostile windows and cannot manufacture false edge.
  Even if everything else is null, a validated no-trade filter is a useful, honest result.
- If the event calendar cannot be sourced cleanly as lookahead-safe schedule data, run
  categories 3–5 (rates/risk regime + no-trade filters) first; they rely only on the FRED
  cache already present.
- A null result is an acceptable, expected outcome → `PAUSE_STRATEGY_RESEARCH`. The point
  is to learn whether slow context conditions tradeability, not to manufacture a signal.
