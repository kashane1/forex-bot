# Strategy-Search Pause — After USD_JPY Macro-Context

**Sprint:** `strategy-search-pause-after-usdjpy-macro-context-001` · **Phase 1**
**Standing decision:** `PAUSE_STRATEGY_RESEARCH`. No strategy approved;
`configs/approved_strategies.yaml` = `approved: []`; paper/demo/live blocked.

---

## 1. Executive summary

Strategy research on the **current data and thesis set is paused.** Across a long,
systematically-diagnosed program, every internal research path has been exhausted:
price-structure / technical / microstructure lanes, USD_JPY specialization, post-entry
trade-management rescue, intraday volatility-compression→expansion, and — correctly framed
as slow context, not speed — the macro/rates/calendar tradeability overlay. None produced a
robust, cost-surviving, out-of-sample, overfit-hardened edge. The disciplined action is to
**stop mining the current data**, preserve the infrastructure, and not restart until a
genuinely new thesis or new data source meets the restart criteria.

This is not a failure of process — it is the process working: the diagnostics repeatedly
killed plausible-looking leads *before* they could become false confidence.

## 2. Why — the exhausted lanes

1. **Price-structure / technical entry signals failed.** Campaigns through C021 and the
   C022/C023 H4/H1 pullback-resolution family produced no entry edge; feature-separation
   showed the structural entry features sit at AUC ≈ 0.50.
2. **USD_JPY specialization failed.** Narrowing to a single, "less-bad" pair did not reveal
   a hidden edge; the entry-edge null generalized to USD_JPY.
3. **Stop-loss / trade-management rescue failed.** Post-entry early-exit counterfactuals
   *reduced* expectancy; the apparent gains lived in unbounded held risk, not a capturable
   signal.
4. **Volatility-compression → expansion failed.** Compression predicts *smaller* absolute
   future range (vol clustering), direction is null, and aggregate monetization loses on
   train. The one post-hoc lead (London continuation) **failed overfit-hardened
   confirmation**: every realistic intrabar protective stop turned it −3 to −8 pips on both
   splits, conservative cost flipped train negative, the Bonferroni ×12 haircut removed
   significance, and the effect was a 2022/2024 trend-regime artifact.
5. **Slow macro/rates/calendar context failed.** Lookahead-safe and latency-independent, but
   with no actionable tradeability conditioning: raw spread is flat across all macro
   contexts, whipsaw ≈ 0.50 everywhere, event-window vol effects are mechanical and
   direction-blind, and the rate-differential regime is non-identifiable on the 2021–2025
   single-cycle history (and the JP leg is absent).

## 3. What NOT to do next (hard prohibitions)

- ❌ No more EMA / ADX / reclaim / pullback-depth indicator variants.
- ❌ No more C022 / C023 mining (the family is retired; ADX22 not supported).
- ❌ No more USD_JPY microstructure mining (entry + management lanes closed).
- ❌ No more stop / exit tweaks framed as a strategy rescue.
- ❌ No more macro-context mining **without new data** (rate-regime is non-identifiable on
  current history).
- ❌ No "try ADX 25 / M5 instead of M15 / one more filter / 2.5-ATR stop."
- ❌ No `CAMPAIGN_024` (or any new campaign number) until the restart criteria are met.
- ❌ No presenting any existing lead (incl. the no-stop London lead) as actionable.

## 4. What remains valuable (preserve, do not discard)

The research **infrastructure** is the durable asset and is fully intact:

- **Materialized data store:** USD_JPY M1 (1.84M) / M5 / M15 (118k) / H1 / H4, plus majors,
  with bid/ask + spread, in the research Postgres `market_data.candles`.
- **M1→timeframe materialization** pipeline.
- **MFE/MAE reconstruction** tooling (`research/mfe_mae`, `reconstruct_mfe_mae_*`).
- **Trade-lifecycle / feature-capture** tooling (`research/lifecycle_features`,
  `post_entry_trade_management`, `microstructure_confirmations`).
- **Session / cost atlas** (`research/cost_atlas`, `build_usdjpy_session_volatility_spread_atlas.py`).
- **Volatility compression/expansion taxonomy** (`volatility_compression_expansion.py`).
- **Macro-regime overlay scaffolding** (`macro_regime_context.py`: lookahead-safe as-of join,
  FRED regime features, public-schedule event calendar).
- **Research-freeze + approval gates** (`check_research_freeze.py`,
  `validate_research_archive.py`, `scan_artifacts_for_secrets.py`, `approved_strategies.yaml`).
- **Backtrader / parity + execution-realism** infrastructure.

All of the above are reusable the day a genuinely new thesis or dataset arrives.

## 5. Standing decision

- **`PAUSE_STRATEGY_RESEARCH`** on the current data/thesis set.
- **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`.
- Paper / demo / live remain **blocked**. C023 not executed; C024 not created.
- Restart is gated by `STRATEGY_RESEARCH_RESTART_CRITERIA.md`; lessons in
  `FOREX_BOT_RESEARCH_LESSONS_LEARNED_001.md`; next actions in
  `NEXT_ACTION_OPTIONS_AFTER_STRATEGY_SEARCH_PAUSE.md`.
