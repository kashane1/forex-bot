# Carry Factor — Cross-Sectional Validation (Phase 4)

**Sprint:** `research-carry-factor-validation-001` · Phase 4
**Type:** consistency analysis (currency / pair / regime / year / drop-one). Figures
from `research/carry/factor_validation/carry_factor_validation.json`. Gross only.
**Date:** 2026-05-31.

Tests whether the gross premium of Phase 3 is **broad and coherent** (a real
cross-sectional factor) or **carried by one currency / pair / episode** (the C1 failure
mode the protocol §9 pre-registered against). Decisions use the 3-month total return.

---

## 1. Per-currency consistency (the central diagnostic)

Mean rate vs mean 3-month forward **spot** and **total** return, per currency:

| Currency | Mean rate (%) | Fwd-3m **spot** | Fwd-3m **total** |
|---|---:|---:|---:|
| USD | 3.59 | +0.00000 | +0.00000 |
| GBP | 3.48 | −0.00217 | −0.00245 |
| NZD | 3.57 | −0.01007 | −0.00997 |
| AUD | 3.06 | −0.00323 | −0.00469 |
| CAD | 2.93 | −0.00571 | −0.00726 |
| EUR | 1.97 | −0.00153 | −0.00557 |
| CHF | 0.43 | +0.00733 | −0.00050 |
| JPY | 0.28 | **−0.01874** | **−0.02711** |

Cross-sectional slope of fwd-3m **total** on mean rate = **+0.00305** (corr **+0.48**) —
positive, the expected carry sign. **But the mechanism is one-sided:**

- The high-rate longs (NZD, AUD, CAD, GBP) themselves had **negative** forward spot — they
  did **not** appreciate; the longs contribute via accrual only (and NZD's spot was
  notably *bad*, −1.0%).
- The slope is positive almost entirely because the **lowest-rate currency, JPY, fell
  hardest** (spot −1.87%, total −2.71%) — and JPY is the **short** leg, so its decline is
  a large gain for the book.
- The other funder, **CHF, moved the *wrong* way for carry**: it *appreciated* (spot
  +0.73%), so shorting it lost on spot (total only ≈0 after its low accrual).

So the cross-section "works" through the **JPY short**, not through a coherent
high-yielder-appreciates / funder-depreciates pattern. CHF actively contradicts it.

## 2. Drop-one currency — the premium is a single-name story

3-month total HML-3 mean, recomputed dropping each currency from the universe:

| Dropped | Mean | | Dropped | Mean |
|---|---:|---|---|---:|
| USD | +0.0056 | | EUR | +0.0078 |
| GBP | +0.0067 | | AUD | +0.0057 |
| NZD | +0.0088 | | CAD | +0.0083 |
| CHF | +0.0094 | | **JPY** | **+0.0003** |

> Dropping **JPY collapses the premium from +0.0075 to +0.0003** — essentially to zero.
> Every other drop leaves it intact (0.0056–0.0094). **The entire gross carry premium in
> this window is the JPY short.**

This is the C1 lesson exactly: an effect that lives in a single name is not a broad
factor. It is economically *coherent* (JPY is the canonical funding currency and had the
largest rate gap), but in this ~5-year window with no carry crash it reduces to **"shorting
the yen worked, 2022–2026."**

## 3. Year consistency

3-month total HML-3 mean by calendar year:

| 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---:|---:|---:|---:|---:|---:|
| +0.0119 | +0.0004 | +0.0122 | +0.0074 | +0.0041 | +0.0260 |

Positive every year — but **2022 is essentially flat (+0.0004)**, the year of the
sharpest FX volatility / rate repricing. The premium is strongest in the calm
trend years (2023, 2026) and disappears in the most turbulent one — an early hint of
carry-crash fragility (formalised next).

## 4. Regime consistency

- **Rate regime** (USD policy-rate 3-month direction): hiking +0.0029 (n=23), on-hold
  +0.0100 (n=17), cutting +0.0110 (n=17). The premium is **weakest during the hiking
  episode** and strongest on-hold/cutting — i.e. it is *not* a pure "rates-going-up"
  artifact, but it is modest exactly when policy was most active.
- **Risk regime** (cross-sectional FX-return dispersion, calm vs turbulent halves): calm
  +0.0076 (n=27), turbulent +0.0073 (n=30). Roughly flat across the proxy — but note the
  proxy is coarse and the window contains **no genuine carry crash** (2008/2020-style), so
  this does **not** clear carry of crash risk; it only says no crash was sampled (H3
  cannot be properly tested here).

## 5. Instrument (pair) consistency

The 15-instrument HML-4 layer is **not** independent confirmation: its long basket is
dominated by JPY-crosses (AUD_JPY, NZD_JPY, GBP_JPY), i.e. *more concentrated* short-JPY
exposure than the currency layer. Its larger raw number (+0.0133 at 3m) reflects that
concentration, not breadth.

## 6. Verdict-relevant summary

- **Correctly signed and positive every year and regime** → not noise; a genuine gross
  tilt exists.
- **But not broad:** the premium is **entirely the JPY short** (drop-JPY → ~0), the
  high-yield longs did not appreciate, and the other funder (CHF) contradicts the sign.
- **Crash-untested:** the one decisive risk (carry crash) is absent from the window.

→ A real-but-narrow, single-name, episode-bound gross tilt. Phase 5 asks whether even
this separates from the nulls.
