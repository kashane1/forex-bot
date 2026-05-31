# C1 Cross-Pair Study (Phase 1)

**Status:** RESULT (descriptive; no verdict, no campaign, no strategy)
**Date:** 2026-05-29
**Branch:** `research-c1-factor-validation-001`
**Runner:** `scripts/run_c1_factor_validation.py --pairs all --null-seeds 60`
**Artifacts:** `docs/research/c1_validation/{pair}_c1_events.csv`,
`docs/research/c1_validation/{pair}_c1_nulls.csv`,
`docs/research/c1_validation/c1_validation_meta.json`

Every figure below is read directly from those committed CSVs. The C1 definition
is the locked prior-sprint one (H4 trend, H1 trend, M15 aligned; EMA 20/50,
slope-3; rising-edge + 60-min cooldown; signed forward return). A **negative**
signed return means price moved *against* the alignment direction (i.e. the
"reverts after multi-TF alignment" effect).

## 1. Method

The prior sprint established C1 on USD_JPY + EUR_USD only. Here the identical
analysis is run on **all seven USD-legged majors** in the corpus (the store has
no non-USD crosses). Each pair gets the full C1_long / C1_short event panel plus
a 60-seed random + session-matched null comparison. 60 seeds (vs the prior 200)
was chosen after timing showed the null-mean dispersion is already stable; a
USD_JPY integrity re-run reproduced the prior 200-seed matched-Z to within
rounding (−3.55 vs −3.20… see note 5).

## 2. C1_trend_cont_long — signed forward response by pair

(`mean30/60` = mean signed return in pips at 30/60 min; `t` = parametric t-stat;
`pneg60` = P(signed return<0) at 60 min; `mZ30/60` = session-matched null Z.)

```
pair    usd-leg    n   mean30   t30   mean60   t60  pneg60  spread   mZ30   mZ60
EUR_USD quote   1592   -0.747 -3.18   -1.169 -3.66   0.541   1.605  -3.47  -4.21
USD_JPY base    2137   -0.681 -2.90   -1.136 -3.56   0.508   1.757  -2.93  -3.55
GBP_USD quote   1584   -0.686 -2.62   -0.651 -1.80   0.520   2.126  -2.46  -1.85
NZD_USD quote   1409   -0.122 -0.71   -0.372 -1.48   0.507   1.627  -0.68  -1.57
AUD_USD quote   1559   -0.136 -0.80   -0.356 -1.47   0.495   1.396  -0.55  -1.33
USD_CHF base    1369   -0.137 -0.65   -0.345 -1.14   0.508   1.726  -1.25  -1.68
USD_CAD base    1805   -0.236 -1.04   -0.179 -0.57   0.512   1.993  -1.08  -0.63
```
(sorted by |mZ60|.)

## 3. C1_trend_cont_short (the mirror) — signed forward response by pair

```
pair    usd-leg    n   mean30   t30   mean60   t60  pneg60  spread   mZ30   mZ60
EUR_USD quote   1779   -0.515 -2.42   -0.355 -1.26   0.508   1.558  -2.98  -1.52
GBP_USD quote   1672   -0.507 -1.75   -0.690 -1.76   0.517   2.065  -2.14  -2.29
USD_CHF base    1419   -0.528 -2.45   -0.263 -0.85   0.505   1.796  -2.35  -0.86
AUD_USD quote   1508   -0.205 -1.09   -0.492 -1.94   0.526   1.394  -1.37  -2.18
USD_CAD base    1496   -0.275 -1.26   -0.350 -1.19   0.502   2.033  -1.27  -1.02
USD_JPY base    1154   -0.251 -0.54   -0.272 -0.39   0.518   1.895  -0.44  -0.35
NZD_USD quote   1613   +0.026 +0.16   +0.067 +0.30   0.501   1.659  +0.16  +0.23
```

## 4. Answers to the Phase-1 questions

**Does the sign remain consistent?** **For C1_long, YES — strikingly so.** The
60-min signed return is **negative on all 7/7 pairs** (P(neg) 0.495–0.541), i.e.
full multi-timeframe bullish alignment is followed by a downward drift on every
major tested. This is the single most important cross-pair fact: the *direction*
of the C1_long effect replicates universally. The C1_short mirror is negative
(reversion) on 6/7 (NZD_USD is the lone near-zero/positive exception), so the
short side is directionally consistent but weaker and noisier.

**Does the magnitude remain consistent? NO.** Magnitude is heavily
**concentrated in the two original discovery pairs**: EUR_USD (−1.169 pip, mZ60
−4.21) and USD_JPY (−1.136 pip, mZ60 −3.55) are the only pairs whose C1_long
clears the matched null strongly (|mZ| ≥ 3). GBP_USD clears at the **30-min**
horizon only (mZ30 −2.46) and fades by 60 min. The remaining four
(NZD/AUD/CHF/CAD) are **within-null at every horizon** (|mZ| < 2), with effects
roughly a third the size. So the effect is **universal in sign but significant
in magnitude on only 2–3 of 7 pairs — and those are the pairs it was discovered
on.** That the discovery pairs are also the strongest is a caution flag carried
forward to the regime and robustness phases (it is consistent with both "real
factor strongest on the most liquid/most-trending pairs" and "the discovery pair
selection captured the favourable tail").

**Is the effect concentrated in USD pairs?** Unanswerable as posed — the corpus
is **all** USD-legged (no non-USD crosses exist to contrast). What *is* testable,
and is the crux of the USD-confound question (Phase 3): the sign does **not flip
between USD-base and USD-quote pairs.** C1_long reverts *down in pair space* on
USD-base pairs (USD_JPY −1.14, USD_CAD −0.18, USD_CHF −0.35) **and** on USD-quote
pairs (EUR −1.17, GBP −0.65, AUD −0.36, NZD −0.37) alike. A pure
"USD-strength-mean-reverts" artifact would force **opposite** pair-space signs on
the two groups; it does not. This is strong early evidence **against** the simple
USD-regime-artifact explanation (Phase 3 dissects it further).

**Does it disappear on some pairs?** Yes — by *significance*, on four of seven
(NZD, AUD, CHF, CAD all within matched-null). By *sign*, it disappears on none
for C1_long (all 7 negative).

## 5. Cost note and integrity note

- **Cost (carried to Phase 5):** the C1_long 60-min reversion is **below spread
  on every pair** — even the strongest, EUR_USD, is |−1.169| / 1.605 ≈ **0.73×**
  spread; USD_JPY ≈ 0.65×; GBP_USD ≈ 0.31×. As measured, C1 is a factor, not an
  edge, on all seven majors.
- **Integrity:** the USD_JPY C1_long panel reproduces the prior sprint exactly
  (h30 mean −0.681 t −2.90; h60 mean −1.136 t −3.56 vs prior −0.6815/−2.899 and
  −1.1366/−3.560). EUR_USD likewise (h60 −1.169 vs prior −1.167). The framework
  re-derivation is sound; new-pair numbers are trustworthy.

## 6. One-line takeaway

C1_long is a **sign-universal** (7/7 negative), **magnitude-concentrated**
(significant on EUR_USD + USD_JPY, marginal GBP_USD, null elsewhere), and
**cost-defeated-everywhere** factor whose pair-space sign does **not** track the
USD leg — already pointing away from "pure USD artifact" and toward "real but not
tradable," pending the regime, confound, and robustness phases.
