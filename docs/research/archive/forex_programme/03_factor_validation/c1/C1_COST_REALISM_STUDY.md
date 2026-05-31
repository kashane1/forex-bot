# C1 Cost-Realism Study (Phase 5)

**Status:** RESULT (descriptive; no verdict, no campaign, no strategy)
**Date:** 2026-05-29
**Branch:** `research-c1-factor-validation-001`
**Artifacts:** `docs/research/c1_validation/{pair}_c1_events.csv`.

**The question:** the factor is real (Phases 1–4); *could it ever realistically
become tradable?* All figures from the committed panels; C1_long, 60-min,
negative = reversion. `spread` is the mean ask−bid (pips) at the event bar; the
forward return is measured **mid-to-mid**. A crude "net" = |effect| − spread
charges one full spread for a round trip and **nothing else** — it is therefore
an *optimistic upper bound* on what a real trade could keep (no entry/exit
slippage, no exit-rule cost, assumes the mean is capturable).

## 1. Unconditional cost picture (all 7 pairs)

```
pair       mean60   spread   |eff|/spread   net(=|eff|-spread)
EUR_USD    -1.169    1.605       0.73           -0.44
USD_JPY    -1.136    1.757       0.65           -0.62
GBP_USD    -0.651    2.126       0.31           -1.48
NZD_USD    -0.372    1.627       0.23           -1.26
AUD_USD    -0.356    1.396       0.26           -1.04
USD_CHF    -0.345    1.726       0.20           -1.38
USD_CAD    -0.179    1.993       0.09           -1.81
```

**Unconditionally, C1_long is cost-defeated on every pair** — even the strongest,
EUR_USD, returns only 0.73× its spread, and that is *before* any slippage or
exit-rule cost. As a flat, take-every-event factor, C1 is **not tradable**. This
confirms and extends the prior sprint's two-pair finding to all seven majors.

## 2. Session-adjusted view (the favourable combination)

Spreads are tightest in London/NY and the reversion is also strongest there
(Phase 2). The most favourable session × volatility cells on the two strong pairs
(within-pair top-tertile volatility = "hi-vol"):

```
pair    session   vol   n    mean60   median   t      spread   net(|mean|-sp)
EUR_USD london    hi   147   -4.31    -2.00   -3.41   1.56     +2.75
EUR_USD ny        lo   416   -1.30    --      --      1.52     -0.22
USD_JPY tokyo     hi   250   -2.63    -2.25   -2.80   1.79     +0.84
USD_JPY ny        hi   263   -2.13    +0.80   -1.55   1.69     +0.45  (outlier-driven)
USD_JPY offhours  hi    41   -3.64    --      --      3.36     +0.28  (tiny n, wide spread)
```

So **there exist sub-regimes where the spread-adjusted reversion is positive** —
concentrated in **high-volatility** windows on the two strong pairs.

## 3. Are those cells real or outlier-driven?

A positive *mean* can be an artifact of a few large reversions when per-event
variance is enormous (the 10th/90th-percentile 60-min return in these hi-vol cells
spans roughly ±20 pips). Checking median, t-stat, and a 5%-trimmed mean:

```
cell                       n    mean    median   t      pneg   5%-trim mean
EUR_USD london  hi-vol    147  -4.31   -2.00   -3.41   0.57    -3.24   REAL
USD_JPY tokyo   hi-vol    250  -2.63   -2.25   -2.80   0.56    -2.09   REAL
USD_JPY ny      hi-vol    263  -2.13   +0.80   -1.55   0.48    -0.40   MIRAGE (tail)
```

Two of the three survive: **EUR_USD London high-vol** (median −2.0, t −3.4,
trimmed −3.2) and **USD_JPY Tokyo high-vol** (median −2.25, t −2.8, trimmed −2.1)
are genuine, non-tail-driven reversions whose **median** alone exceeds the spread.
The USD_JPY NY cell that looked best on raw mean is an **outlier mirage** (median
positive, insignificant) — a direct reminder of how easily post-hoc cell-scanning
manufactures false "tradable" pockets.

## 4. Realistic-execution caveats (why §2–§3 is a hypothesis, not a result)

1. **Post-hoc selection / forking paths.** These cells were found by scanning
   pair × session × volatility × extension. The favourable ones are a hand-picked
   minority; one already proved to be an outlier mirage. Their significance is
   *not* corrected for the search and would need a fresh, pre-registered,
   **out-of-sample** test to mean anything.
2. **Optimistic cost.** "net = |mean| − spread" assumes mid-to-mid capture with
   one spread charged. A real C1 fade enters *against* a strong multi-TF trend
   (adverse selection on the fill) and must be exited; realistic round-trip cost
   is materially higher than one quoted spread, and high-vol spreads spike and gap
   beyond their mean.
3. **No exit rule exists (and none may be built here).** The 60-min mean is not
   capturable without an exit policy; with ±20-pip per-event dispersion, the
   realised result depends entirely on sizing/stops/targets that are out of scope
   and would themselves need validation.
4. **Concentrated on the discovery pairs.** The cost-aware cells live on EUR_USD
   and USD_JPY — the pairs C1 was discovered on — not on the five new majors.

## 5. Answer: could C1 ever realistically become tradable?

**Not as a flat factor** (cost-defeated on all 7 pairs unconditionally). **But a
specific, economically sensible cost-aware path is not dead:** the reversion is
volatility-scaled (Phase 2), and in **high-volatility windows on EUR_USD/USD_JPY**
the spread-adjusted reversion is positive and survives an outlier check. That is a
*plausible hypothesis of tradeability*, not a demonstration — its apparent edge is
post-hoc, optimistically costed, and exit-rule-free.

This is precisely the situation a single **pre-registered front-gate screen** is
designed to adjudicate: take the high-volatility-conditioned C1 fade on
EUR_USD/USD_JPY, charge realistic round-trip cost, and test it **out-of-sample**
against a matched, post-cost null — with a pre-committed lane-closure stop if it
fails. The verdict (Phase 6) weighs whether that path is strong enough to earn
that one screen.
