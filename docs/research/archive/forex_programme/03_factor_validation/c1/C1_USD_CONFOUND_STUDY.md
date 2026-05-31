# C1 USD-Confound Study (Phase 3)

**Status:** RESULT (descriptive; no verdict, no campaign, no strategy)
**Date:** 2026-05-29
**Branch:** `research-c1-factor-validation-001`
**Artifacts:** `docs/research/c1_validation/{pair}_c1_events.csv`.

**The question:** is `C1_trend_cont_long`'s reversion just *USD strength
mean-reverting* dressed up as multi-timeframe alignment? The corpus has only
USD-legged majors (no non-USD crosses), but USD sits on the **base** of three
pairs (USD_JPY, USD_CAD, USD_CHF) and the **quote** of four (EUR_USD, GBP_USD,
AUD_USD, NZD_USD). That split, plus the long/short mirror and cross-pair
synchrony, lets us interrogate the confound four ways. All figures from the
committed panels; C1_long at 60 min unless noted; **negative = reversion against
the alignment**.

## 1. Base-currency vs quote-currency effects (pair-space)

```
USD-leg group     n      mean60   t60    pneg
quote (EUR/GBP/AUD/NZD)  6120   -0.646  -4.29  0.516
base  (JPY/CAD/CHF)      5294   -0.607  -3.29  0.510
```

The C1_long reversion is **the same sign and nearly the same magnitude** whether
USD is the base or the quote currency (−0.65 vs −0.61 pip; both significant).
**It does not matter which side of the pair USD is on.** This is the first and
strongest discriminator: a genuine *USD-directional* effect (e.g. "USD keeps
strengthening") would push base-USD and quote-USD pairs in **opposite pair-space
directions** and therefore show **opposite signs** here. It does not. (The prior
sprint's `A3_breakout` cell *did* flip sign between EUR_USD and USD_JPY, proving
this corpus genuinely can express USD-directional sign-flips — C1 simply isn't
one of them.)

## 2. Pair inversion behaviour (USD-space translation)

Re-expressing the universal pair-space reversion in terms of USD:

| Group | C1_long means (pair) | USD state at the event | Reversion (pair down) ⇒ USD |
|---|---|---|---|
| quote-USD | pair extended **up** | USD extended **weak** | USD **strengthens** back |
| base-USD | pair extended **up** | USD extended **strong** | USD **weakens** back |

So under inversion the two groups move USD in **opposite directions** — but in
**both** cases *the extended USD move reverts toward its mean*. C1 is therefore a
**mean-reversion** signature, **not** a directional USD bet. A USD-strength
*trend* confound (USD persistently rising through 2021–2024) would instead make
base-USD C1_long **continue** (USD keeps rising) while only quote-USD C1_long
reverts — an asymmetry we explicitly do **not** see (§1, §3).

## 3. Directional asymmetry — does the short mirror also revert?

If C1 is symmetric overshoot-reversion (a pair-structure property), *both* full
bullish alignment **and** full bearish alignment should fade (negative signed
return for long and short). If it were a USD-regime drift, long and short would be
asymmetric.

```
pair      C1_long 60 (t)      C1_short 60 (t)
EUR_USD   -1.169 (-3.66)      -0.355 (-1.26)
GBP_USD   -0.651 (-1.80)      -0.690 (-1.76)
AUD_USD   -0.356 (-1.47)      -0.492 (-1.94)
NZD_USD   -0.372 (-1.48)      +0.067 (+0.30)
USD_JPY   -1.136 (-3.56)      -0.272 (-0.39)
USD_CAD   -0.179 (-0.57)      -0.350 (-1.19)
USD_CHF   -0.345 (-1.14)      -0.263 (-0.85)
```

The short mirror is **negative (reversion) on 6 of 7 pairs** (NZD_USD the lone
near-zero exception). Pooled, C1_short is −0.368 (t −2.47) on quote-USD pairs and
−0.298 (t −1.19) on base-USD pairs. **Both alignment directions fade** — the
hallmark of symmetric mean-reversion of an overshoot, not a one-directional
regime trend. (The long side is the stronger of the two, consistent with the
prior sprint, but the short side does not contradict it.)

## 4. Is it one common USD factor? — cross-pair synchrony

If a single USD factor drove the reversion, C1_long monthly-mean returns would be
**highly correlated** across same-leg pairs and **anti-correlated** across the
base/quote divide (a USD reversion month helps one group, hurts the other).
Pearson correlation of monthly-mean C1_long 60-min returns:

```
avg corr WITHIN quote-USD pairs : 0.21
avg corr WITHIN base-USD pairs  : 0.30
avg corr ACROSS quote vs base   : -0.08
```

The within-group correlation is **modest** (0.2–0.3 — expected, since same-group
pairs literally share the USD leg) and the across-group correlation is
**essentially zero** (−0.08), not the strong negative a dominant USD reversion
factor would force. So the C1 reversion is **mostly pair-idiosyncratic**, with
only a **modest shared-USD overlay** — not a synchronized common-USD event.

## 5. Verdict on the confound

**C1 is *not* primarily a USD-regime artifact.** Four independent reads agree:
(1) equal magnitude and **no sign-flip** across the base/quote split; (2) under
inversion both groups show the *extended move reverting* (mean-reversion, not a
USD direction); (3) the **short mirror also reverts** on 6/7 pairs (symmetric
overshoot, not directional drift); (4) **low cross-pair synchrony** (idiosyncratic,
not one USD factor). Each is the opposite of what a USD-strength confound would
produce, and the contrast with the sign-flipping `A3_breakout` cell shows the
test has teeth.

**Honest residual caveat.** Every pair in the corpus shares the USD leg, so the
seven "replications" are **not independent** — roughly half of each pair's
variance is USD, and a modest shared-USD overlay is visible (§4). This study can
show USD is **not the dominant directional driver**; it **cannot** fully exclude a
USD *contribution*. Only genuinely non-USD crosses (EUR_GBP, AUD_JPY, …), which
**do not exist in this corpus**, could close that last gap. That irreducible
limitation — not a failure of C1 — is why the cross-pair evidence, though
favourable, is weaker than seven independent pairs would be.

**Net:** of the four candidate explanations, **#2 (USD-regime artifact) is
substantially ruled out**; the evidence favours **#1 (a genuine multi-TF-extension
mean-reversion factor)**, with a residual, non-excludable shared-USD component.
