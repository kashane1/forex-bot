# Cross Relative-Value Factor — Pre-Registration Protocol

**Sprint:** `research-cross-relative-value-factor-validation-001` · Phase 1
**Status:** **PRE-REGISTERED AND FROZEN as of this commit.** Every element below
is locked *before* any datum is read. No element may change after data review
(hard rule). Any deviation forced during execution is recorded in the result docs,
never silently applied.
**Date:** 2026-05-30.

Factor-existence/robustness only. Tradability, cost, signals, entry/exit are out of
scope and not computed.

---

## 1. Universe (frozen)

15 instruments, M5 materialized mid closes (`m1_materialized`), window 2021-05-27 →
2026-05-26, on the **common aligned M5 grid** (inner-join across all 15 — same grid
as S2, ~304k bars).

- **USD majors (7):** EUR_USD, GBP_USD, USD_JPY, AUD_USD, NZD_USD, USD_CAD, USD_CHF
- **Crosses (8):** EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY, NZD_JPY, EUR_CHF, GBP_CHF,
  EUR_AUD

## 2. Relationship definitions (frozen — PRIMARY: triangular consistency residuals)

Define each currency's USD log-value `u(c) = ln(price of 1 unit c in USD)` from the
majors:
```
u(EUR)=+ln(EUR_USD)  u(GBP)=+ln(GBP_USD)  u(AUD)=+ln(AUD_USD)  u(NZD)=+ln(NZD_USD)
u(JPY)=−ln(USD_JPY)  u(CAD)=−ln(USD_CAD)  u(CHF)=−ln(USD_CHF)  u(USD)=0
```
For each cross `BASE_QUOTE`, the **no-arbitrage implied** log price is
`u(BASE) − u(QUOTE)`, and the **triangular residual** is:
```
resid_c(t) = ln(observed BASE_QUOTE)(t) − [ u(BASE)(t) − u(QUOTE)(t) ]
```
The 8 frozen pre-named relationships (residual = obs − implied):
```
EUR_GBP : ln(EUR_GBP) − [ ln(EUR_USD) − ln(GBP_USD) ]
EUR_JPY : ln(EUR_JPY) − [ ln(EUR_USD) + ln(USD_JPY) ]
GBP_JPY : ln(GBP_JPY) − [ ln(GBP_USD) + ln(USD_JPY) ]
AUD_JPY : ln(AUD_JPY) − [ ln(AUD_USD) + ln(USD_JPY) ]
NZD_JPY : ln(NZD_JPY) − [ ln(NZD_USD) + ln(USD_JPY) ]
EUR_CHF : ln(EUR_CHF) − [ ln(EUR_USD) + ln(USD_CHF) ]
GBP_CHF : ln(GBP_CHF) − [ ln(GBP_USD) + ln(USD_CHF) ]
EUR_AUD : ln(EUR_AUD) − [ ln(EUR_USD) − ln(AUD_USD) ]
```
**8 relationships, one per cross, zero spread search.** Each is pinned by
no-arbitrage and should be small and stationary; the factor question is whether its
**deviations revert**.

**Secondary (Phase-6 robustness only — nearby relationship definition):**
shared-leg cointegration spreads on the JPY-cross complex, pre-named:
`EUR_JPY~GBP_JPY`, `EUR_JPY~AUD_JPY`, `GBP_JPY~AUD_JPY`, `AUD_JPY~NZD_JPY`
(hedge ratio β by OLS of `ln(p1)` on `ln(p2)`; spread = `ln(p1) − β·ln(p2)`).
Reuse `research/edge_discovery/relative_value_spread.py` (`estimate_beta`,
`ar1_half_life`). These are NOT the primary and only test robustness of the
conclusion to relationship choice.

## 3. Normalization method (frozen)

Each residual is standardized to a **rolling z-score** using strictly-prior stats
(look-ahead-safe): `z_t = (resid_t − mean_{t-L..t-1}) / std_{t-L..t-1}`, via the
lab's `rolling_z(resid, L)` (which uses `.shift(1)`). **Primary L = 48 M5 bars
(4h).** No de-trending beyond the rolling mean; no winsorization.

## 4. Deviation thresholds (frozen)

By |z| of the residual at the event bar:
- **stretched:** |z| ≥ 2
- **extreme:** |z| ≥ 3
- **compressed / unusually stable:** |z| ≤ 0.5
- (reference: **mild** 0.5 < |z| < 2)

## 5. Response windows (frozen)

Forward horizons: **5, 15, 30, 60, 240 minutes** = **1, 3, 6, 12, 48 M5 bars**.

**Reversion response.** For an event at t with residual `resid_t` (z = `z_t`):
- **signed reversion** `rev_c(t,h) = −sign(z_t) · (resid_{t+h} − resid_t)`, in the
  residual's natural units (log → **basis points**, 1 bp = 1e-4). **Positive =
  reverts toward zero**; negative = diverges further.
- **fraction closed** `frac_c(t,h) = −(resid_{t+h} − resid_t) · sign(resid_t) /
  |resid_t|` (how much of the deviation is undone; 1.0 = fully closed).
- **directional behavior:** P(reverts) = P(rev > 0).

## 6. Response metrics (frozen)

Per relationship × deviation-bucket × horizon: **mean signed reversion (bp)**,
**P(reverts)**, **mean fraction closed**, plus per-relationship **AR(1) half-life**
(`ar1_half_life`, in M5 bars) and **persistence** (lag-1 autocorrelation of the
residual). Residual **scale** (std, in bp) and the cross's mean **spread** (bp) are
recorded **descriptively** to judge the no-arb-band/microstructure question — NOT as
a tradability gate.

## 7. Conditions studied (frozen)

For each relationship and each evaluated bar, bucket by §4 and measure §5/§6:
1. **stretched** (|z| ≥ 2) → does the residual revert?
2. **extreme** (|z| ≥ 3) → stronger reversion?
3. **compressed** (|z| ≤ 0.5) → behavior when relationship is tight (control).
Direction (revert vs diverge) is an **empirical output**, not assumed.

## 8. Event sampling (frozen)

Evaluate on the full common M5 grid but **decimate events to an hourly grid** (every
12 M5 bars) to limit overlap, consistent with S2. Warm-up = L bars. Pool events
across the 8 relationships for the cross-relationship summaries; keep
per-relationship breakdowns for Phase 4.

## 9. Null methodology (frozen)

Four nulls, **200 seeds** each (fixed seed sequence 0..199 — no `Math.random`):
- **Unconditional baseline:** mean `rev_c(t,h)` over **all** bars (every |z|,
  ignoring the stretched condition) — "do residuals revert on average regardless?"
- **Randomized relationships:** rebuild the "implied" leg from a **wrong/shuffled
  triangle** (permute which majors form the implied cross) → a residual that is not
  the true no-arb relationship; recompute conditional reversion.
- **Shuffled timestamps:** detach the forward window from the event by drawing the
  forward residual change from a **random bar** (same count), breaking the
  deviation→reversion time link.
- **Matched nulls:** **session-matched** random bars (lab UTC session bucket) +
  random relationship → conditional reversion.

**Decisive statistic:** `matched_z = (observed_stretched_reversion − null_mean) /
null_std` per relationship/pool × bucket × horizon × null.

## 10. Significance / multiple-comparison (frozen)

- Bar: **|matched-Z| ≥ 2** to "clear" a cell.
- 8 relationships × {stretched,extreme} × 5 horizons is large; isolated |Z|≈2 hits
  are the multiple-comparison **noise expectation**. A real factor clears **multiple
  coherent cells** under **all four** nulls AND is **not** explained by the no-arb /
  microstructure artifact test (§11).

## 11. No-arb / microstructure artifact test (frozen)

Triangular residuals can "revert" trivially because three mid prices are
non-synchronous (stale-quote catch-up), inside the cost band. To separate genuine RV
from this artifact, pre-register three checks:
- **Horizon profile:** a microstructure artifact reverts ~entirely by the **first
  (5-min) horizon** and is flat after; a genuine RV factor reverts progressively
  over longer horizons matching its **half-life**.
- **Scale vs spread:** report residual std and reversion magnitude in **bp vs the
  triangle's summed leg spread (bp)**. Reversion confined **within the summed-spread
  band** is descriptively flagged as no-arb-band (not a usable factor) — recorded,
  not used to set the verdict's null test.
- **Half-life sanity:** an AR(1) half-life of **≤1 bar** indicates noise/staleness,
  not exploitable reversion; a half-life on the order of the horizons studied is
  consistent with a genuine slow relationship.

## 12. Robustness axes (frozen — Phase 6, stability not optimization)

- **Nearby normalization:** L ∈ {24, 96} vs primary 48; and a **median/MAD**
  robust-z variant vs mean/std.
- **Nearby relationship definitions:** the secondary **shared-leg cointegration
  spreads** (§2) vs the primary triangular residuals.
- **Nearby deviation thresholds:** stretched at |z| ≥ 1.5 and ≥ 2.5 vs 2.0.
The verdict uses the **primary** spec; robustness only tests whether the conclusion
survives these neighbours.

## 13. What is NOT allowed post-data (frozen)

No change to relationships, normalization, L, thresholds, horizons, nulls, seeds, or
the |Z|≥2 / multiple-cell / artifact rules after seeing a number. No dropping a
relationship to improve a statistic (all 8 reported). No new relationship invented
to rescue a weak result (that would be the C028 best-of-N anti-pattern). No
cost/tradability gate decides the verdict.

## 14. Frozen verdict map (applied mechanically in Phase 7)

| Verdict | Condition |
|---|---|
| **FACTOR_FRONT_GATE_CANDIDATE** | reversion clears |Z|≥2 on **multiple** relationships under **all four** nulls, robust across pairs/years/sessions/neighbours, **and passes the §11 artifact test** (progressive reversion over horizons, half-life > 1 bar, not confined to the no-arb band) |
| **FACTOR_REAL_BUT_WEAK** | genuine null-separated reversion exists **somewhere stable** but is narrow (few relationships / modest Z / partial robustness) OR is confined to the no-arb/microstructure band |
| **FACTOR_REJECTED** | reversion within null, OR sign-incoherent / single-relationship-driven, OR entirely a no-arb/microstructure (instantaneous, sub-spread, half-life ≤ 1 bar) artifact |

This map is frozen. Phases 2–6 produce evidence; Phase 7 applies the table without
further latitude.
