# Do-Not-Repeat List

**Sprint:** `research-nonusd-cross-factor-discovery-planning-001` · Phase 3
**Type:** anti-pattern fence. Docs-only. No factor, no screen, no campaign.
**Date:** 2026-05-30.

This phase applies the hard-won lessons of the programme so the cross lane does
not re-run failures in a cross costume. It names: (1) **closed lanes that must
not be re-tuned**, (2) **factor families from Phase 2 likely to repeat a prior
failure**, (3) **hidden re-tunes** (ideas that *look* new but are an old reject
re-parameterized), (4) **search-space traps**, and (5) **low-value directions**.

The governing rule from every prior closeout: **reopen only with new data or a
new external thesis, never a re-tune — and a fresh screen, never a re-fit.**

---

## 1. Closed lanes — DO NOT re-tune (carried verbatim from prior closeouts)

These are REJECTED or RETIRED and stay closed. A cross is **new data only for
breadth/replication**, not a licence to re-run a closed single-instrument lane.

| Lane | Verdict | Why it stays closed on crosses |
|------|---------|-------------------------------|
| C020–C023 pullback / MTF pullback | RETIRED (no entry edge) | single-instrument directional; wider cross spread = strictly worse |
| C025/C026 Donchian + TF ladder (M3–M30) | REJECT (cost gradient, no floor) | same family, wider spread |
| C027 H4 z-score reversion | REJECT_TRAIN_GATE (last front-gate survivor) | single-pair mean-reversion; cost wall higher on crosses |
| C028 relative-value spread | LIKELY_SELECTION_NOISE | RV *concept* reopens (F15–F18) ONLY with economically-motivated cross spreads + half-life-matched hold; the **collinear best-of-N** version stays closed |
| C029 10-pip range bars (USD_JPY) | REJECT (net −0.019R) | non-time-bar directional; retired lane |
| C031 vol-managed TSMOM | WITHIN_NULL + financing-defeated | slow signal, ~5y still underpowers; financing ≈4× spread |
| H16 overshoot-exhaustion fade | FAIL_FRONT_GATE | non-time-bar microstructure; retired |
| H03 thin-move fade | FAIL_FRONT_GATE | non-time-bar microstructure; retired |
| C1 high-vol directional (M1/HTF) | FAIL_FRONT_GATE (net-negative 3/3) | **C1 *replication* on crosses is sanctioned; C1 *re-tune* for a friendlier vol/threshold is NOT** |
| C016 cross-sectional momentum (USD majors) | REJECT (USD bet) | the *currency* cross-section reopens (F08); the **USD-collinear weekly** version stays closed |

**Single most important fence:** F24 (C1 replication) is a *fresh, pre-registered
screen of the locked C1 definition* to answer the residual-USD question. The
moment anyone adjusts a C1 threshold, vol cut, horizon, or pair filter to improve
a cross result, it becomes a **C1 re-tune** and is forbidden.

---

## 2. Phase-2 families likely to repeat a prior failure

Scored against the dominant failure modes (cost-defeated, financing-defeated,
within-null, selection-noise, data-blocked).

### 2a. HIGH repeat-risk — fence hard or drop

- **F05, F06, F16 (triangular residual / triangle-RV).** Three-leg structures
  multiply the round-trip spread by ~3× the *widest* legs. The programme died on
  a *one-leg* spread wall; three legs is the cost wall cubed. True triangular
  arbitrage is additionally latency-defeated for a retail M1 backtest. **Repeats
  the cost-defeated failure with near-certainty.** Keep F05/F07 only as *filters*
  (no independent leg cost), drop F06/F16 as standalone tradables.
- **F10 (short-horizon cross-sectional reversal).** Short horizon = high turnover
  = the spread wall, on instruments that are *wider* than the majors C016 already
  failed on. **Repeats cost-defeated.**
- **F12 (classic carry) as currently testable.** Honest screening needs **real
  swap rates that are not ingested**; the registry figures are estimates. Running
  it now repeats C031's financing-defeated failure *and* would be evidence built
  on estimated costs — a data-integrity trap. **Data-blocked until financing
  ingest.**

### 2b. MEDIUM repeat-risk — admissible only with explicit guards

- **F08, F09, F11 (cross-sectional momentum / carry-tilt / momentum-of-crosses).**
  Reopened by breadth, but C016's ghost is real: weekly rebalance + wide cross
  spreads can still be cost-defeated, and best-of-(lookback,k,horizon) is a
  forking path. Guard: **pre-register one lookback/horizon/k, cost-first, on the
  genuine currency cross-section (not instrument best-of-N).**
- **F15, F17, F18 (shared-leg / safe-haven / half-life-matched RV).** Reopen the
  RV concept C028 closed; admissible *only* with (i) an economic cointegration
  rationale stated before fitting, (ii) half-life ≤ intended hold, (iii) two-leg
  measured cross cost in the gate. Without all three this is C028 again.
- **F04, F10 reversion variants.** Mean-reversion on wider-spread instruments
  inherits the C008/C027 cost wall; only the *cross-currency* (basket) framing,
  not single-pair, is admissible.

### 2c. LOW repeat-risk — genuinely new territory

- **F01–F03 (currency-strength / dispersion / strongest-vs-weakest).** No prior
  analogue; the USD-collinearity that killed C016/C031 is *exactly* what these
  remove. Still cost-gated, but structurally novel.
- **F19–F21 (lead-lag / confirmation filters).** Filters that *cannot create
  edge alone* but also carry no extra leg cost when used to gate a host signal —
  low repeat-risk *as filters* (high if mistaken for generators).
- **F22, F23 (vol-dispersion / correlation-regime gates).** Regime conditioners,
  not generators; low standalone risk, valuable as overlays.
- **F24 (C1 replication).** The sanctioned reuse; low risk *if* kept frozen.

---

## 3. Hidden re-tunes (look new, are old)

The most dangerous category — these *feel* like cross-enabled novelty but are a
closed reject re-parameterized:

1. **"C1 but on EUR_GBP with a wider vol filter."** = C1 re-tune. Forbidden.
   (Only the frozen-definition replication is allowed.)
2. **"C028 RV but pick the best of the 8×7 cross spreads."** = C028
   selection-noise with more candidates. The added breadth *increases* best-of-N
   inflation; it does not fix it.
3. **"C016 weekly momentum but include crosses in the ranking universe."**
   Mixing crosses into a USD-anchored rank still double-counts the USD leg
   (EUR_USD and EUR_JPY both load on EUR) unless a proper currency decomposition
   is used. Naively adding crosses to C016 = C016 with leakage.
4. **"C029/H16/H03 range/overshoot but on GBP_JPY."** = retired non-time-bar lane
   on a *wider, fatter-tailed* instrument. Strictly worse; the retirement stands.
5. **"C031 TSMOM but on the 8 crosses."** Same ~5y window underpowers the slow
   signal identically; crosses add breadth not history, and financing is still
   un-ingested. = C031 with the same limiters.

**Rule:** if a "new" cross idea maps onto a closed lane after stripping the
instrument name, it is a hidden re-tune and is rejected here.

---

## 4. Search-space traps

- **Best-of-N inflation.** 15 instruments, 8 currencies, 9+ triangles, dozens of
  spread pairs → the candidate count explodes. Any family that searches over
  (instrument × lookback × threshold × horizon) and reports the best is
  manufacturing selection noise. **Mitigation:** pre-register one specification;
  multiple-comparison correction is mandatory in the gate.
- **Collinearity masquerading as breadth.** EUR_USD, EUR_JPY, EUR_GBP, EUR_AUD,
  EUR_CHF all load on EUR. Treating them as independent names overstates breadth
  and re-creates the USD-bet pathology with EUR. **Mitigation:** decompose to
  currencies (F01) before claiming cross-sectional independence.
- **Regime-dependent independence.** In risk-off, JPY/CHF crosses co-move and
  "breadth" collapses exactly when it matters (named in the feasibility study).
  A backtest over a calm sub-window overstates diversification. **Mitigation:**
  F23 correlation-regime conditioning and explicit risk-off stress slices.
- **Three-leg cost denial.** Triangular/triangle-RV families that quietly assume
  one-leg cost. **Mitigation:** cost model must charge every leg's measured
  spread.
- **Estimated-financing evidence.** Reporting carry results on registry *estimate*
  rates as if measured. **Mitigation:** carry families are data-blocked until real
  swap ingest; label estimates as estimates.
- **Structural-break leakage.** EUR_CHF's 2015 SNB break is outside the window,
  but any longer-horizon extension reintroduces it. **Mitigation:** keep the
  populated window; flag on any history extension.

---

## 5. Low-value directions (deprioritize even if testable)

- **Single-instrument directional/mean-reversion on any cross** (Categories A/B)
  — strictly worse than the majors that already failed; no breadth benefit.
- **Macro/event/calendar on crosses** (Category L) — breadth doesn't fix the
  missing real-rate leg or the ~5y history; still data-blocked.
- **Non-time-bar microstructure on crosses** (Category C) — retired lane, wider
  cost wall; reopen only via a *new thesis*, and even then a cheaper instrument
  (EUR_GBP) than the JPY crosses H16/H03 implicitly favored.
- **Pure triangular arbitrage capture** — latency/cost-defeated for retail M1;
  only the *consistency/lead-lag research* angle (as a filter) has any value.

---

## Bottom line

Of the 24 Phase-2 families: **drop/fence-as-filter** the three-leg triangular
tradables (F06, F16) and short-horizon reversal (F10); **data-block** classic
carry (F12–F14) until financing ingest; **admit-with-guards** the cross-sectional
(F08/F09/F11) and RV (F15/F17/F18) families; and carry forward as **low-risk
novelty** the currency-strength group (F01–F03), the filter/lead-lag group
(F19–F21), the regime overlays (F22/F23), and the sanctioned C1 replication
(F24). Phase 4 scores the survivors; Phase 5 shortlists ≤5.
