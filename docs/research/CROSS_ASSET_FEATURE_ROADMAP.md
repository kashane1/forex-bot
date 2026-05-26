# Cross-Asset Feature Roadmap

**Date:** 2026-05-26  
**Branch:** `research-pro-alpha-confluence-and-asset-expansion-roadmap-001`  
**Status:** Design only — features/filters first; tradable expansion later.

> Cross-asset series feed the confluence engine and cost model. They do **not** trigger trades directly in Phase 1.

---

## 1. Principle

FX pairs often react to dollar trend, rates, equities, volatility, gold, oil, and risk appetite. Add these as **confirmation features** before adding them as tradable instruments.

Distinction:

| mode | purpose | when |
|---|---|---|
| **Feature / filter** | Regime context for FX signals | Phase 1 |
| **Tradable instrument** | Own strategy lane after cost atlas | Phase 2+ |

---

## 2. Phase 1 — data/features only

### 2.1 Priority feature set

| asset / source | feature role | primary pairs affected | data source (initial) |
|---|---|---|---|
| **DXY / broad USD index** | USD regime filter | all USD pairs | ICE US Dollar Index futures proxy or weighted USD basket from majors |
| **US 2Y yield (DGS2)** | rates / funding | USD_JPY, USD_CHF, carry | [FRED DGS2](https://fred.stlouisfed.org/series/DGS2) |
| **US 10Y yield (DGS10)** | rates / macro | USD crosses, gold correlation | [FRED DGS10](https://fred.stlouisfed.org/series/DGS10) |
| **Yield curve / diffs** | rate differential | JPY, CHF funding | derived: DGS10 − DGS2, pair-rate spread features |
| **VIX** | risk-on / risk-off | JPY, CHF, AUD, NZD, CAD | Cboe VIX index / futures settlement |
| **S&P 500 / Nasdaq** | risk appetite | AUD, NZD, JPY, CAD | index daily closes (vendor or broker CFD if available) |
| **DAX / Nikkei** | regional risk | EUR, JPY crosses | index daily closes |
| **Gold (XAU_USD)** | USD / real-rate / hedge | USD weakness confirm | OANDA if available; else vendor |
| **Oil (WTI / Brent)** | CAD / inflation / risk | USD_CAD, NOK (future) | OANDA / vendor |
| **COT positioning** | crowding / slow sentiment | currencies, rates, VIX | [CFTC COT](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) |
| **Economic calendar** | event-window risk | all | existing calendar research lane (C014) — metadata only |

References: [ICE US Dollar Index](https://www.ice.com/products/194/US-Dollar-Index-Futures) · [Cboe VIX](https://www.cboe.com/tradable_products/vix/).

### 2.2 Feature schema (v0)

Store in research cache / SQLite side tables — not in strategy code as hard-coded API calls.

```python
# Illustrative — not implemented this sprint
CrossAssetSnapshot = {
    "as_of": "2026-05-26T00:00:00Z",
    "usd_regime": "strengthening" | "weakening" | "neutral",
    "risk_regime": "risk_on" | "risk_off" | "neutral",
    "rates_bias": "higher" | "lower" | "flat",
    "vix_level": float,
    "vix_change_5d": float,
    "gold_confirm_usd_weak": bool | None,
    "oil_confirm_cad": bool | None,
    "cot_crowding": dict[str, str],  # e.g. {"EUR": "net_long_extreme"}
}
```

Confluence consumes `CrossAssetSnapshot` — see [`MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md`](MULTI_TIMEFRAME_CONFLUENCE_DESIGN.md).

### 2.3 Ingestion architecture

```text
External sources (FRED, CFTC, optional vendor)
  → research/cross_asset/ ingest scripts (read-only)
  → normalized Parquet or SQLite feature store
  → joined at bar timestamp in backtest / paper loop

OANDA candles (where instrument exists)
  → same candle pipeline as FX
  → bid/ask for cost-aware features
```

**Hard rule:** ingest scripts are read-only research tools — no broker order APIs.

OANDA instrument endpoint supports bid/ask candle components for tradable symbols: [OANDA Developer — Instrument](https://developer.oanda.com/rest-live-v20/instrument-ep/).

---

## 3. Observed spread / cost atlas (rank #3)

Merged from prior sprint `infra-observed-cost-and-spread-regime-diagnostics-001`.

### 3.1 Purpose

Before asking “is the signal good,” determine whether the pair/session/timeframe is **structurally tradable** after spread.

C015–C017 all **worsen under 2× cost** — cost gating is mandatory for any future strategy.

### 3.2 Atlas dimensions

| segment | metrics |
|---|---|
| pair | spread pips, spread/ATR, round-trip drag |
| session (UTC / NY) | median, p90, hostile-window flags |
| weekday | rollover-adjacent degradation |
| vol regime | ATR percentile buckets |
| walk-forward fold | fold-specific cost drift |

### 3.3 Outputs

| artifact | use |
|---|---|
| `research/cost_atlas/spread_by_pair_session.json` | risk hard filter thresholds |
| `research/cost_atlas/hostile_windows.md` | human-readable ban list |
| per-bar `cost_state` | confluence `acceptable` / `marginal` / `hostile` |

### 3.4 Integration

- **Risk engine:** reject or downgrade when `cost_state == hostile` (extends existing `SpreadFilterConfig`).
- **Confluence:** layer 5 trade economics — see five-layer model in [`PRO_ALPHA_CONFLUENCE_AND_ASSET_EXPANSION_PLAN.md`](PRO_ALPHA_CONFLUENCE_AND_ASSET_EXPANSION_PLAN.md).
- **Strategy research:** no new campaign without cost atlas baseline for universe.

Data: local deduped H4 bid/ask (same stores as C011–C017). **No new OANDA order traffic.**

---

## 4. Financing / carry model (rank #4)

### 4.1 Why it blocks honest research

Carry is one of the few academically documented FX premia, but [Brunnermeier, Nagel, Pedersen (NBER w14473)](https://www.nber.org/papers/w14473) document **crash risk** during risk-off and funding stress.

Current bot state:

- Engine PnL **excludes** historical financing (overlay at report time only).
- Carry strategies cannot be tested honestly without accrual in engine or validated overlay.

### 4.2 Roadmap

| step | deliverable |
|---|---|
| F-1 | Observed swap capture from practice account (existing pilot spec) |
| F-2 | Historical financing fixtures per instrument |
| F-3 | Engine accrual or reconciled post-bar financing debit |
| F-4 | Carry **eligibility** feature: positive carry + risk regime OK |
| F-5 | Pre-registered carry lane campaign (only after F-3) |

Carry is a **future strategy lane**, not a confluence tweak.

Existing docs: [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md), [`FINANCING_MODEL_001_PLAN.md`](FINANCING_MODEL_001_PLAN.md).

---

## 5. COT positioning (rank #10)

Weekly CFTC Commitments of Traders — slow confirmation, not entry trigger.

| use | rule |
|---|---|
| Block trend add-on | extreme net positioning same direction as trade |
| Boost MR caution | extreme positioning + HTF range |
| Macro filter | Treasury / VIX / commodity index positioning for regime |

Lag: report weekly; align to Friday release with no lookahead in backtests.

---

## 6. Phase 2 — tradable research instruments (after cost atlas)

Add only when spread/ATR screening passes on OANDA (or declared broker):

| instrument | condition |
|---|---|
| XAU_USD | spread/ATR acceptable on H4 |
| XAG_USD | same; often wider — likely filter-only initially |
| WTI / Brent CFD | broker + cost model support |
| SPX500 / NAS100 / GER40 / JP225 CFDs | account + margin metadata validated |

Do **not** assume availability — verify via instrument list API before research commit.

---

## 7. Phase 3 — FX cross expansion

After cost screening on H4 bid/ask:

```text
EUR_JPY, GBP_JPY, AUD_JPY, CAD_JPY, CHF_JPY
EUR_GBP, AUD_NZD, EUR_AUD, GBP_AUD, EUR_CHF
```

Purpose: express themes without every trade being implicit USD direction.

---

## 8. Explicit avoid list (for now)

```text
crypto
single-stock CFDs
exotic FX pairs
low-liquidity commodities
options
news scalping
triangular arbitrage
martingale / grid / averaging down
```

Rationale: volatility, data complexity, spread dominance, or architectural mismatch with H4/OANDA research bot.

---

## 9. Implementation sprint sequence (recommended)

| sprint | scope |
|---|---|
| `infra-observed-cost-and-spread-regime-diagnostics-001` | cost atlas only (subset of this doc §3) |
| `infra-cross-asset-feature-ingest-001` | FRED yields + VIX + DXY proxy; no strategy |
| `infra-mtf-confluence-prototype-001` | scorer on H4 + synthetic D1; see MTF design |
| `infra-financing-accrual-001` | engine/net PnL honesty for carry |

This design sprint does **not** authorize those sprints — it ranks them for human selection.

---

## 10. Success criteria (feature layer)

- Cross-asset features available at backtest bar time with documented alignment (no lookahead).
- Cost atlas identifies hostile windows for all seven research pairs.
- Confluence can consume `cross_asset_state` + `cost_state` without executor changes.
- No strategy approved as side effect of building features.
