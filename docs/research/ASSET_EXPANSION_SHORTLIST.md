# Asset Expansion Shortlist

**Date:** 2026-05-26  
**Branch:** `research-pro-alpha-confluence-and-asset-expansion-roadmap-001`  
**Status:** Ranked shortlist for research — **no instruments added to production configs** this sprint.

---

## 1. Current universes

| context | instruments | granularity | notes |
|---|---|---|---|
| **Production paper/practice** | EUR_USD, USD_JPY, GBP_USD, AUD_USD, USD_CAD | H4 bid/ask | `configs/paper.yaml`, `configs/practice.yaml` |
| **Research (deduped campaigns)** | above + NZD_USD, USD_CHF | H4 bid/ask | C011–C017 seven-pair set |
| **Approved strategies** | none | — | `configs/approved_strategies.yaml`: `approved: []` |

Spread and session filters already active in production configs.

---

## 2. Expansion philosophy

```text
Phase 1 → add as data/features (filters for FX)
Phase 2 → add as tradable research instruments (after cost atlas)
Phase 3 → add FX crosses (after spread/ATR screening)
```

**Do not** expand tradable universe before cost atlas exists ([`CROSS_ASSET_FEATURE_ROADMAP.md`](CROSS_ASSET_FEATURE_ROADMAP.md) §3).

---

## 3. Phase 1 — features only (implement first)

No new tradable symbols in bot configs. Ingest for confluence only.

| priority | asset / data | feature use | source |
|---:|---|---|---|
| P0 | DXY or synthetic USD basket | USD regime | ICE DXY / derived from majors |
| P0 | US 2Y / 10Y yields | rates, funding | FRED DGS2, DGS10 |
| P0 | Yield curve features | rate differential | derived |
| P0 | VIX | risk-on/off | Cboe |
| P1 | S&P 500, Nasdaq | global risk | index daily |
| P1 | DAX, Nikkei | regional risk | index daily |
| P1 | Gold | USD / inflation / hedge confirm | OANDA XAU or vendor |
| P2 | Oil WTI/Brent | CAD / macro | OANDA or vendor |
| P2 | COT reports | positioning crowding | CFTC weekly |
| P2 | Economic calendar metadata | event windows | calendar API / fixtures |

---

## 4. Phase 2 — tradable research candidates

Promote only after **observed spread/ATR atlas** marks instrument/session as acceptable.

| rank | instrument | rationale | gate |
|---:|---|---|---|
| 1 | **XAU_USD** | Macro confirm + possible own lane; OANDA supported | spread/ATR ≤ research threshold |
| 2 | **Index CFDs** (SPX500, NAS100, GER40, JP225) | Momentum lane per AQR evidence | broker account + margin metadata |
| 3 | **XAG_USD** | similar to gold; often wider spread | likely filter-only until costs OK |
| 4 | **WTI / Brent** | CAD/macro; commodity momentum | broker symbol + financing model |

Verify each via OANDA instrument list and bid/ask history pull before any campaign pre-commit.

---

## 5. Phase 3 — FX crosses

Screen on H4 bid/ask spread/ATR vs ATR-percentile bands from cost atlas.

### 5.1 Tier A (highest research value)

Express JPY funding and risk themes without USD-only framing:

```text
EUR_JPY
GBP_JPY
AUD_JPY
CAD_JPY
CHF_JPY
```

### 5.2 Tier B (cross themes)

```text
EUR_GBP
AUD_NZD
EUR_AUD
GBP_AUD
EUR_CHF
```

### 5.3 Screening criteria (pass/fail)

| metric | pass (draft — calibrate in cost sprint) |
|---|---|
| median spread/ATR (H4) | below pair-specific p75 of current majors |
| hostile-session fraction | ≤ majors baseline |
| min history length | ≥ walk-forward window requirement |
| financing magnitude | documented before carry-sensitive crosses |

Failed screen → remain **filter-only** or exclude.

---

## 6. Explicit exclusion list

Not authorized for expansion in current roadmap:

| category | reason |
|---|---|
| Crypto | volatility, 24/7 session mismatch, data complexity |
| Single-stock CFDs | idiosyncratic risk, universe explosion |
| Exotic FX | spread/financing dominate edge |
| Low-liquidity commodities | cost + gap risk |
| Options | architecture mismatch |
| News scalping | latency + event model not built |
| Triangular arbitrage | execution-latency game; not H4 bot |

Also excluded by policy: martingale, grid, averaging down (`allow_martingale: false` in configs).

---

## 7. Pair-level research notes (seven-pair baseline)

From post-dedup archetype exploratory ranking (NOT approval):

| pair | note |
|---|---|
| NZD_USD | exploratory cells beat null — high variance |
| EUR_USD | mixed; C016 fold spikes |
| AUD_USD | mixed |
| USD_JPY | near null across C015–C017 — low marginal signal in current templates |
| USD_CHF | mixed |
| GBP_USD | mixed |
| USD_CAD | uniformly weak in C015–C017 |

Cross expansion should **not** overweight pairs based on exploratory fold cells alone (WITHIN_NULL aggregate).

---

## 8. Config touchpoints (future — not this sprint)

When an instrument graduates from research:

| file | change |
|---|---|
| `configs/paper.yaml` | `market.instruments`, spread caps |
| `configs/practice.yaml` | same |
| campaign YAMLs | pre-registered universe only |
| `research/` data store | hydration scripts |

Production five-pair universe **unchanged** until human approval + cost evidence.

---

## 9. Recommended next implementation sprint

After this design sprint:

**`infra-multi-timeframe-confluence-and-cost-atlas-001`**

- Build cost atlas for current five- and seven-pair sets.
- Prototype confluence scorer (H4 + synthetic D1).
- Begin Phase 1 feature ingest (DXY proxy, FRED yields, VIX) as read-only.

No CAMPAIGN_018. No `approved_strategies.yaml` edit.

---

## 10. Decision matrix (summary)

| question | answer this sprint |
|---|---|
| Add XAU_USD to paper.yaml? | **No** — design only |
| Add EUR_JPY to research hydration? | **Ranked Phase 3** — after cost screen |
| Add DXY as feature? | **Yes — Phase 1 priority** |
| Trade COT signals? | **No** — filter only |
| Expand to crypto? | **No** — excluded |
