# USD_JPY Macro-Regime Context — Robustness & Latency-Independence

**Sprint:** `usdjpy-macro-regime-context-tradeability-001` · **Phase 3**
**Source:** `research/usdjpy_macro_regime_context/{context_manifest,analysis_summary}.json`.

> DIAGNOSTIC ONLY. These checks falsify; they do not endorse. TEST sealed throughout.

---

### 1. Lookahead audit
Slow features attach via a backward `merge_asof` with a publication lag: a decision bar at
`t` only sees daily values with `date + lag ≤ t`. This is unit-tested
(`test_macro_regime_context.py::test_asof_join_uses_only_lagged_past_values`). Event
windows use **public schedule dates only** (known in advance); the event *outcome* is never
read. **No lookahead.** ✅

### 2. Latency-independence (required by the framing)
Re-ran the full join + analysis with the publication lag increased **1 day → 7 days**:

| cell | metric | lag 1d | lag 7d |
|---|---|---|---|
| evt_post=True | spread/ATR (train/val) | 0.159 / 0.126 | **0.159 / 0.126** |
| evt_pre=True | spread/ATR (train/val) | 0.214 / 0.159 | **0.214 / 0.159** |
| risk_off=True | spread/ATR (train/val) | 0.200 / 0.147 | 0.199 / 0.148 |

Event-window effects are **identical** under a 7-day delay (they are calendar-driven), and
the rates/risk regime is barely moved by a week's lag. The slow context is genuinely
**latency-independent** — it does not rely on reacting quickly. ✅ (This also re-confirms
the effects are slow/mechanical, not a fast signal.)

### 3. Whipsaw / chop conditioning
Whipsaw rate is **0.49–0.51 in every context cell, both splits** — event windows, risk
regimes, rate regimes alike. Slow macro context does **not** identify choppy vs clean
periods. **Null.** ❌ (no conditioning)

### 4. Raw spread (cost) conditioning
Median spread is **1.6–1.7 pips in every macro cell, both splits.** Macro context does not
change the cost of trading. **No macro cost filter.** ❌

### 5. spread/ATR effect = vol-mechanical only
The only consistent spread/ATR deviations (post-event lower, pre-event higher) are driven
entirely by the **ATR denominator** (events raise realized vol), not by spread. The effect
is direction-blind and redundant with the session/time-of-day atlas. Real but not
actionable as a tradeability edge.

### 6. Rate-differential regime — non-identifiable (period confound)
The slow US-rate regime moved near-monotonically over 2021–2025, making the regime label
**collinear with the train/validation split**: `us_2y_regime=high` = 52,324 train / 1,927
val; `=low` = 897 train / 19,773 val. A regime effect cannot be separated from the
period/split effect, and the JP leg of the differential is absent. **Not identifiable
here.** ❌ A verified JP rate series + a multi-cycle history would be required future infra.

### 7. Risk regime (VIX / risk-off)
High-VIX / risk-off cells differ only in ATR (vol); raw spread, whipsaw (~0.50), and
false-breakout (~baseline) are unchanged. Risk regime conditions only vol level — mechanical,
already in the atlas. ❌ (no incremental conditioning)

### 8. False-breakout conditioning
Pre-event false-breakout higher in train (0.539) but ≈baseline in validation (0.499) —
**inconsistent across splits**. Post-event slightly lower (~0.46) but small. ❌

### 9. Sample sizes
Adequate overall (event windows 5,900–8,987 bars; risk/rate cells thousands–tens of
thousands). The binding problem is **not** sample size but the period confound (#6) and the
absence of any whipsaw/cost conditioning (#3, #4).

### 10. No-trade-filter value (the highest-value intended output)
**Not supported.** The existing session/rollover spread filter (atlas: rollover 5–10 pip)
dominates; macro context adds nothing on raw spread or chop. The only macro-specific
candidate — stand aside / size down in the pre-event low-vol window — rests on a small,
mechanical vol effect with **unchanged spread**, and the symmetric post-event window is
actually *higher* vol. There is no robust macro-derived no-trade rule beyond what the
session atlas already provides.

### 11. TEST untouched
The dataset builder hard-refuses `--end` past `2025-07-01`; no 2025-07+ data was read. ✅

---

## Summary

| check | result |
|---|---|
| lookahead audit | clean ✅ |
| latency-independence | confirmed (identical at 7-day lag) ✅ |
| whipsaw conditioning | null ❌ |
| raw-spread conditioning | null (flat 1.6–1.7p) ❌ |
| spread/ATR effect | vol-mechanical only, direction-blind |
| rate-regime | non-identifiable (period confound) ❌ |
| risk-regime | vol-only, no incremental conditioning ❌ |
| false-breakout conditioning | inconsistent ❌ |
| sample size | adequate (not the binding issue) |
| no-trade-filter value | not supported beyond session/rollover ❌ |
| TEST untouched | clean ✅ |

The diagnostic is **lookahead-safe and latency-independent** (it meets those framing
requirements), but it finds **no robust, identifiable, actionable tradeability
conditioning** from slow macro/rates/calendar context beyond mechanical volatility effects
already captured by the session atlas. Proceed to the readiness decision.
