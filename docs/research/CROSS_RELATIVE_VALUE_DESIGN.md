# Cross Relative-Value — Construction Design (Phase 2)

**Sprint:** `research-cross-relative-value-factor-validation-001` · Phase 2
**Status:** construction (factor candidates only — **no trades, no signals, no
entry/exit, no PnL**). Code: `research/edge_discovery/cross_relative_value.py`;
runner `scripts/run_cross_relative_value_factor.py`. Reuses the C028 lab utilities
(`rolling_z`, `ar1_half_life`) — no refit of C028.
**Date:** 2026-05-30.

This phase **constructs the relative-value relationships and their descriptive
diagnostics** (residual scale, half-life, autocorrelation, no-arb band). It does
not decide anything (Phase 3+ measure response; Phase 7 the verdict).

---

## 1. Relationship definitions tested (as built)

**Primary — 8 triangular no-arbitrage consistency residuals** (one per cross):
`resid_c(t) = ln(observed cross)(t) − implied(t)`, implied = the two USD legs
(`docs/research/CROSS_RELATIVE_VALUE_PROTOCOL.md` §2). All 8 pre-named, zero spread
search. Built on the common aligned M5 grid (304,014 bars, 25,331 events,
2021-05-27 → 2026-05-26).

**Secondary (Phase-6 robustness only) — shared-leg cointegration spreads:**
`EUR_JPY~GBP_JPY`, `EUR_JPY~AUD_JPY`, `GBP_JPY~AUD_JPY`, `AUD_JPY~NZD_JPY`
(hedge-ratio β by OLS of `ln(p1)` on `ln(p2)`).

## 2. Relationship diagnostics (from `construction_meta.json`)

```
cross     resid_std_bp  half_life_bars  ar1_phi  autocorr1  no_arb_band_bp
EUR_GBP       0.23          0.6          0.332     0.332        4.97
EUR_JPY       0.61          9.6          0.930     0.930        4.25
GBP_JPY       0.53          7.2          0.909     0.909        4.87
AUD_JPY       0.59          4.8          0.866     0.866        5.66
NZD_JPY       0.81          6.8          0.904     0.904        7.18
EUR_CHF       0.28          0.8          0.398     0.398        5.40
GBP_CHF       0.31          0.8          0.401     0.401        5.90
EUR_AUD       0.26          0.8          0.400     0.400        5.47
```
(`no_arb_band_bp` = summed mean relative spread of the cross + its two legs — the
descriptive transaction-cost band of the triangle.)

## 3. Two structurally different relationship groups (key construction fact)

The 8 residuals split cleanly into two families by their mean-reversion diagnostic:

- **JPY-cross complex (EUR_JPY, GBP_JPY, AUD_JPY, NZD_JPY):** ar1_phi **0.87–0.93**,
  half-life **4.8–9.6 bars** (24–48 min). These are **genuinely slowly mean-
  reverting** residuals — a real multi-bar relationship, not 1-bar noise.
- **Non-JPY (EUR_GBP, EUR_CHF, GBP_CHF, EUR_AUD):** ar1_phi **0.33–0.40**,
  half-life **≤1 bar** (0.6–0.8). Per protocol §11 this is the **noise/stale-quote
  signature** — the residual reverts essentially within one M5 bar.

## 4. Scale fact (critical, carried to the §11 artifact test)

**Every residual's standard deviation (0.23–0.81 bp) is ~6–25× SMALLER than its
triangle's no-arb spread band (4.25–7.18 bp).** The triangular relationships are
extremely tight — deviations live an order of magnitude **inside** the
transaction-cost band. This is the dominant descriptive fact and it pre-frames the
existence question: even if deviations revert (Phase 3), they revert *within the
cost band*. (Tradability is out of scope; this is recorded descriptively for the
§11 artifact test, not as a cost gate.)

## 5. What was NOT built

No signal, trade rule, entry/exit, position, PnL, cost-feasibility gate, or
approval. Construction + diagnostics only. The C028 module was **reused** (utility
functions), **not refit**.
