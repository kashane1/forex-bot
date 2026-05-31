# Currency-Strength Factor — Cross-Sectional Validation (Phase 4)

**Sprint:** `research-currency-strength-factor-validation-001` · Phase 4
**Status:** RESULT (descriptive; verdict deferred to Phase 7). Factor unchanged.
Figures from committed `docs/research/currency_strength/cross_sectional.csv`
(derived from `events_long.csv`). Forward currency returns in **bp**.
**Date:** 2026-05-30.

**Question:** is the (near-zero) response **consistent** across currencies, pairs,
years, and sessions — i.e. is there *any* coherent sub-population where the factor
behaves, or is it uniformly noise?

---

## 1. Consistency across currencies (which currency is selected; 60m mean bp)

```
strongest  | AUD -0.05  CAD +0.11  CHF -0.27  EUR -0.17  GBP +0.14  JPY +0.15  NZD -0.07  USD +0.05
weakest    | AUD +0.01  CAD -0.25  CHF -0.27  EUR +0.25  GBP +0.08  JPY -0.10  NZD +0.13  USD -0.08
```

**No coherent cross-currency pattern.** For the *strongest* condition the 8
currencies split **4 positive / 4 negative**, all within **±0.27 bp**. If
currency strength carried a continuation signal, strong currencies would
predominantly continue up (consistent sign); they do not. The signs look like a
random partition, not a factor. (CHF appears mildly negative in both conditions,
but at |0.27| bp it is inside the null — Phase 5 — and a single currency is the
multiple-comparison noise expectation.)

## 2. Consistency across pairs

Per the construction, **each currency's forward return is itself the equal-weight
average over the pairs containing it** (signed) — so the per-currency view in §1
*is* the pair-aggregated view. With every currency's conditional mean within
±0.27 bp and split-signed, **no pair-level coherence is possible**: a coherent
pair effect would have to aggregate into a coherent currency effect, which is
absent. (CAD is the degenerate case — 1 instrument — so "CAD strength" is just
−USD_CAD; its ±0.1–0.25 bp readings are a single pair and carry no breadth.) No
pair sub-population rescues the factor.

## 3. Consistency across years (strongest / rapid_weaken, 60m mean bp)

```
strongest    2021 +0.60  2022 +0.00  2023 +0.13  2024 -0.05  2025 -0.16  2026 -0.15
weakest      2021 -0.45  2022 -0.08  2023 -0.11  2024 +0.00  2025 -0.01  2026 +0.41
rapid_weaken 2021 -0.14  2022 -0.09  2023 -0.12  2024 -0.15  2025 +0.05  2026 +0.16
```

**Signs flip year to year**, magnitudes ≤ 0.6 bp. The strongest condition is
positive in 2021 (+0.60) then drifts negative 2024–26; weakest mirrors loosely.
There is **no stable annual sign** — the factor does not hold in any consistent
direction across the sample. (2021 is a partial year from 2021-05-27, hence its
larger noise.)

## 4. Consistency across sessions (60m mean bp)

```
strongest    asia +0.12  london -0.05  overlap -0.03  new_york -0.09  late +0.18
weakest      asia -0.02  london -0.06  overlap -0.20  new_york +0.17  late -0.13
rapid_weaken asia -0.06  london -0.03  overlap -0.41  new_york +0.15  late +0.34
```

Signs flip across sessions; magnitudes ≤ 0.41 bp. No session (incl. the liquid
london / london-NY overlap) shows a coherent or material effect. The largest
single cell (rapid_weaken late +0.34, overlap −0.41) is sign-inconsistent across
sessions — noise, not structure.

## 5. Sign-consistency tally (the headline)

| Condition (60m) | across currencies | across years | across sessions | max |mean| |
|---|---|---|---|---|
| strongest | 4+ / 4− | 2+ / 3− | 2+ / 3− | 0.60 bp |
| rapid_weaken | 5+ / 3− | 2+ / 4− | 2+ / 3− | 0.52 bp |

Every axis splits close to 50/50 with sub-bp magnitudes — the fingerprint of
**no factor**, not a weak-but-coherent one.

---

## 6. Phase-4 reading (no verdict here)

The near-zero response is **uniformly noise** — there is **no currency, pair,
year, or session sub-population** in which cross-implied currency strength behaves
as a coherent directional factor. Signs split ~50/50 on every axis with magnitudes
≤ 0.6 bp (≈ 10% of 60m path noise). This is the opposite of a real factor, which
would show a consistent sign in at least some coherent slice. Phase 5 confirms
formally against the four nulls; Phase 6 checks lookback/aggregation robustness.
