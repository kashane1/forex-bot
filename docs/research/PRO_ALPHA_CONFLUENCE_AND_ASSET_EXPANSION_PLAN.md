# Pro-Alpha Confluence and Asset Expansion — Sprint Plan

**Date:** 2026-05-26  
**Branch:** `research-pro-alpha-confluence-and-asset-expansion-roadmap-001`  
**Base branch:** `research-broad-strategy-pause-and-roadmap-001`  
**Sprint type:** Research / design roadmap — **not** strategy implementation, backtest campaign, tuning, or paper/demo/live enablement.

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_018 will **not** be created. Rejected campaigns (C015–C017) will **not** be retuned.

---

## 0. Goal

Stop treating “entry signal” as the whole strategy. Before reopening strategy discovery, document a **trade-quality and asset-expansion layer** that sits between raw strategy signals and risk evaluation — multi-timeframe confluence, cross-asset regime confirmation, cost filters, exit overlays, and adaptive sizing rules.

This sprint produces **design documents and ranked implementation priorities only**. It does not implement features, run campaigns, or enable trading loops.

**Supersedes (for sequencing):** the prior selected next sprint `infra-observed-cost-and-spread-regime-diagnostics-001` is **folded into** this roadmap as ranked item #3 (observed spread/cost atlas). Cost diagnostics remain essential but are one layer of a broader trade-quality stack, not the sole next sprint.

---

## 1. Architectural constraint (binding)

The repo architecture is already clean:

```text
market data → strategy signal → risk evaluation → executor/broker
```

**Alpha and confluence belong before risk/execution.** The executor stays dumb and safe.

| layer | module | trade-quality responsibility |
|---|---|---|
| Data | `data/`, broker candles | Fetch/store W1/D1/H4/H1 and cross-asset series |
| Strategy / research | `strategies/`, `research/` | Emit `Signal` + `ConfluenceScore` / trade-quality metadata |
| Risk | `risk/` | Consume confluence grade, cost state, sizing overlay; approve/reject |
| Execution | `execution/` | Submit approved plans only — **no confluence logic** |

Existing `Signal.features: dict[str, Any]` can carry confluence metadata without executor changes. A future typed `ConfluenceScore` domain model is recommended before live use.

---

## 2. Phase 0 — truth audit

### 2.1 Current production paper universe

From `configs/paper.yaml` and `configs/practice.yaml`:

| dimension | value |
|---|---|
| instruments | EUR_USD, USD_JPY, GBP_USD, AUD_USD, USD_CAD |
| granularity | H4 |
| candle components | bid/ask (`BA`) |
| spread filter | enabled (`max_spread_to_atr_pct`, per-pair pip caps) |
| session filter | enabled (rollover blackout, etc.) |

Research track has expanded to **seven pairs** (adds NZD_USD, USD_CHF). Evidence still says **no strategy approved**; broad H4 pattern search is **paused**.

### 2.2 Evidence state (inputs to this sprint)

| check | status | note |
|---|---|---|
| CAMPAIGN_011 deduped null | **PASS** | exp_r ≈ −0.0029 R — canonical beat-null bar |
| CAMPAIGN_015–017 | **REJECT** | all WITHIN_NULL vs deduped null |
| Post-dedup meta-analysis | **PASS** | NO_RELIABLE_ARCHETYPE |
| Broad search pause | **PASS** | re-entry gates documented |
| CAMPAIGN_008 mean-reversion | **REJECT** (narrow) | validation positive but train fail — strongest mean-reversion clue |
| Exit instrumentation | **PASS** | trade records include R-multiple, spread paid, exit reason, gap flags |
| Financing in engine PnL | **FAIL (known gap)** | overlay only; blocks honest carry research |
| D1 backtest support | **FAIL (known gap)** | CAMPAIGN_006 blocker — W1/D1 confluence needs infrastructure |
| `configs/approved_strategies.yaml` | **PASS** | `approved: []` |
| research freeze | **PASS** | `scripts/check_research_freeze.py` |

### 2.3 Hard rules (all phases)

- Do not approve any strategy or edit `configs/approved_strategies.yaml` beyond confirming `approved: []`.
- Do not enable paper / demo / live trading loops beyond current blocked state.
- Do not create CAMPAIGN_018 or any new backtest campaign.
- Do not retune CAMPAIGN_015, CAMPAIGN_016, or CAMPAIGN_017.
- Do not call OANDA order APIs or submit broker orders.
- Do not commit credentials, SQLite DBs, or bulky trade dumps.
- Do not present design recommendations as tradable edge.

---

## 3. Ranked additions (sprint output)

Priority order for **implementation sprints after this design sprint**:

| rank | addition | role | doc |
|---:|---|---|---|
| 1 | Multi-timeframe confluence engine | Trade-quality gate | [`MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md`](MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md) |
| 2 | Cross-asset regime filters | Confirmation layer | [`CROSS_ASSET_FEATURE_ROADMAP.md`](CROSS_ASSET_FEATURE_ROADMAP.md) |
| 3 | Observed spread/cost atlas | Hard trade filter | [`CROSS_ASSET_FEATURE_ROADMAP.md`](CROSS_ASSET_FEATURE_ROADMAP.md) § cost |
| 4 | Financing / carry model | Eligibility + net PnL | [`CROSS_ASSET_FEATURE_ROADMAP.md`](CROSS_ASSET_FEATURE_ROADMAP.md) § carry |
| 5 | Daily/weekly multi-asset momentum lane | New strategy lane (future) | [`ASSET_EXPANSION_SHORTLIST.md`](ASSET_EXPANSION_SHORTLIST.md) |
| 6 | C008-style mean-reversion post-mortem | Research lane (no retune) | [`EXIT_AND_SIZING_OVERLAY_ROADMAP.md`](EXIT_AND_SIZING_OVERLAY_ROADMAP.md) § C008 |
| 7 | Divergence as filter/exit only | Not primary entry | [`MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md`](MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md) § divergence |
| 8 | Exit engine overlays | First-class research | [`EXIT_AND_SIZING_OVERLAY_ROADMAP.md`](EXIT_AND_SIZING_OVERLAY_ROADMAP.md) |
| 9 | Fractional-Kelly sizing | After calibrated probabilities | [`EXIT_AND_SIZING_OVERLAY_ROADMAP.md`](EXIT_AND_SIZING_OVERLAY_ROADMAP.md) § sizing |
| 10 | COT positioning | Slow confirmation | [`CROSS_ASSET_FEATURE_ROADMAP.md`](CROSS_ASSET_FEATURE_ROADMAP.md) § COT |

---

## 4. Five-layer trade-quality model

Every professional trade should pass:

```text
Layer 1 — Market regime        trend / range / high-vol / low-vol / risk-on / risk-off
Layer 2 — Multi-TF alignment   W1/D1/H4 agree, or explicit counter-trend MR thesis
Layer 3 — Cross-asset confirm  USD, rates, VIX, equities, gold, oil
Layer 4 — Local trigger        breakout / pullback / rejection / MR trigger
Layer 5 — Trade economics      spread/ATR, financing, expected R, portfolio heat
```

Only after all five pass should risk consider the trade. Confluence grade (A/B/C/reject) summarizes layers 1–4; layer 5 is enforced by existing and future cost/risk gates.

---

## 5. Phase plan

| phase | deliverable | commit |
|---:|---|---|
| 0 | This plan + truth audit | yes |
| 1 | [`MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md`](MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md) | yes |
| 2 | [`CROSS_ASSET_FEATURE_ROADMAP.md`](CROSS_ASSET_FEATURE_ROADMAP.md) | yes |
| 3 | [`EXIT_AND_SIZING_OVERLAY_ROADMAP.md`](EXIT_AND_SIZING_OVERLAY_ROADMAP.md) | yes |
| 4 | [`ASSET_EXPANSION_SHORTLIST.md`](ASSET_EXPANSION_SHORTLIST.md) | yes |
| 5 | [`PRO_ALPHA_CONFLUENCE_AND_ASSET_EXPANSION_SUMMARY.md`](PRO_ALPHA_CONFLUENCE_AND_ASSET_EXPANSION_SUMMARY.md) + validation | yes |

---

## 6. Expected outcomes

- Trade-quality layer **designed** to sit between strategy signals and risk — not inside the executor.
- Cross-asset and multi-timeframe features **ranked** for phased data ingestion (features first, tradable instruments later).
- Exit and sizing overlays **documented** as first-class research, with Kelly deferred until calibrated probabilities exist.
- Asset expansion **shortlisted** in three phases with explicit avoid list.
- Next implementation sprint (after this design sprint): **`infra-multi-timeframe-confluence-and-cost-atlas-001`** — local feature layer + spread atlas; still no strategy campaign.
- CAMPAIGN_018: **not created**.
- Strategies: **none approved**.

---

## 7. External evidence anchors (for future pre-registration)

| theme | source | implication for bot |
|---|---|---|
| Time-series momentum | [AQR — Time Series Momentum](https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum) | Multi-asset, multi-horizon momentum lane stronger than isolated H4 FX patterns |
| Value + momentum | [AQR — Value and Momentum Everywhere](https://www.aqr.com/Insights/Research/Journal-Article/Value-and-Momentum-Everywhere) | Factor context matters; negative correlation between value and momentum |
| Carry crash risk | [NBER w14473 — Carry Trades and Currency Crashes](https://www.nber.org/papers/w14473) | Carry requires financing + risk-regime modeling before strategy lane |
| Kelly criterion | [Kelly criterion (Wikipedia)](https://en.wikipedia.org/wiki/Kelly_criterion) | Fractional Kelly only after P(win), payoff, tail risk estimates |

---

## 8. Validation (Phase 5)

| check | expected |
|---|---|
| `pytest tests/ -q` | pass (no code changes expected) |
| `python scripts/check_research_freeze.py` | ALL CHECKS PASSED |
| `configs/approved_strategies.yaml` | `approved: []` unchanged |
