# M1/HTF Confluence — State Shortlist

**Status:** SHORTLIST (descriptive; not a strategy, not a campaign, not approval)
**Date:** 2026-05-29
**Branch:** `research-m1-htf-confluence-sampling-matrix-001`

Five states from the discovery (Phases 3–4) and null (Phase 5) passes. **Characterization
of factors, not trade signals.** Parametric t-stats / mean_ret come from the summary CSVs;
matched-Z comes from the null CSVs (which cover `C1_trend_cont_long`, `A1_trend_cont_long`,
`A3_breakout_long`, `A3_breakout_short`). Where a state was not in the null run it is
labelled **parametric-only**.

## Shortlist (max 5)

### 1. `C1_trend_cont_long` — H4 trend-up **and** H1 trend-up **and** M15 above EMA50, context long
- **Sample count:** USD_JPY 2,143 · EUR_USD 1,592 (smallest pool — triple confluence).
- **Directional bias:** **Negative** — price *reverts down* after full multi-TF bullish
  alignment. mean_ret grows with horizon: USD_JPY −0.153 → −1.137 pips (5→60 min);
  EUR_USD −0.281 → −1.167. Largest-magnitude effect in the study, **same sign and
  magnitude on both pairs.**
- **Null comparison:** **The only state clearing the matched null with the same sign on
  both pairs.** EUR_USD: |Z| ≥ 2 at *all* horizons (−3.22 → −4.09). USD_JPY: clears at
  30 min (−2.96) and 60 min (−3.20), within-null at 5–15 min. `matched_z ≈ rand_z`.
- **Spread sensitivity:** 60-min reversion ~1.1–1.2 pips vs spreads ~1.76 / ~1.61 →
  **cost-defeated on both** (~0.65× / ~0.72×).
- **Implementation complexity:** Medium (three-TF lookahead-safe alignment; the *fade*
  direction is opposite the naive "trend-continuation" read).

### 2. `A2_pullback_long` — M15 trend-up + M5 pullback (below EMA20), context long *(parametric-only)*
- **Sample count:** USD_JPY 6,790 · EUR_USD 6,116.
- **Directional bias:** **Positive** continuation (buy-the-dip): USD_JPY t up to +2.91,
  +0.537 pips @60 min. EUR_USD within noise (t ≤ +0.24, turns negative).
- **Null comparison:** Not in the null run. Its strong USD_JPY-only / weak-EUR_USD
  parametric profile mirrors the null-tested cells (continuation = USD-only). No null
  claim made.
- **Spread sensitivity:** Cost-defeated (≤0.54 pip vs 1.76).
- **Implementation complexity:** Low.

### 3. `C1_trend_cont_short` — H4 + H1 trend-down + M15 below EMA50, context short *(parametric-only)*
- **Sample count:** USD_JPY 1,155 · EUR_USD 1,781.
- **Directional bias:** Bearish mirror of #1 — multi-TF bearish alignment reverts *up*.
  EUR_USD t −2.47 → −3.33 (strong); USD_JPY weak (t ≤ −0.55).
- **Null comparison:** Not in the null run; EUR_USD parametric strength suggests an
  EUR-leaning mirror of #1, but no null claim is made. Fold into the same future screen.
- **Spread sensitivity:** Cost-defeated.
- **Implementation complexity:** Medium (mirror of #1).

### 4. `A3_breakout_long` — M15 trend-up + M5 breakout, context long
- **Sample count:** USD_JPY 6,389 · EUR_USD 5,670.
- **Directional bias:** **Sign flips across pairs** — USD_JPY +0.403 pips @60 min
  (continuation), EUR_USD −0.375 (reversion). Classic drift confound.
- **Null comparison:** USD_JPY within-null (matched-Z ≤ +0.9); EUR_USD clears negative
  (−2.6 → −2.9). Opposite signs ⇒ **not** a consistent factor.
- **Spread sensitivity:** Cost-defeated.
- **Implementation complexity:** Low.

### 5. `A1_trend_cont_long` — M15 trend-up + M5 above EMA50, context long
- **Sample count:** USD_JPY 6,669 · EUR_USD 6,255.
- **Directional bias:** Weak; USD_JPY near-flat (+0.07 pip @60 min), EUR_USD negative
  (−0.438) — drift, not a clean conditional effect.
- **Null comparison:** **Within-null on USD_JPY** (|Z| ≤ 1.48); clears only on EUR_USD
  (−2.74 / −2.82 @30/60). Does not replicate ⇒ trend-continuation is not the driver.
- **Spread sensitivity:** Cost-defeated.
- **Implementation complexity:** Low.

## Bottom line

**One state survives the cross-pair matched-null bar (same sign): `C1_trend_cont_long`**
— fading full multi-timeframe bullish alignment produces a short-horizon downward
reversion that beats a matched null on *both* pairs at the 30- and 60-minute horizons
(all horizons on EUR_USD; 30–60 min on USD_JPY), and is cost-defeated on both (~0.7×).
Trend-continuation (`A1`) does not replicate; breakout (`A3`) flips sign (drift); the
USD-only continuation (`A2`) and EUR-only `C1` short mirror are parametric-only. The
single defensible candidate is **the multi-TF-alignment fade (`C1_long`)**.
