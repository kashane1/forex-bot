# C1 High-Volatility Stability Study (Phase 5)

**Status:** RESULT (descriptive; no verdict here)
**Date:** 2026-05-29
**Branch:** `research-c1-high-volatility-frontgate-001`
**Source:** high-vol subset of the committed C1 event panels. `C1_trend_cont_long`,
60-min signed return (negative = reversion). Buckets with n<15 marked "few".

There is **no held-out split** (the hard rules forbid train/val/test, and the
corpus has no spare data; the path was discovered on this corpus). "Stability"
here = persistence across **years**, **sessions**, and **pairs**, with **GBP_USD**
as the least-contaminated quasi-out-of-sample pair.

## 1. By calendar year (mean_ret60, t)

```
EUR_USD   2022 -2.75(-2.34) | 2023 +0.59(+0.43) | 2025 -1.44(-1.27) | 2026 -1.83(-1.03)   [2021,2024 few]
USD_JPY   2022 -2.41(-2.42) | 2023 -1.46(-0.95) | 2024 -4.20(-2.63) | 2025 -0.14(-0.09) | 2026 +3.46(+1.39)
GBP_USD   2021 -1.06(-0.68) | 2022 -0.34(-0.26) | 2023 -2.97(-1.90) | 2025 +0.89(+0.44) | 2026 -4.43(-1.46)   [2024 few]
```

- Sign is **mostly negative but not unanimous**: EUR_USD negative in 3/4 usable
  years (2023 positive); USD_JPY 4/5 (2026 positive, small n); GBP_USD 4/5 (2025
  positive). None meets the Phase-1 "≥4 of 6 years negative" bar *cleanly* once
  too-few years are excluded, and each pair has at least one positive year.
- **Magnitude is concentrated in a few years**: USD_JPY leans heavily on 2024
  (−4.20); EUR_USD on 2022 (−2.75). Removing the single strongest year materially
  weakens each pair.

## 2. By session (mean_ret60, t)

```
EUR_USD   london -4.31(-3.41) | ny -1.28(-0.91) | tokyo -0.30(-0.37) | offhours -0.08(-0.06)
USD_JPY   london -0.79(-0.61) | ny -2.13(-1.55) | tokyo -2.63(-2.80) | offhours -3.64(-1.87)
GBP_USD   london -3.22(-1.88) | ny -1.03(-0.73) | tokyo -0.07(-0.06) | offhours -0.42(-0.33)
```

- **Sign is negative in all 4 sessions on all 3 pairs** (the one Phase-1 stability
  sub-condition that is cleanly met).
- **But the magnitude is highly session-concentrated, and the concentration
  differs by pair**: EUR_USD lives almost entirely in **London** (−4.31, t −3.41;
  other sessions ≈ 0); USD_JPY in **Tokyo/NY/offhours** with London near zero;
  GBP_USD in London. There is **no single session** where the effect is uniformly
  strong across pairs — the "high-vol C1 fade" is really several different
  session-specific pockets that happen to share a sign.

## 3. By pair

The two primaries clear nulls (Phase 4) but are session-concentrated; GBP_USD (the
quasi-OOS pair) is the **weakest**: 60-min t only −1.58, below the raw spread on
cost (Phase 3), and with a positive year (2025) and near-zero Tokyo/offhours.

## 4. Answer to the Phase-5 question

**Concentrated, not robustly persistent.** The *sign* is persistent (negative
across all sessions, most years, all three pairs), but the *magnitude* — the part
that would have to pay for spread — is concentrated in specific
**pair×session×year** pockets (EUR_USD·London·2022, USD_JPY·Tokyo·2024) rather
than being a broad, always-on effect. By the Phase-1 stability criteria this is
**borderline at best**: the "≥3 of 4 sessions negative" sign test passes, but the
"≥4 of 6 years negative / no single year >60%" robustness test does not clear
cleanly, and the effect's economic weight rests on a few cells. This concentration
is consistent with the validation finding that the favourable cost cells were
session-specific — and it is *not* enough, on its own, to support a scaffold.
