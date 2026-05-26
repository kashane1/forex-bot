# Future Research Backlog

**Date:** 2026-05-26 · **Branch:** `infra-external-data-ingest-blocker-resolution-001`

> **Nothing in this document is authorized.** This is a menu of *possible*
> future directions, recorded so the research freeze does not lose
> institutional memory. Each item requires an explicit human decision
> before any work begins. The research is currently **frozen** — see
> `docs/research/FINAL_RESEARCH_DECISION_MEMO.md`. No strategy is
> approved; no campaign may be run on the strength of this list.
>
> **Broad seven-pair pattern strategy search is paused** (2026-05-26).
> Re-entry gates: [`BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md`](BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md).
> Trade-quality infrastructure sprints **complete**:
> [`INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md`](INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md),
> [`INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md`](INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md).

Ordering is rough priority. **Item 0** is the recommended next sprint.
Items 1–2 are infrastructure; items 3–4 are validation / diagnostics;
items 5–8 are genuinely new strategy research — **blocked until
broad-search re-entry gates are met.**

---

## 0. External data credentials or manual CSV setup (RECOMMENDED NEXT SPRINT)

- **Why it matters.** Full-window pipeline is built but **FRED_API_KEY absent**
  and `data/external_features/` empty. `cross_asset_missing` remains **2,142**.
  Operator must configure FRED auth or drop 2018+ CSVs.
- **Sprint name.** `infra-external-data-credentials-or-manual-csv-setup-001`
- **Scope.** Operator action sprint: set `FRED_API_KEY`, re-run
  `scripts/run_external_data_full_window_pipeline.py`, verify `cross_asset_missing`
  decreases. No broker order APIs.
- **Status.** **RECOMMENDED — BLOCKED ON OPERATOR AUTH/DATA.**

---

## 0-complete. External data ingest blocker resolution (COMPLETE)

- **Sprint.** `infra-external-data-ingest-blocker-resolution-001`
- **Delivered.** H4-aware observation window, full-window pipeline, fetch status
  reporting, local CSV template/validation, enhanced manifest, alignment audit,
  diagnostic re-run.
- **Summary.** [`INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md`](INFRA_EXTERNAL_DATA_INGEST_BLOCKER_RESOLUTION_001_SUMMARY.md)
- **Status.** **COMPLETE** — pipeline ready; FRED auth still blocked.

---

## 0-complete-prior. Cross-asset real-data ingest (COMPLETE)

- **Sprint.** `infra-cross-asset-real-data-ingest-001`
- **Delivered.** Source registry, FRED fetcher (blocked without key), local CSV
  loader, normalization, derived features, H4 availability alignment, COT design,
  diagnostic re-run.
- **Summary.** [`INFRA_CROSS_ASSET_REAL_DATA_INGEST_001_SUMMARY.md`](INFRA_CROSS_ASSET_REAL_DATA_INGEST_001_SUMMARY.md)
- **Status.** **COMPLETE** — pipeline ready; full-window data still blocked.

---

## 0-complete-prior. Cross-asset real-data ingest planning (SUPERSEDED)

- **Sprint name.** `infra-cross-asset-real-data-ingest-001` (planning entry — now complete)
- **Status.** **COMPLETE** — see above.

---

## 0-complete-mtf. Multi-timeframe confluence + cost atlas (COMPLETE)

- **Sprint.** `infra-multi-timeframe-confluence-and-cost-atlas-001`
- **Delivered.** Cost atlas (69,648 H4 bars), confluence prototype,
  cross-asset scaffolding, diagnostic runner, validation protocol.
- **Summary.** [`INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md`](INFRA_MTF_CONFLUENCE_AND_COST_ATLAS_001_SUMMARY.md)
- **Status.** **COMPLETE** — diagnostic only; no strategy approved.

---

## 1. Improve the financing / swap model

- **Why it might matter.** Financing (overnight swap) is currently
  unmodeled in the backtest engine — only a conservative stress overlay
  exists. It is an unconditional hard blocker for *any* live promotion.
  Until it is modelled, no backtest figure can be trusted as a net
  result.
- **Required data / code.** A reliable historical swap-rate source per
  instrument (broker financing tables or a data vendor); a financing
  accrual in `BacktestEngine` keyed on position carry and rollover
  timestamps; reconciliation against real OANDA financing transactions.
- **Risk of overfitting.** Low — this is a cost model, not a signal.
  The danger is *under*-modelling (optimism), not overfitting.
- **What would count as success.** Engine PnL includes financing;
  backtested financing reconciles within a small tolerance against real
  practice-account financing transactions; the conservative stress
  overlay can be retired.

## 2. Valid D1 (daily) backtest support

- **Why it might matter.** CAMPAIGN_006 could not test a daily-trend
  hypothesis at all: D1 candles close at the 17:00 NY rollover and the
  engine's intraday fill / session / spread machinery is invalid for
  them. A whole timeframe is currently untestable.
- **Required data / code.** Either (a) next-bar-open fills plus a
  non-rollover spread reference for true D1 candles, or (b) synthetic
  daily bars aggregated from already-validated H4 candles, with a
  documented, tested aggregation that avoids the rollover contamination.
  A non-rollover spread snapshot is required either way.
- **Risk of overfitting.** Low for the infrastructure itself; normal
  for any strategy later tested on D1.
- **What would count as success.** A D1 backtest of a known strategy
  produces results consistent with its H4 behaviour and with no
  session/spread artifacts; the CAMPAIGN_006 blocker is lifted.

## 3. Lean parity for one historical rejected campaign

- **Why it might matter.** The backtest engine is bespoke. Reproducing
  one rejected campaign (e.g. CAMPAIGN_002 trend baseline) in an
  independent engine (QuantConnect Lean) would validate the engine
  itself — that the REJECT verdicts are real, not an engine artifact.
- **Required data / code.** The `src/forex_bot/lean/` parity notes; a
  Lean project replicating one strategy + the same OANDA candles; a
  comparison of trade-by-trade output.
- **Risk of overfitting.** None — this is verification, not search.
- **What would count as success.** Lean and the bespoke engine agree on
  trade entries/exits and aggregate metrics for the chosen campaign
  within a small, explained tolerance.

## 4. Richer market-regime diagnostics

- **Why it might matter.** CAMPAIGN_005 measured one regime statistic
  (efficiency ratio 0.24 — choppy). A richer, time-resolved regime map
  (trend vs range vs volatile, per pair, per period) would let a future
  human judge *whether any tradable regime exists at all* before
  committing to a strategy campaign.
- **Required data / code.** A diagnostics script over the existing
  OANDA candle store; regime metrics (efficiency ratio, ADX
  distribution, autocorrelation, realised vol regimes); no strategy, no
  pass/fail gate.
- **Risk of overfitting.** Low if it stays descriptive. The danger is
  using the diagnostics to *reverse-engineer* a strategy to the sample —
  which must be explicitly avoided.
- **What would count as success.** A descriptive regime atlas that a
  human can read to decide whether further strategy research is even
  worthwhile — purely informational.

## 5. Non-FX or multi-asset research

- **Why it might matter.** The project tested six FX majors and found no
  edge. Other asset classes (index CFDs, commodities, crypto) have
  different regime and cost structures; an edge absent in FX majors may
  exist elsewhere — or the same null result may recur, which is itself
  informative.
- **Required data / code.** A data source and a verified candle store
  for the new asset class; instrument metadata; cost (spread / commission
  / financing) models appropriate to that class.
- **Risk of overfitting.** High — a new universe multiplies the search
  space. Strict pre-commit discipline and held-out test windows are
  mandatory.
- **What would count as success.** A strategy that passes a pre-committed
  screening **and** test window on real data for the new class, earning
  at most PAPER-TRADE-ONLY.

## 6. Carry / swap-aware research — only after item 1

- **Why it might matter.** Carry (holding positive-swap positions) is a
  recognised FX return source. But researching it *before* the financing
  model exists would be meaningless — carry research is entirely a
  financing-PnL question.
- **Required data / code.** A completed, reconciled financing model
  (item 1) is a hard prerequisite; historical swap rates; a
  carry-oriented signal.
- **Risk of overfitting.** Moderate — carry is a small, slow signal
  easily swamped by curve-fitting on a short sample.
- **What would count as success.** Net-of-financing positive expectancy
  on a pre-committed test window, with the edge attributable to carry
  rather than to price direction.

## 7. Mean-reversion revisit — only with a fresh human-approved thesis

- **Why it might matter.** Regime-filtered mean reversion was the only
  family with a real validation-era signal (CAMPAIGN_008/009). It is the
  most plausible place an edge could exist.
- **Required data / code.** A **genuinely new thesis** — not a tweak of
  c008/c009, not a relaxed gate. Possible angles: a different regime
  definition, a different universe, an explicit volatility filter. A
  fresh pre-commit and explicit human authorization.
- **Risk of overfitting.** High — mean reversion overfits easily, and
  the project has already looked at this data twice. A third look at the
  same data is especially dangerous; any revisit should prefer new data
  or a new universe.
- **What would count as success.** An **independent** train split that
  is non-negative (both prior campaigns failed exactly here), plus a
  passed test window — the bar c008/c009 could not clear.

## 8. News / economic-calendar filter research — only with reliable data

- **Why it might matter.** Large scheduled events (rate decisions, NFP)
  drive spread spikes and gaps. A filter that avoids trading around them
  could improve any future strategy's cost profile.
- **Required data / code.** A *reliable* historical economic-calendar
  data source with accurate timestamps — without it, this research is
  not worth starting. A calendar-aware filter in the risk engine.
- **Risk of overfitting.** Moderate — event windows are a tempting place
  to fit noise; the filter must be specified before seeing results.
- **What would count as success.** A calendar filter that measurably
  reduces adverse-cost trades on a pre-committed window without being
  tuned to specific historical events.

---

## Cross-cutting discipline (applies to every item above)

- No item is authorized; each needs an explicit human decision.
- Every strategy campaign needs a pre-commit written and committed
  *before* the run, with gates fixed in advance.
- The 2025–2026 reported test window stays a sealed lockbox until a
  screening gate passes.
- Best attainable verdict remains **PAPER-TRADE-ONLY** until financing
  is modelled; live trading is out of scope.
- A strategy is only ever runnable in a loop after a human adds it to
  `configs/approved_strategies.yaml`.
- See `docs/research/HYPOTHESIS_BACKLOG.md` for the earlier,
  campaign-era hypothesis list.
