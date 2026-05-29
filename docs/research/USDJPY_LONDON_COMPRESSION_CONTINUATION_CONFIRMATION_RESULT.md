# USD_JPY London Compression-Continuation — Confirmation Result

**Sprint:** `usdjpy-london-compression-continuation-confirmation-001` · **Phase 2**
**Tooling:** `scripts/confirm_usdjpy_london_compression_continuation.py`
**Output:** `research/usdjpy_london_compression_continuation/confirmation_summary.json`
**Locked definition:** `USDJPY_LONDON_COMPRESSION_CONTINUATION_LOCKED_DEFINITION.md`

> DIAGNOSTIC ONLY. Not a strategy, not edge, not a campaign. The locked definition was
> frozen *before* this run; the only output is pass/fail against it. TEST sealed.

---

## Headline

**The London compression-continuation lead FAILS confirmation, decisively and on
multiple independent grounds.** The prior positive numbers reproduce **exactly** — but
only in the unrealistic configuration that has **no protective stop**, **optimistic
cost**, ignores **multiple testing**, and ignores **year-to-year instability**. The
moment any realism is added, the effect collapses or reverses.

- **3,065** London compressed-continuation trades simulated across train+validation.

---

## Result grid (mean pips/trade, net)

### No protective stop (matches the prior sim)

| cell | train | val | val n | val Bonferroni-p (×12) | survives haircut |
|---|---|---|---|---|---|
| h16, base cost | +1.04 | +3.04 | 692 | 0.977 | **No** |
| h32, base cost | +2.21 | +6.12 | 712 | 0.041 | val yes / **train no (p=1.0)** |
| h16, conservative | **−0.65** | +1.34 | 692 | 1.0 | **No** |
| h32, conservative | +0.33 | +4.26 | 712 | 0.52 | **No** |
| h32, optimistic | +5.16 | +9.06 | 712 | 0.0001 | yes (but optimistic cost only) |

### With a realistic intrabar protective stop (base cost) — all strongly negative

| stop | h16 train | h16 val | h32 train | h32 val |
|---|---|---|---|---|
| range_1.0× | −5.94 | −6.30 | −6.97 | −7.70 |
| range_1.5× | −3.25 | −4.82 | −2.67 | −5.49 |
| atr_1.0× | −4.45 | −5.61 | −5.28 | −6.28 |

**Every** predeclared protective stop turns the lead **strongly negative on both splits
at both horizons.**

---

## Kill criteria — which fired (from the locked definition)

| # | criterion | fired? | evidence |
|---|---|---|---|
| 1 | train or val ≤ 0 after base cost | partial | base no-stop is positive both splits; but see #2/#3 |
| 2 | conservative cost flips either split negative | **YES** | h16 no-stop conservative train **−0.65** |
| 3 | intrabar stop eliminates the positive expectancy | **YES (decisive)** | all stops, both horizons, both splits **−3 to −7.7** |
| 4 | sample too small (<150/split) | no | n ≈ 690–850/split |
| 5 | survives only at a single cell | **YES** | positive only at no-stop + non-conservative cost; dies elsewhere |
| 6 | multiple-testing haircut removes significance | **YES** | h16 fails both splits; h32 fails on **train** (Bonferroni-p = 1.0) |
| 7 | dominated by outliers | partial | trimmed (drop-top-5) stays positive, but see #8 — it's a *regime*, not 5 trades |
| 8 | year/half-split sign inconsistency | **YES** | effect concentrated in 2022 (train) & 2024 (val); 2021/2023/2025 negative-or-flat |

Five of eight kill criteria fire (#2, #3, #5, #6, #8), including the decisive stop test.

---

## Why it fails (mechanism)

The no-stop "profit" comes from **holding continuation trades to a fixed horizon through
arbitrarily deep adverse excursions**. A realistic risk-managed trade places a protective
stop; those stops are hit on the many trades that dip hard against entry before (maybe)
recovering by the horizon. With any stop, the small +2–6 pip mean inverts to a −3 to −8
pip loss. This is the same failure mode the repo documented for the C022 post-entry
work: the apparent gain lives entirely in unbounded held risk, not in a capturable edge.

**Year breakdown** confirms it is a **trend-regime artifact**: nearly all of the no-stop
"edge" sits in 2022 (train: +4.1/+7.8 pips at h16/h32) and 2024 (val: +6.2/+8.6) — the
two strong USD_JPY trending years — while 2021, 2023 and 2025 are negative or flat. A
direction-blind continuation that only pays in trending years is a beta-to-trend
exposure, not an edge, and is exactly what the multiple-testing haircut and the year
check are designed to catch.

---

## Verdict on the lead

**FAILS confirmation.** It survives only under no-stop + optimistic/base cost + no
multiple-testing correction + favorable-years selection — i.e. it is not a tradable,
risk-managed, cost-surviving, robust edge. Per the locked kill criteria and the sprint
mandate, the readiness verdict is **`PAUSE_STRATEGY_RESEARCH`** (recorded in Phase 4).
Robustness detail in `USDJPY_LONDON_COMPRESSION_CONTINUATION_ROBUSTNESS.md`.
