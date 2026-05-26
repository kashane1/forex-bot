# Pro-Alpha Confluence and Asset Expansion — Sprint Summary

**Date:** 2026-05-26  
**Branch:** `research-pro-alpha-confluence-and-asset-expansion-roadmap-001`  
**Base:** `research-broad-strategy-pause-and-roadmap-001`

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_018 was **not** created.

---

## 1. Sprint outcome

Documented a **trade-quality and asset-expansion layer** that sits between strategy signals and risk evaluation — before reopening strategy discovery. Alpha/confluence is produced in strategy/research; risk consumes grades; executor stays dumb.

**Supersedes sequencing:** prior next sprint `infra-observed-cost-and-spread-regime-diagnostics-001` is **subsumed** as ranked item #3 (cost atlas) inside the broader roadmap, not abandoned.

---

## 2. Deliverables

| document | purpose |
|---|---|
| [`PRO_ALPHA_CONFLUENCE_AND_ASSET_EXPANSION_PLAN.md`](PRO_ALPHA_CONFLUENCE_AND_ASSET_EXPANSION_PLAN.md) | Master plan, truth audit, five-layer model, phase plan |
| [`MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md`](MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md) | `ConfluenceScore`, MTF states, divergence rules, validation protocol |
| [`CROSS_ASSET_FEATURE_ROADMAP.md`](CROSS_ASSET_FEATURE_ROADMAP.md) | Phase 1 features, cost atlas, financing/carry, COT |
| [`EXIT_AND_SIZING_OVERLAY_ROADMAP.md`](EXIT_AND_SIZING_OVERLAY_ROADMAP.md) | Exit catalog, C008 post-mortem lane, Kelly deferral |
| [`ASSET_EXPANSION_SHORTLIST.md`](ASSET_EXPANSION_SHORTLIST.md) | Phased instrument shortlist + avoid list |
| This summary | Close-out |

---

## 3. Architectural decision (binding)

```text
market data → strategy signal (+ ConfluenceScore) → risk evaluation → executor/broker
```

- **Strategy/research:** emit `Signal.features["confluence"]` (future typed `ConfluenceScore`).
- **Risk:** grade gates, cost state, sizing multiplier (1.25× / 1.0× / 0.5× / reject).
- **Executor:** no confluence logic — submit approved plans only.

Existing [`Signal.features`](../../src/forex_bot/domain/signals.py) supports prototype without executor changes.

---

## 4. Ranked additions (implementation priority)

| rank | addition | role |
|---:|---|---|
| 1 | Multi-timeframe confluence | Trade-quality gate |
| 2 | Cross-asset regime filters | Confirmation |
| 3 | Observed spread/cost atlas | Hard filter |
| 4 | Financing / carry model | Net PnL + eligibility |
| 5 | Multi-asset momentum lane | Future strategy (AQR-backed) |
| 6 | C008 mean-reversion post-mortem | Research lane — no retune |
| 7 | Divergence filter/exit only | Not standalone entry |
| 8 | Exit engine overlays | First-class research |
| 9 | Fractional-Kelly sizing | After calibrated probabilities |
| 10 | COT positioning | Slow confirmation |

---

## 5. Five-layer trade-quality model

```text
Layer 1 — Market regime
Layer 2 — Multi-timeframe alignment
Layer 3 — Cross-asset confirmation
Layer 4 — Local trigger quality
Layer 5 — Trade economics (spread, financing, R, heat)
```

Confluence grade **A / B / C / reject** summarizes layers 1–4; layer 5 ties to cost atlas + existing spread filter.

---

## 6. Key design choices

| topic | decision |
|---|---|
| Entry signal | Not the whole strategy — quality layer required |
| Confluence test | Conditional probability lift (exp_r, not win rate alone) |
| Cross-asset | Features first; tradable expansion Phase 2+ |
| Divergence | MR boost + exit de-risk only; never sole entry |
| Exits | Research parity with entries; stops/time dominate losses |
| Kelly | Deferred until P(win), payoffs, tail risk calibrated |
| Interim sizing | A=1.25×, B=1.0×, C=0.5×/skip — capped by max_risk |
| C008 | Post-mortem when-it-worked study — **no retune** |
| CAMPAIGN_018 | Not created |
| C015–C017 | Not retuned |

---

## 7. Asset expansion summary

| phase | content |
|---|---|
| **1 — features** | DXY, yields, VIX, equities, gold, oil, COT, calendar |
| **2 — tradable** | XAU_USD, index CFDs, oil — after cost atlas |
| **3 — FX crosses** | JPY crosses, EUR_GBP, AUD_NZD, etc. — after spread screen |
| **avoid** | crypto, single stocks, exotics, options, arb, grid/martingale |

Production paper universe unchanged: **five majors**, H4 bid/ask.

---

## 8. Infrastructure gaps acknowledged

| gap | blocks |
|---|---|
| D1/W1 from broker candles | CAMPAIGN_006 rollover issue — synthetic D1 from H4 or engine fix |
| Financing in engine PnL | honest carry research |
| Cross-asset feature store | Phase 1 ingest sprint |
| Cost atlas | structural tradability gating |

---

## 9. Recommended next sprint

**`infra-multi-timeframe-confluence-and-cost-atlas-001`**

Scope:

1. Observed spread/cost atlas on deduped H4 bid/ask (five- + seven-pair).
2. Confluence scorer prototype (H4 regime + synthetic D1).
3. Begin read-only Phase 1 feature ingest (DXY proxy, FRED yields, VIX).

Still: **no strategy campaign**, no broker orders, no approval.

Alternative narrower start: run **`infra-observed-cost-and-spread-regime-diagnostics-001`** first as cost-atlas-only slice of rank #3.

---

## 10. Re-entry to strategy discovery (unchanged)

Broad H4 pattern search remains **paused**. New strategy requires re-entry gates from [`BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md`](BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md):

- structural change (new data, thesis, cost model, timeframe, external evidence)
- pre-registered hypothesis beating deduped null ≥ **0.05 R**
- DEDUPED_INPUT, human memo, no `approved_strategies.yaml` edit from agent

This sprint adds **trade-quality infrastructure** as a prerequisite — not a bypass.

---

## 11. Validation

| check | result |
|---|---|
| Code changes | none (docs only) |
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_018 | not created |
| Broker order APIs | not called |

Run before merge:

```bash
pytest tests/ -q
python scripts/check_research_freeze.py
```

---

## 12. Suggested registry updates (on merge)

- Add section to [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) for PRO_ALPHA_CONFLUENCE_001.
- Update [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md) item 0 to reflect trade-quality stack vs cost-only sprint.
- Optional: supersede note in [`NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md`](NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md).

Not required for sprint close-out; human may batch with merge commit.
