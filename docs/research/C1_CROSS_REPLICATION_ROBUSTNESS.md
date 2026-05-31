# C1 Cross-Replication — Robustness Review (Phase 4)

**Sprint:** `research-c1-cross-replication-screen-001` · Phase 4
**Status:** RESULT (descriptive; verdict deferred to Phase 5). The factor
definition is **unchanged**; this phase only slices the existing C1_long event
panels by year, session, and volatility, and reads the frozen one-knob
perturbation specs from `c1_cross_robustness.csv`. All figures from committed
CSVs.
**Date:** 2026-05-30.

Focus pairs: the 3 JPY-quote required crosses that showed a weak 30-min tilt
(EUR_JPY, GBP_JPY, AUD_JPY), the only 60-min null-clearing pair (GBP_CHF,
optional), and the cheapest cross (EUR_GBP). C1_long, the primary effect.

---

## 1. Pair-by-pair sensitivity (recap from Phase 2/3)

Already established: on the 4 **required** crosses the 60-min effect is within
null (|mZ60| ≤ 0.64), 2/4 sign-flip positive, and the lone 30-min null-clearing
required pair (EUR_JPY, mZ30 −2.26) **reverses** by 60 min. The only 60-min
null-clearing pair is **GBP_CHF** (optional, single pair → noise). The result is
**highly pair-sensitive** — the opposite of the majors, where the sign was
universal across all 7.

## 2. Year-by-year stability — C1_long mean60 (pips)

```
EUR_JPY  2021:-2.58  2022:+0.24  2023:+0.49  2024:-0.56  2025:+0.47  2026:+1.27
GBP_JPY  2021:-0.93  2022:-1.72  2023:+0.84  2024:+0.76  2025:-0.59  2026:+1.25
AUD_JPY  2021:-0.27  2022:-0.34  2023:+1.18  2024:-0.18  2025:-0.16  2026:-0.32
GBP_CHF  2021:+0.80  2022:-2.22  2023:-1.17  2024:-0.49  2025:-0.50  2026:-0.08
EUR_GBP  2021:-0.57  2022:-0.08  2023:+0.16  2024:-0.65  2025:+0.01  2026:+0.54
```

**No required cross holds its sign across years.** EUR_JPY and GBP_JPY flip sign
repeatedly year to year; AUD_JPY is near zero with one positive year (2023).
Crucially, **GBP_CHF's apparent effect is period-concentrated** in **2022 (−2.22)
and 2023 (−1.17)** — a single risk-off macro window — and is weak/positive
elsewhere. That is the fingerprint of a **regime artifact**, not a stable factor.

## 3. Session stability — C1_long mean60 (pips)

```
EUR_JPY  london:+0.99  ny:+0.18  offhours:-1.46  tokyo:-0.04
GBP_JPY  london:-0.07  ny:+0.82  offhours:-2.41  tokyo:-0.35
AUD_JPY  london:+0.03  ny:-0.21  offhours:+0.12  tokyo:+0.31
GBP_CHF  london:-0.54  ny:-1.11  offhours:-1.59  tokyo:-0.38
```

Signs flip across sessions on every required pair. The negative readings cluster
in **off-hours** (EUR_JPY −1.46, GBP_JPY −2.41, GBP_CHF −1.59) — the **thinnest,
widest-spread** part of the day. An "effect" that lives in off-hours on
wide-spread crosses is far more consistent with **microstructure/spread noise**
than with the C1 multi-timeframe confluence mechanism.

## 4. Volatility stability — C1_long mean30 / mean60 by vol tercile

```
EUR_JPY  lo:30=-0.01/60=+1.20  mid:30=-0.64/60=-0.16  hi:30=-0.62/60=-0.54
GBP_JPY  lo:30=-0.42/60=+0.24  mid:30=-0.56/60=-0.63  hi:30=-0.27/60=+0.17
AUD_JPY  lo:30=+0.08/60=+0.34  mid:30=-0.03/60=+0.36  hi:30=-0.43/60=-0.56
GBP_CHF  lo:30=-0.37          mid:60=-0.91          hi:60=-1.05
```

**No coherent, majors-like vol gradient.** On the majors the C1 effect was
*strongest in high vol*. Here EUR_JPY's largest 60-min reading is **+1.20 in the
LOW-vol tercile** (positive — the wrong sign), and the JPY crosses show no
monotone pattern. Only **GBP_CHF** strengthens with vol (lo −0.37 → hi −1.05) —
but GBP_CHF is the isolated optional pair whose effect we already flagged as
period/session-concentrated; a vol gradient on the widest-tail CHF cross is again
consistent with spread/vol noise rather than confluence.

## 5. Specification robustness — C1_long mean60 under one-knob perturbations

```
pair      baseline ema_30_60 ema_10_40 slope_lb_5 trend_no_slope m15_strict drop_h4  add_m5
EUR_JPY     +0.162   +0.102   -0.243    +0.067     -0.233        +0.235    +0.101  +0.268
GBP_JPY     -0.071   -0.430   -0.138    -0.323     -0.131        +0.385    +0.090  -0.302
AUD_JPY     +0.045   -0.082   +0.056    +0.077     -0.127        +0.061    +0.203  +0.061
GBP_CHF     -0.774   -0.778   -0.652    -0.504     -0.790        -0.559    -0.695  -0.438
EUR_GBP     -0.059   -0.033   -0.144    +0.088     -0.080        -0.062    -0.161  -0.222
```

**The required crosses' signs are not stable to a single knob.** EUR_JPY flips to
−0.24 under `ema_10_40` and `trend_no_slope`; GBP_JPY flips to **+0.385** under
`m15_strict`; AUD_JPY scatters around zero. On the majors, C1 was robust to these
same one-knob perturbations — here it is not. **Only GBP_CHF stays negative across
all 8 specs** (−0.44 to −0.79) — spec-robust, but (per §2–§4) period- and
session-concentrated, i.e. robust to the *factor* knobs yet explained by *when/
where* it trades, not by the confluence.

---

## 6. Phase-4 reading (no verdict here)

Across all four robustness dimensions, **no required cross exhibits a stable C1
effect**: signs flip year to year, flip across sessions (negatives clustering in
thin off-hours), show no majors-like vol gradient, and do not survive one-knob
spec perturbation. The single spec-robust pair (GBP_CHF, optional) is a
**period-concentrated (2022–23), off-hours/wide-spread, single-pair** signal —
the signature of a regime/microstructure artifact, not of the C1 confluence
mechanism replicating. This is the **opposite** of the majors, where C1 was
sign-universal and robust to year, and to one-knob perturbation. Phase 5 applies
the frozen verdict map.
