# FX Futures Carry — Verdict (Phase 5)

**Sprint:** `research-fx-futures-carry-diagnostic-001` · Phase 5
**Type:** Binary, decision-forcing verdict. One label. No middle option. Makes no tradability claim and authorizes no strategy.
**Date:** 2026-05-31

---

# Verdict: `CARRY_DOES_NOT_SURVIVE_IN_FUTURES`

The frozen cross-sectional carry factor, evaluated on real CME FX-futures continuous price returns, is **statistically zero in the matched 5-year window, negative over 24 years, indistinguishable from (or below) every matched null, JPY-concentrated, and without timing content**. Carry does **not** survive the venue change.

---

## 1. The evidence (numbers from `primary.json` / `deep.json`)

- **PRIMARY (incl-JPY, 2021-05 → 2026-05):** primary 3-month cell mean **+0.000426 (+0.04 %/qtr), NW-HAC t = +0.09** — economically and statistically zero. Sign consistency ~0.5 (0.46 at 12 m).
- **PRIMARY nulls (h3):** randomized-ranks Z **+0.21**, shuffled-timestamp Z **−0.09**, matched-random Z **+0.15** — all far below the frozen **Z ≥ 2** bar; Holm rejects nothing; unconditional baseline ≈ −0.0046.
- **DEEP (ex-JPY, ~24 y, 2001-01 → 2026-04):** 3-month mean **−0.0041, t = −1.65** (negative, |t| < 2); matched Z **negative** against every null (randomized −2.98, shuffled −2.83, matched −3.00 → carry is *below* every null, one-sided p ≈ 0.998); unconditional baseline **positive (+0.0028)** while carry is negative — carry *detracts* over the long sample.
- **Single-name:** drop-JPY moves the PRIMARY h3 mean to **−0.0047** — the near-zero reading is a JPY artifact, not breadth.
- **Persistence:** rank stability ≈ **0.98** — a static tilt, no dynamic/timing content (as in spot).

## 2. Why this is decisive, not marginal

The venue study made a falsifiable prediction: because futures embed the rate differential in the **basis** (converging into price) rather than paying a nightly **accrual**, the **futures total return = price return = the spot-predictive component** — which the spot study had already measured as statistically **zero** (t ≈ 0.1).

The diagnostic confirms this: the PRIMARY futures total (+0.04 %/qtr, t = +0.09) essentially equals the spot study's spot-predictive leg (≈0, t = 0.10), and the 24-year ex-JPY run is, if anything, negative. The one thing futures could have revealed — a predictive residual hidden under the financing wall — **does not exist.** Futures removed the financing *penalty* and the accrual *benefit* together (they are the same rate differential), and what remained was zero.

## 3. Why not `CARRY_SURVIVES_IN_FUTURES`

Survival requires the futures carry return to be positive *and* clear the frozen nulls (matched-Z ≥ 2). In the matched window it is statistically zero and indistinguishable from every null (max |Z| ≈ 0.21); over 24 years it is negative and below every null. There is no horizon, window, or null against which carry shows favourable, significant separation. The binary cannot fall the other way.

## 4. Scope and honesty caveats (do not overclaim)

- This is a **gross price-return** diagnostic on a **vendor-continuous** series (Yahoo `=F`); a bespoke roll was not built (free data can't feed it). At monthly cadence this is second-order, but the result is a *factor-survival* finding, not a backtested PnL.
- Yahoo `=F` absolute levels / deep-history start are **non-deterministic across fetches** (vendor roll re-anchor); the **return-based diagnostic is reproducible from the committed CSVs** (`FX_FUTURES_DATA_VALIDATION.md` §0).
- The DEEP run is **JPY-excluded** (FRED JPY series retired). Both the matched incl-JPY window and the deep ex-JPY window give the same conclusion.
- The finding is about **this carry construction** (interbank-rate HML on FX-futures price). It is consistent with the academic result that FX carry's return is a risk premium realized through the rate differential, not predictable price appreciation.

## 5. Consequence

`CARRY_DOES_NOT_SURVIVE_IN_FUTURES` resolves the programme's final open question — *was carry financing-defeated or genuinely non-predictive?* — in favour of **genuinely non-predictive.** This triggers the **pre-committed fallback from the programme-direction decision: Option E — archive the strategy search.** See Phase 6.

## 6. Hard-rule compliance

No campaign created. No strategy / entry-exit / trading logic / front gate. Nothing approved; `approved: []`. Paper/demo/live remain blocked. Carry definition unchanged; no thresholds retuned; no rejected factor reopened. Evaluated gross; no broker API used.
