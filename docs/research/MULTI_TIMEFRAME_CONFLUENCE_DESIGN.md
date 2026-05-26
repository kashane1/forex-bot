# Multi-Timeframe Confluence Design

**Date:** 2026-05-26  
**Branch:** `research-pro-alpha-confluence-and-asset-expansion-roadmap-001`  
**Status:** Design only — no implementation, no strategy approval.

> **Architectural rule:** Confluence is produced in the strategy/research layer and consumed by the risk engine. The executor must not implement confluence logic.

---

## 1. Problem statement

Current campaigns ask essentially: “Did H4 trigger?” A professional FX bot must ask whether higher timeframes agree, whether cross-asset context supports the thesis, whether costs allow the trade, and whether lower-timeframe structure confirms or rejects the entry.

Post-dedup evidence: isolated H4 pattern entries (C015–C017) fail at or below the deduped null. Confluence is not a guarantee of edge, but **unconditional H4 entries without regime alignment** is the failure mode we have been repeating.

---

## 2. Proposed artifact: `ConfluenceScore`

Emitted alongside (or embedded in) each `Signal` via `Signal.features` until a typed domain model is added.

### 2.1 Timeframe states

| field | values | source TF |
|---|---|---|
| `w1_state` | `trend_up` · `trend_down` · `range` · `unknown` | W1 |
| `d1_state` | `trend_up` · `trend_down` · `range` · `unknown` | D1 |
| `h4_setup` | `breakout` · `pullback` · `mean_reversion` · `no_setup` | H4 |
| `h1_trigger` | `confirmation` · `rejection` · `no_trigger` | H1 or M15 |

**State detection (v0 — deterministic, no ML):**

- **Trend up:** close > N-period EMA and EMA slope positive; optional ADX > threshold.
- **Trend down:** symmetric.
- **Range:** ADX below threshold AND efficiency ratio below threshold (consistent with CAMPAIGN_005 choppy-regime finding).
- **Unknown:** insufficient warmup bars or missing data.

Infrastructure note: true D1/W1 from OANDA daily candles hit rollover contamination (CAMPAIGN_006). **Preferred v0 path:** aggregate W1/D1 from validated H4 bid/ask with documented rules, or fix D1 fill/spread path before relying on broker D1 candles.

### 2.2 Cross-asset and cost sub-scores

| field | values |
|---|---|
| `cross_asset_state` | structured dict — see [`CROSS_ASSET_FEATURE_ROADMAP.md`](CROSS_ASSET_FEATURE_ROADMAP.md) |
| `cost_state` | `acceptable` · `marginal` · `hostile` |
| `divergence_flag` | `none` · `bullish` · `bearish` · `conflicting` |

### 2.3 Final grade

| grade | meaning | risk-engine default |
|---|---|---|
| **A** | All aligned; cost acceptable; no LTF rejection | allow up to 1.25× base risk (cap unchanged) |
| **B** | Minor conflict or marginal cost; thesis still valid | 1.00× base risk |
| **C** | Material conflict or diagnostic-only | 0.50× or reject per config |
| **reject** | Hostile regime, cost, or explicit counter-signal | block new entry |

Grades are **research outputs first**. Risk consumption requires a follow-up sprint with config gates and backtest attribution.

---

## 3. Example: long EUR_USD

Before emitting a long signal, confluence evaluates:

```text
Is D1 aligned (trend_up or range supporting reversion thesis)?
Is W1 hostile (strong trend_down against long)?
Is DXY confirming USD weakness (or at least not strengthening)?
Is VIX / risk regime supportive of EUR risk-on?
Is spread/ATR acceptable right now?
Is there H1 rejection against the long?
Is expected R after spread still worth taking?
```

Example scored output:

```json
{
  "w1_state": "range",
  "d1_state": "trend_up",
  "h4_setup": "pullback",
  "h1_trigger": "confirmation",
  "cross_asset_state": {
    "usd_trend": "weak",
    "risk_regime": "risk_on",
    "rates_bias": "neutral"
  },
  "cost_state": "acceptable",
  "divergence_flag": "none",
  "grade": "A",
  "grade_reasons": ["d1_aligned", "dxy_weak", "spread_ok"]
}
```

---

## 4. Integration points (no executor changes)

```text
StrategyContext
  └─ candles (H4 primary + optional H1/M15)
  └─ cross_asset_features (future: from data layer cache)
  └─ cost_state (from spread atlas or live SpreadSnapshot)

strategy.generate_signal(ctx)
  └─ raw entry logic
  └─ confluence_engine.score(ctx, candidate_side, setup_type)
  └─ Signal(..., features={"confluence": {...}})

RiskEngine.evaluate(inputs)
  └─ read signal.features["confluence"]["grade"]
  └─ apply grade → sizing multiplier
  └─ reject if grade == "reject" or cost_state == "hostile"
  └─ existing spread/session/exposure gates unchanged
```

[`src/forex_bot/domain/signals.py`](../../src/forex_bot/domain/signals.py) already provides `features: dict[str, Any]` — sufficient for research prototypes.

Recommended follow-up: frozen Pydantic `ConfluenceScore` in `domain/` with schema version for ledger persistence.

---

## 5. Divergence — allowed and forbidden uses

### 5.1 Definitions

```text
bullish_divergence  = price lower low + oscillator higher low
bearish_divergence  = price higher high + oscillator lower high
```

Oscillator v0: RSI-14 and/or MACD histogram — pick one for research consistency.

### 5.2 Allowed

| use | condition |
|---|---|
| Boost MR trade quality +1 grade | D1/H4 in `range`; divergence supports reversion direction |
| Tighten trailing stop | Divergence against open trend trade |
| Block new trend entries | Divergence against intended direction on H4/H1 |

### 5.3 Forbidden

- Enter **solely** because divergence exists.
- Use divergence without HTF range/overextension context for MR.
- Treat divergence as early reversal proof in strong trends (can persist for extended moves).

Reference: [Investopedia — Divergence](https://www.investopedia.com/terms/d/divergence.asp).

---

## 6. Research validation protocol

Confluence must be tested as **conditional probability lift**, not win-rate alone.

For each historical signal (or null-entry proxy):

| metric | all signals | grade A only | grade B only |
|---|---|---|---|
| win rate | | | |
| expectancy (R) | | | |
| profit factor | | | |
| max drawdown | | | |
| trade count | | | |

**Success criteria (design sprint — to be pre-registered before any campaign):**

- Grade A subset beats all-signals expectancy by ≥ **0.05 R** with minimum **N** trades per fold.
- Grade A does not collapse trade count below research-minimum thresholds.
- Lift survives **2× cost** stress (per C015–C017 sensitivity pattern).

**Failure mode to reject:** confluence raises win rate but destroys payoff or reduces sample to noise.

---

## 7. Implementation phases (future sprints)

| phase | scope | dependency |
|---|---|---|
| **MTF-0** | H4-only regime tags (trend/range) on existing data | none |
| **MTF-1** | Synthetic D1/W1 from H4 aggregation + tests | D1 infrastructure decision |
| **MTF-2** | H1/M15 trigger confirmation on stored candles | data hydration |
| **MTF-3** | Cross-asset inputs wired into scorer | [`CROSS_ASSET_FEATURE_ROADMAP.md`](CROSS_ASSET_FEATURE_ROADMAP.md) Phase 1 |
| **MTF-4** | Risk-engine grade gates + backtest attribution | MTF-0–3 |

---

## 8. Non-goals

- ML-based confluence classifiers in v0.
- Confluence inside `Executor` or broker adapter.
- Automatic strategy approval from confluence lift alone (still requires pre-registered campaign vs deduped null).

---

## 9. Open questions

1. **D1 source:** synthetic from H4 vs fixed engine D1 path — blocks W1/D1 accuracy.
2. **Trigger TF:** H1 vs M15 — OANDA granularity availability and storage cost.
3. **Grade calibration:** fixed rule table vs walk-forward tuned weights — weights must not be fit on C015–C017 rejects.
4. **Counter-trend MR:** explicit grade path when W1 hostile but D1/H4 range + MR setup (C008 lane).
