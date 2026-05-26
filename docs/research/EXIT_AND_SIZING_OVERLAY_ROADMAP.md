# Exit and Sizing Overlay Roadmap

**Date:** 2026-05-26  
**Branch:** `research-pro-alpha-confluence-and-asset-expansion-roadmap-001`  
**Status:** Design only — exits and sizing as first-class research; no campaign.

> Post-dedup archetype analysis: **stops dominate** (~50%) and **time exits** (~48%) drive losses. Entries have been over-researched relative to exits.

---

## 1. Evidence basis

From [`POST_DEDUP_ARCHETYPE_ANALYSIS.md`](POST_DEDUP_ARCHETYPE_ANALYSIS.md):

| exit reason | share (C015–C017 aggregate) |
|---|---:|
| stop | 50.4% |
| time | 47.8% |
| eod | 1.8% |

Dominant loss driver: **stops_dominate**. Short side slightly less bad than long in aggregate — exit asymmetry may interact with side/regime.

Existing trade records already capture:

- R-multiple at exit
- spread paid
- exit reason
- fill timing, ambiguous exit flags, gap-fill flags

Instrumentation for exit research is **mostly present** — see [`INFRA_EXIT_FIDELITY_001_SUMMARY.md`](INFRA_EXIT_FIDELITY_001_SUMMARY.md).

---

## 2. Exit overlay catalog

Test each exit as a **first-class strategy component**, not an afterthought on fixed entry rules.

| exit concept | helps | implementation sketch |
|---|---|---|
| **ATR trailing stop / Chandelier** | trend trades | ratchet stop by `highest_close - k×ATR` (long) |
| **Counter-signal exit** | trend + MR | close when setup invalid (e.g. ADX crosses above MR gate) |
| **Regime invalidation exit** | all | HTF flips hostile — tie to confluence W1/D1 states |
| **Cost-hostile exit block** | all | no add/tighten during hostile spread windows |
| **Partial TP + runner** | impulse trends | fixed partial at 1R; trail remainder — test expectancy impact |
| **Time stop by setup type** | MR / session | N bars by setup class, not one global max_bars |
| **Divergence de-risk** | open trend | tighten stop or partial on bearish/bullish divergence vs position |

### 2.1 Regime invalidation (links to confluence)

```text
IF in long AND d1_state flips to trend_down AND NOT explicit_counter_trend_mr:
  exit at next bar open (or tighten to breakeven first — test both)
```

### 2.2 Counter-signal exit (MR example)

CAMPAIGN_008/009 mean-reversion: exit when z-score returns to midline **or** ADX rises above range gate — C009 tested midline target; regime flip exit is under-tested.

### 2.3 Cost-hostile behavior

From cost atlas ([`CROSS_ASSET_FEATURE_ROADMAP.md`](CROSS_ASSET_FEATURE_ROADMAP.md) §3):

- **Block new entries** in hostile windows (risk layer).
- **Optional:** force flat before known hostile window if holding overnight through rollover — research only with financing model.

---

## 3. C008 mean-reversion post-mortem lane (rank #6)

**Do not retune CAMPAIGN_008.** Study **when** it worked.

| fact | source |
|---|---|
| Train exp_r negative — gate fail | CAMPAIGN_008 report |
| Validation exp_r **+0.172 R**, PF 1.29, 6/6 pairs positive | CAMPAIGN_008 report |
| Range regime gate (ADX) central to design | [`CAMPAIGN_008_RANGE_MEAN_REVERSION_PRECOMMIT.md`](CAMPAIGN_008_RANGE_MEAN_REVERSION_PRECOMMIT.md) |
| Dedup integrity | EVIDENCE INTEGRITY UNKNOWN — rerun before trusting magnitudes |

### 3.1 Research questions (descriptive sprint)

1. Which **folds / pairs** drove validation positivity?
2. Did wins cluster in **low ADX / high efficiency-ratio chop** sub-regimes?
3. Stop vs time exit mix on winning vs losing MR trades?
4. Would **confluence grade A** (D1/H4 range + no HTF trend) subset validation trades?
5. Does validation edge **vanish under 2× cost** or financing overlay?

### 3.2 Deliverable shape (future)

`docs/research/CAMPAIGN_008_CONDITIONAL_POSTMORTEM.md` — conditional analysis only; no new parameters.

### 3.3 Divergence overlay for MR

Allowed: bullish divergence + HTF range → +1 confluence grade for long MR candidate. Forbidden: divergence-only entry.

---

## 4. Daily / weekly multi-asset momentum lane (rank #5)

External anchor: [AQR Time Series Momentum](https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum) — 12-month excess return predictability across diverse futures/forwards.

**Bot implication:** a **weekly cross-sectional or time-series momentum lane** on multiple assets may have stronger priors than H4 indicator churn.

CAMPAIGN_016 tested weekly cross-sectional momentum on FX only — **REJECT**, WITHIN_NULL. Future lane should:

- use **multi-asset** universe (FX + indices + commodities per data availability),
- require **financing-aware** net returns,
- apply **confluence/cost gates**,
- pre-register beat-null ≥ 0.05 R vs deduped null.

Not authorized by this design sprint.

---

## 5. Sizing overlay (rank #9 — deferred)

### 5.1 Why not now

Kelly sizing maximizes long-run geometric growth but **amplifies model error** when P(win) and payoffs are miscalibrated ([Kelly criterion](https://en.wikipedia.org/wiki/Kelly_criterion)).

We do not yet have calibrated out-of-sample:

```text
P(win | setup, regime, asset, timeframe, cost state)
average win R / average loss R
tail loss / gap risk
correlation with open positions
sample size and confidence intervals
```

Confluence grade **must not** proxy for Kelly inputs until measured.

### 5.2 Interim policy (when confluence ships)

| setup grade | risk multiplier | notes |
|---|---:|---|
| base | 0.10%–0.25% per trade | existing `risk_per_trade_pct` band |
| A | max **1.25×** base | capped by `max_risk_per_trade_pct` |
| B | **1.00×** base | default |
| C | **0.50×** diagnostic or no trade | config flag |
| reject | **0** | block |

**Forbidden:**

- Full Kelly allocation.
- Doubling risk because setup “looks good.”
- Grade-based sizing before confluence lift validated on held-out data.

Portfolio heat cap (`max_correlated_positions`, drawdown limits) **unchanged**.

### 5.3 Future fractional-Kelly gate

Enable only when:

1. Calibrated probability model passes walk-forward calibration tests.
2. Fractional Kelly (e.g. ¼ Kelly) with hard cap at `max_risk_per_trade_pct`.
3. Human pre-registration for sizing overlay campaign separate from entry signal campaign.

---

## 6. Exit research protocol

Mirror walk-forward discipline from [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md):

| step | action |
|---|---|
| 1 | Fix entry rule set (existing rejected or null anchor) |
| 2 | Pre-register exit variant(s) |
| 3 | Run walk-forward with **one exit change at a time** |
| 4 | Compare vs same-entry baseline on exp_r, PF, drawdown, exit mix |
| 5 | 2× cost stress on promising variants |

Anti-pattern: optimize exit parameters on C015–C017 rejects to force APPROVE.

---

## 7. Recommended implementation order

| order | item | module touch |
|---:|---|---|
| 1 | Time stop by setup type | strategy `exit_model` + backtest engine |
| 2 | ATR trailing stop variant | strategy + engine stop update path |
| 3 | Regime invalidation exit | confluence HTF states → strategy exit hook |
| 4 | Counter-signal exit | strategy-specific |
| 5 | Partial TP + runner | engine partial fill support (if missing) |
| 6 | Grade-based sizing multiplier | risk engine only |
| 7 | Fractional Kelly | risk engine — **blocked** until calibration sprint |

Executor: submit/cancel only — exit logic lives in strategy + engine simulation.

---

## 8. Non-goals

- Retuning CAMPAIGN_008 parameters.
- Kelly sizing from confluence grades without probability calibration.
- Using exit optimization to resurrect C015–C017 without new hypothesis.

---

## 9. Success criteria (future exit sprint)

- At least one exit variant shows **≥ 0.05 R** lift vs fixed-stop baseline on **held-out folds** with stable exit-reason mix improvement (fewer stop-dominated losses without collapsing winners).
- Lift survives 2× cost on seven-pair universe.
- Still no strategy approval without full gate protocol and human memo.
