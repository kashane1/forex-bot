# Carry Dataset — Validation (Phase 3)

**Sprint:** `research-financing-rate-data-ingestion-001` · Phase 3
**Type:** data validation + diagnostics. Docs-only (reads committed artifacts).
**No factor study, no edge claim.**
**Date:** 2026-05-31.

Validates the Phase-2 carry dataset on coverage, gaps, consistency, currency
relationships, and cross-construction logic. Figures read from
`docs/research/carry_rates/` artifacts.

---

## 1. Date coverage (corpus window 2021-05 → 2026-05, monthly)

| Ccy | distinct months (raw) | last raw obs | forward-fill tail |
|-----|----------------------:|--------------|-------------------|
| USD | 60 | 2026-04 | 1 month |
| AUD | 60 | 2026-04 | 1 month |
| NZD | 60 | 2026-04 | 1 month |
| CAD | 60 | 2026-04 | 1 month |
| CHF | 60 | 2026-04 | 1 month |
| JPY | 59 | 2026-03 | 2 months |
| EUR | 57 | 2026-01 | 4 months |
| GBP | 57 | 2026-01 | 4 months |

- **No mid-window gaps** — every currency has a regular monthly cadence across the
  window.
- The only fill is the **tail publication lag** (1 month for most; 2 for JPY; 4 for
  EUR/GBP), forward-filled from the last known value. After construction, **all 15
  instruments have exactly 60 monthly carry rows** in the window (min = max = 60).
- Deep history is also present (back to 2002-04, bounded by JPY's series start) for
  any future longer-window study.

## 2. Missing periods

- **Within-window:** none at monthly cadence.
- **Tail:** the 1–4-month publication-lag fill at the window end (above) — the
  **only** imputation, explicitly flagged. A future study must additionally apply a
  ≥1-month implementation lag (design §) so even the *known* months are used
  publication-safe.

## 3. Internal consistency

- **Triangular rate-residual: max |residual| = 1.78e-15** (machine zero, from
  `rate_provenance.json`) — every cross's carry equals the difference of its two
  USD-leg carries. The 8-currency matrix is perfectly internally consistent.
- **Cross-construction spot-checks** (`carry_differentials.csv`):
  - `carry(EUR_JPY) = 3.9003` vs `carry(EUR_USD)+carry(USD_JPY) = 3.9003`
    (diff 4.4e-16).
  - `carry(GBP_JPY) = 5.1750` vs `carry(GBP_USD)+carry(USD_JPY) = 5.1750`
    (diff 0.0).
  Additive triangular identity holds exactly → cross construction logic verified.

## 4. Currency relationships (sanity)

- **Funding currencies are always the lowest-yield:** over the corpus window the
  *lowest-rate* currency is **CHF 52.5%** / **JPY 47.5%** of months — and **no other
  currency is ever the lowest.** Exactly the textbook funding pair.
- **High-yielders on top:** *highest-rate* currency is **NZD 66.1%**, USD 15.3%
  (the 2022–23 Fed peak), GBP 11.9%, AUD 6.8% of months. Correct regime ordering.

## 5. Diagnostics — carry distribution (corpus window, annualized %)

```
inst       mean   std    min    max   pos%  sign-stable
NZD_JPY    3.37  1.84   0.40   5.69   1.00   yes
USD_JPY    3.37  1.79   0.16   5.47   1.00   yes
GBP_JPY    3.26  1.71   0.14   5.53   1.00   yes
USD_CHF    3.19  1.14   0.83   4.32   1.00   yes
GBP_CHF    3.08  1.10   0.81   4.14   1.00   yes
AUD_JPY    2.82  1.48   0.08   4.36   1.00   yes
EUR_JPY    1.74  1.59  -0.53   3.98   0.78   no
EUR_CHF    1.55  0.86   0.13   2.49   1.00   yes
USD_CAD    0.66  0.63  -0.21   1.70   0.83   no
NZD_USD   -0.00  0.68  -1.40   0.90   0.68   no
GBP_USD   -0.11  0.27  -0.94   0.43   0.30   no
AUD_USD   -0.55  0.51  -1.40   0.57   0.07   no
EUR_AUD   -1.08  0.58  -2.31  -0.24   0.00   yes
EUR_GBP   -1.53  0.40  -2.17  -0.61   0.00   yes
EUR_USD   -1.64  0.52  -2.63  -0.63   0.00   yes
```

## 6. Positive / negative carry frequency

- **Always-positive carry (sign-stable +):** NZD_JPY, USD_JPY, GBP_JPY, USD_CHF,
  GBP_CHF, AUD_JPY, EUR_CHF — the classic carry crosses (high-yield/USD vs JPY/CHF
  funding).
- **Always-negative carry (sign-stable −):** EUR_USD, EUR_GBP, EUR_AUD — long-EUR
  vs higher-yield legs.
- **Sign-flipping (regime-dependent):** AUD_USD (7% positive), GBP_USD (30%),
  NZD_USD (68%), USD_CAD (83%), EUR_JPY (78%) — these reflect the **2022–23 Fed
  hiking cycle** reordering USD vs AUD/GBP/NZD, and EUR_JPY crossing zero early in
  the window. Economically expected.

## 7. Currency-ranking frequency

- **Highest-yield:** NZD 0.661 · USD 0.153 · GBP 0.119 · AUD 0.068.
- **Lowest-yield:** CHF 0.525 · JPY 0.475.
- Dispersion across 8 currencies is real and time-varying (the ranking reorders with
  the hiking cycle) — a genuine cross-sectional carry signal *exists in the data*
  (its predictive value is **not** assessed here — out of scope).

## 8. Validation verdict (data-quality only)

The carry dataset is **complete, internally consistent, lookahead-safe at monthly
cadence, and economically sensible.** No within-window gaps; the only imputation is
the documented 1–4-month tail fill; triangular consistency is exact; funding/
high-yield rankings and sign patterns match known regimes. The dataset is
**research-grade as a DATA asset.** Whether it is *sufficient* for a factor study —
given the monthly cadence, ~5y window, and interbank-vs-broker-financing gap — is
the readiness question (Phase 6). Plausibility against macro history is Phase 4.
