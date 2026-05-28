# USD_JPY Macro-Regime Context — Tradeability Diagnostic Result

**Sprint:** `usdjpy-macro-regime-context-tradeability-001` · **Phase 2**
**Tooling:** `scripts/build_usdjpy_macro_regime_context_dataset.py` +
`scripts/analyze_usdjpy_macro_regime_context.py`
**Outputs:** `research/usdjpy_macro_regime_context/{context_manifest.json,analysis_summary.json}`

> DIAGNOSTIC ONLY — slow tradeability **context**, not edge, not a strategy, not fast-news
> trading. Macro is a no-trade-filter / conditioner, never an entry. Lower spread/ATR,
> whipsaw, and false-breakout = more tradeable. Train+validation only; TEST sealed.

---

## Setup

- 95,756 M15 bars (train 59,852 / val 35,904).
- Slow context joined **as-of with a 1-day publication lag** (lookahead-safe): US 2y/10y
  level/trend regimes + 2s10s, VIX/SP500 risk regime, broad-USD trend, composite risk-off.
- Public-schedule event windows: **49 NFP** (computed, exact) + **33 FOMC** (best-effort);
  CPI/BOJ deferred. Pre-event 24h / post-event 48h windows + stabilization buckets.
- Baseline tradeability: spread 1.7 pip median; spread/ATR 0.20 (train) / 0.17 (val);
  whipsaw 0.50/0.50; false-breakout 0.495/0.488.

---

## Findings (honest, mostly null for actionable conditioning)

### 1. Raw spread cost is FLAT across all macro context
Median spread is **1.6–1.7 pips in every** macro/rates/risk/event cell — pre-event,
post-event, NFP, FOMC, risk-on/off, high/low VIX, every rate regime. **Slow macro context
does not change the raw cost of trading USD/JPY.** Therefore it provides **no
macro-based cost / no-trade filter** beyond the session/rollover filter already found by
the atlas (rollover 5–10 pip). This is the single most important result.

### 2. spread/ATR moves only mechanically with volatility, not cost
- **Pre-event** (24h before NFP/FOMC): ATR slightly *lower* (8.8 train) → spread/ATR
  slightly *higher* (0.214) = mildly more cost-hostile per unit vol.
- **Post-event** (48h after): ATR *higher* (12.7 train / 15.1 val) → spread/ATR *lower*
  (0.16 / 0.13). This is the well-known "scheduled releases raise realized vol afterward"
  effect — purely mechanical (denominator), **direction-blind**, and already implied by
  the session/time-of-day atlas. It is not a tradeability *edge*.

### 3. Whipsaw / chop is UNCONDITIONED by slow macro regime
Whipsaw rate is **0.49–0.51 in every context cell** (event windows, risk regimes, rate
regimes). Slow macro context does **not** identify choppier vs cleaner periods. Flat null
— consistent with the atlas-level direction null.

### 4. False-breakout conditioning is weak and inconsistent
Pre-event false-breakout is higher in train (0.539) but ~baseline in validation (0.499) —
**not consistent**. Post-event is slightly lower (≈0.46) on both splits but small. No
reliable breakout-survival conditioning.

### 5. Rate-differential regime is NON-IDENTIFIABLE here (confounded with the period)
The slow US-rate regime moved near-monotonically over 2021–2025, so the regime label is
**collinear with the train/validation split**: `us_2y_regime=high` is 52,324 train vs
only 1,927 val; `=low` is 897 train vs 19,773 val. Any "rate-regime effect" cannot be
separated from the period/split effect with this data. (And the JP leg of the
differential is absent.) **Rate-regime conditioning is not testable here** — a verified
JP rate series + a longer multi-cycle history would be future infrastructure.

### 6. Risk regime (VIX / risk-off) shows only the vol-mechanical effect
High VIX / risk-off cells have higher ATR (lower spread/ATR) but the **same raw spread,
the same ~0.50 whipsaw, and ~baseline false-breakout**. Risk regime does not condition
direction or chop; only vol level, which is mechanical and already in the atlas.

---

## Interpretation

Slow macro/rates/calendar context, joined lookahead-safe, **does not provide a robust,
identifiable tradeability-conditioning or no-trade signal for USD/JPY beyond mechanical
volatility effects that the session/time-of-day atlas already captures.** Specifically:

- raw spread cost is invariant to macro context → no macro cost filter;
- whipsaw/chop and false-breakout are essentially unconditioned by macro regime;
- the only real effect (pre/post-event vol level) is mechanical, direction-blind, small,
  and time-of-day-redundant;
- rate-differential regime is confounded with the train/val period and not identifiable.

The **highest-value intended output — a macro-based no-trade filter — is not supported**:
the existing session/rollover spread filter dominates, and macro adds nothing to it on
cost or chop.

## What is NOT claimed

No edge, no entry signal, no fast-news reaction. The post-event vol-elevation effect is
NOT presented as tradeable; it is a mechanical descriptor. Nothing here changes a verdict.

Proceed to Phase 3 (robustness + latency-independence) and Phase 4 (readiness), which —
on this evidence — point to `NOT_READY` / `PAUSE_STRATEGY_RESEARCH`.
