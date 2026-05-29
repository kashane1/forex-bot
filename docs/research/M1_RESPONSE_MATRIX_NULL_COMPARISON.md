# M1/HTF Confluence — Null Comparison

**Status:** RESULT (descriptive; no verdict, no campaign, no strategy)
**Date:** 2026-05-29
**Branch:** `research-m1-htf-confluence-sampling-matrix-001`
**Runner:** `scripts/run_m1_response_matrix.py --pair {PAIR} --null-states ... --null-seeds 200`
**Artifacts:** `docs/research/usd_jpy_m1_response_matrix_nulls.csv`,
`docs/research/eur_usd_m1_response_matrix_nulls.csv`

Every figure below is read directly from those two committed CSVs (states tested:
`C1_trend_cont_long`, `A1_trend_cont_long`, `A3_breakout_long`, `A3_breakout_short` —
the cross-pair candidate plus a trend-continuation control and the breakout pair).

## 1. Question and method

Phases 3–4 surfaced several |t| ≥ 2.5 cells; most flip sign between pairs (a USD-regime
drift confound), with one — `C1_trend_cont_long` — replicating in sign and magnitude.
The t-stat assumes events are an unstructured draw. This phase asks: **does the observed
signed forward return exceed what random event-timing produces, holding event count
(and, for the matched null, session mix and direction) fixed?** Over 200 seeds, every
horizon:

- **Random-timestamp null** — `n` random M1 timestamps, same fixed direction →
  `rand_z = (observed − mean_null) / std_null`.
- **Session-matched null** — one random M1 bar per event *in the same session*, same
  direction → `matched_z` (the stricter control; fixing direction partly absorbs the
  pair's overall drift).

## 2. Matched-Z by horizon (5/10/15/30/60 min), with observed 60-min return (pips)

**USD_JPY**
```
state                  mZ5    mZ10   mZ15   mZ30   mZ60  | obs_ret60
C1_trend_cont_long    -1.47  -0.69  -1.25  -2.96  -3.20  |  -1.137
A1_trend_cont_long    -0.45  -1.48  -1.25  -1.25  -0.39  |  +0.070
A3_breakout_long      +0.19  -0.84  -0.34  +0.28  +0.92  |  +0.403
A3_breakout_short     -2.32  -0.71  -0.09  +0.12  +1.31  |  +0.175
```

**EUR_USD**
```
state                  mZ5    mZ10   mZ15   mZ30   mZ60  | obs_ret60
C1_trend_cont_long    -3.22  -3.53  -3.81  -3.56  -4.09  |  -1.167
A1_trend_cont_long    -1.18  -0.66  -1.66  -2.74  -2.82  |  -0.438
A3_breakout_long      -1.55  -1.61  -2.59  -2.94  -2.33  |  -0.375
A3_breakout_short     -1.76  -2.96  -1.42  -1.94  -2.82  |  -0.363
```

`rand_z` tracks `matched_z` closely (e.g. USD_JPY `C1_long` rand_z
−1.39/−0.70/−1.28/−2.76/−3.30 vs matched −1.47/−0.69/−1.25/−2.96/−3.20; EUR_USD `C1_long`
rand_z −3.69 → −4.28), so any effect present is **intrinsic to the state, not its session
timing.**

## 3. Does the observed effect exceed random variation?

Bar: |matched-Z| ≥ 2, **same sign on both pairs** (replication is the real test against
the 18×5×2 surface).

| State | USD_JPY | EUR_USD | Same-sign |Z|≥2 on both? |
|---|---|---|---|
| **`C1_trend_cont_long`** | clears at **30/60 min** (−2.96, −3.20) | clears at **all** horizons (−3.2…−4.1) | **YES** (at 30 & 60 min) |
| `A1_trend_cont_long` | within null (|Z| ≤ 1.48) | clears at 30/60 min (−2.74, −2.82) | No — USD_JPY within null |
| `A3_breakout_long` | within null (positive, ≤ +0.9) | clears negative (−2.6, −2.9) | No — **sign flips** |
| `A3_breakout_short` | clears at 5 min only (−2.32) | clears at 10/60 min | No — inconsistent horizons |

**Conclusions:**

1. **One state beats the matched null with the same sign on both pairs:
   `C1_trend_cont_long`** — when H4, H1 and M15 are all bullish-aligned, M1 reverts
   *down*. Survival is **strong and full-horizon on EUR_USD** (matched-Z −3.2 to **−4.09**)
   and **horizon-limited on USD_JPY** (clears only at 30 min −2.96 and 60 min −3.20;
   within-null at 5–15 min). At the **30- and 60-minute** horizons *both* pairs clear
   |Z| ≥ 2 with the same negative sign and near-identical magnitude (obs −1.137 / −1.167
   pips). A specific state at ≤ −3σ on two independent pairs, same sign, is far outside
   best-of-N selection noise — the first directional confluence state on this corpus to
   beat a matched null cross-pair (C029/H16/H03 were null-internal).

2. **It is intrinsic, not timing** (`matched_z ≈ rand_z` everywhere).

3. **The trend-continuation and breakout cells do not replicate cross-pair.**
   `A1_trend_cont_long` is within-null on USD_JPY and only clears on EUR_USD (drift);
   `A3_breakout` **flips sign** between pairs (USD_JPY + / EUR_USD −) — a textbook
   USD-regime drift confound; `A3_breakout_short` clears at inconsistent single horizons.

4. **Not null-tested in this pass:** `A2_pullback_long` (USD_JPY parametric t +2.9, but
   EUR_USD within noise — see Phase 3/4) and the `C1_trend_cont_short` mirror (EUR_USD
   parametric t −3.33, USD_JPY weak). Their summary t-stats suggest the same pattern as
   the null-tested states (continuation = USD-only; the `C1` reversion mirror = EUR-only),
   but no null claim is made for them here.

## 4. Cost note (carried to the decision)

`C1_long`'s 60-min reversion is ~1.1–1.2 pips against spreads of ~1.76 (USD_JPY) and
~1.61 (EUR_USD) — **cost-defeated on both pairs** (~0.65× and ~0.72×). So `C1_long` is a
genuine, cross-pair, null-surviving **factor** that is **not** an edge as measured. Per
this sprint's factor-vs-edge framing, that is exactly what earns *one* future front-gate
screen (whose job is to test cost-capture and non-USD generalization), and nothing more.
