# Cross Relative-Value — Deviation-Response Study (Phase 3)

**Sprint:** `research-cross-relative-value-factor-validation-001` · Phase 3
**Status:** RESULT (descriptive; verdict deferred to Phase 7). Frozen construction
applied unchanged. Figures from committed `docs/research/cross_relative_value/
response_pooled.csv` + `response_by_relationship.csv`. Reversion in **bp** (1 bp =
1e-4 log); **positive = reverts toward zero**.
**Date:** 2026-05-30.

**Question:** when a triangular residual becomes **stretched** (|z| ≥ 2),
**extreme** (|z| ≥ 3), or **compressed** (|z| ≤ 0.5), what happens next at 5/15/30/
60/240 min? Metrics: signed reversion, P(reverts), fraction of the deviation closed.

---

## 1. Pooled response — stretched bucket (|z| ≥ 2)

```
horizon  mean_rev_bp  p_revert  frac_closed     n
   5        0.393      0.939       0.774      11862
  15        0.421      0.946       0.926      11862
  30        0.435      0.950       0.863      11861
  60        0.452      0.954       0.867      11861
 240        0.501      0.960       0.821      11858
```

**Stretched residuals revert, hard and consistently.** P(reverts) = **0.94–0.96**,
~**77–93%** of the deviation is closed, and the signed reversion is positive at
every horizon. This is a strong, unambiguous reversion response — the first
non-null directional/behavioral signal in the programme.

## 2. Per-relationship reversion (stretched, mean_rev_bp)

```
relationship    5      15     30     60     240    half-life
EUR_GBP       0.382  0.405  0.412  0.422  0.426    0.6 bar
EUR_JPY       0.308  0.330  0.346  0.354  0.358    9.6 bar
GBP_JPY       0.321  0.335  0.346  0.358  0.367    7.2 bar
AUD_JPY       0.446  0.457  0.478  0.479  0.483    4.8 bar
NZD_JPY       0.340  0.376  0.400  0.490  0.829    6.8 bar
EUR_CHF       0.428  0.476  0.492  0.499  0.502    0.8 bar
GBP_CHF       0.485  0.540  0.556  0.568  0.572    0.8 bar
EUR_AUD       0.434  0.449  0.450  0.446  0.468    0.8 bar
```

**All 8 relationships revert** (positive at every horizon), P(reverts) 0.87–0.98.
The effect is broad, not a single relationship.

## 3. Horizon profile — the microstructure signature (protocol §11)

The decisive *shape* fact: **most of the reversion is already complete by the
first (5-min) horizon.** Pooled, 0.393 bp of the eventual 0.501 bp (240-min) is
realized at 5 min — **~78% in the first bar**, then a slow crawl. Per protocol §11
a microstructure / stale-quote artifact "reverts ~entirely by the first horizon and
is flat after." That is largely what the **non-JPY** relationships (half-life ≤1
bar) show: EUR_CHF 0.428→0.502, GBP_CHF 0.485→0.572 — front-loaded, nearly flat.

**Exception — the JPY crosses show progressive reversion** matching their
multi-bar half-lives: NZD_JPY climbs 0.340→0.829 across horizons (half-life 6.8
bars); EUR_JPY/GBP_JPY rise gradually. These four have genuine slow reversion, not
pure 1-bar staleness.

## 4. Scale check (carried to §11 / Phase 7)

The reversion magnitude (~0.3–0.8 bp) sits **~10× inside the no-arb spread band**
(4.25–7.18 bp per triangle; Phase 2 §4). The deviations that revert are an order of
magnitude smaller than the triangle's transaction-cost band. (Descriptive — cost
is out of scope; this informs the artifact test, not a tradability gate.)

## 5. Compressed bucket (control)

When |z| ≤ 0.5 (relationship already tight) there is no material directional
reversion — as expected for a residual near its mean. The reversion is a property
of the **stretched** state, confirming it is a deviation→reversion response, not a
constant drift.

---

## 6. Phase-3 reading (no verdict here)

Triangular residual deviations **revert strongly and consistently** (P≈0.95, ~80%
closed, all 8 relationships, all horizons) — a genuine reversion response. But two
construction facts temper it: (a) the reversion is **front-loaded** (~78% in the
first 5 min) with a clear microstructure signature on the 4 non-JPY relationships
(half-life ≤1 bar), and (b) it is **~10× inside the no-arb cost band**. The 4 JPY
crosses show genuine *progressive* multi-bar reversion. Phase 4 tests cross-
sectional stability, Phase 5 the formal nulls, Phase 6 robustness, and Phase 7
weighs the genuine-reversion-vs-no-arb-band question via the frozen §11 test.
