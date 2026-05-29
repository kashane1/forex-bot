# M1/HTF Confluence Response Matrix — Decision

**Status:** DECISION
**Date:** 2026-05-29
**Branch:** `research-m1-htf-confluence-sampling-matrix-001`
**Freeze state:** intact — this decision creates **no** campaign, **no** strategy,
**no** approval, and enables **no** paper/demo/live. It recommends (does not start) at
most one future front-gate screen. Figures are read from the committed CSV artifacts.

## Verdict

# `FRONT_GATE_CANDIDATE_EXISTS`

One higher-timeframe confluence state produces an M1 forward response that is
**statistically meaningful, repeatable, cross-pair (same sign), and null-surviving** —
though **cost-defeated as measured**:

> **`C1_trend_cont_long` — when H4 trend, H1 trend, and M15 are all bullish-aligned, M1
> price tends to REVERT DOWN over the next 30–60 minutes.** It clears the session-matched
> null (|Z| ≥ 2) at the 30- and 60-minute horizons on **both** pairs with the same
> negative sign (USD_JPY −2.96 / −3.20; EUR_USD −3.56 / −4.09), strongly and at *all*
> horizons on EUR_USD, with near-identical observed magnitude (−1.137 / −1.167 pips at
> 60 min).

This is **mean-reversion after multi-timeframe extension** — the opposite of the naive
"stacked-trend → continuation" read. The effect is intrinsic to the state
(`matched_z ≈ rand_z`) and survives the multiple-comparison surface via cross-pair
replication (a specific state at ≤ −3σ on two independent pairs, same sign, is far
outside best-of-N noise). It is the first directional confluence factor on this corpus to
beat a matched null cross-pair; C029/H16/H03 were all null-internal.

## What the sprint answered

- **Any repeatable directional bias after a confluence state?** Yes —
  `C1_trend_cont_long` (fade full multi-TF bullish alignment).
- **Does it exceed random variation?** Yes — beats the matched null at 30–60 min on both
  pairs (EUR_USD at all horizons to −4.1σ; USD_JPY at 30/60 min to −3.2σ, within-null at
  5–15 min). The only state clearing cross-pair, same-sign.
- **Is it an edge?** **No, as measured.** The 60-min reversion (~1.1–1.2 pips) is below
  spread on **both** pairs (~1.76 USD_JPY ~0.65×; ~1.61 EUR_USD ~0.72×). A real *factor*,
  not an *edge*.
- **Did confluence depth matter?** Yes, unusually — the *triple*-TF state (`C1`)
  replicates, while single-structure trend-continuation (`A1`) is within-null on USD_JPY.
- **Were the other strong cells real?** Not cross-pair: `A3_breakout` **flips sign**
  between pairs (drift); `A1_trend_cont_long` clears only on EUR_USD; the USD-only
  `A2_pullback_long` continuation and EUR-only `C1` short mirror were not null-tested.

## Why a candidate (and not `NO_EDGE_FOUND`)

A front-gate candidate must, at minimum, **beat a matched null**, and ideally replicate.
`C1_trend_cont_long` does both — same negative sign on two pairs, ≤ −3σ, at the 30–60 min
horizons — the bar C029/H16/H03 all failed (they were null-internal). In this sprint's
explicit **factor-vs-edge** framing, a cross-pair null-surviving *factor* that is
cost-defeated is exactly what earns *one* front-gate screen (whose job is to test whether
it can be captured), not an outright stop. It earns that one screen — no more.

**Honest caveats (for the screen to resolve, not assumed away):**
- **Cost.** Below spread on both pairs as measured; the screen must show a net-of-cost
  path exists or it dies on cost like its predecessors.
- **Mechanism may differ by pair.** On USD_JPY (a 2021–2026 up-mover) `C1_long` reads as
  over-extension fade; on EUR_USD (broadly down) as bear-rally resumption. The shared
  *observable* is real, but whether it is one universal effect or a coincidence of the
  USD regime can only be settled on **non-USD crosses**.
- **Horizon-limited on USD_JPY** (clears null only at 30–60 min, not 5–15 min).

## Recommended next step — exactly ONE future front-gate screen

**Screen name (proposed):** `C1 multi-timeframe-alignment mean-reversion front-gate screen`

Pre-register (frozen precommit) and test **only**:

1. **Cross-pair, non-USD generalization.** Run the `C1_long` fade (and `C1_short` mirror)
   on USD_JPY + EUR_USD **plus ≥2 non-USD crosses** (e.g. EUR_GBP, AUD_JPY) to separate a
   genuine multi-TF-extension effect from a USD-regime drift artifact. Survival on
   non-USD crosses is the make-or-break.
2. **Matched-null-post-cost.** Charge realistic round-trip cost (spread at the event bar
   + slippage) and re-test against the matched null with the lab's `cost_feasibility` +
   `matched_nulls` machinery. The bar is "beats matched null **after** cost." As measured,
   `C1_long` is below spread on both pairs, so this is the likeliest failure point.
3. **Extension monotonicity.** Vary how stretched the alignment must be (distance above
   EMA50 in ATR) to check the reversion grows with extension rather than being a
   single-threshold artifact.

**Stop criterion (pre-committed):** if `C1` does not beat the matched-null-**post-cost**
bar on ≥2 of the (USD + non-USD) pairs, the M1/HTF time-bar confluence directional lane
is closed on this corpus (joining the retired non-time-bar lane); reopen only with new
data or a new external thesis, via a fresh screen, never a re-tune.

A `PASS` of that future screen would authorize only a *separate, later* scaffold sprint —
it would not, by itself, create a campaign or approve anything.

## Hard-rule confirmation

No campaign created. No strategy built. No train/validation/test run. No entry/exit
rules. No parameters optimized (states locked a priori in Phase 1). No strategy approved.
Paper/demo/live remain blocked. No OANDA APIs, no credentials used. No trading
recommendation issued — only a recommendation for one future *research* screen.
