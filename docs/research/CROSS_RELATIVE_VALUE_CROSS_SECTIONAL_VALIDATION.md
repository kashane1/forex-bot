# Cross Relative-Value — Cross-Sectional Validation (Phase 4)

**Sprint:** `research-cross-relative-value-factor-validation-001` · Phase 4
**Status:** RESULT (descriptive; verdict deferred to Phase 7). Construction
unchanged. Figures from committed `docs/research/cross_relative_value/
events_long.csv` (stretched events) + `response_by_relationship.csv`. Reversion in
**bp**, positive = reverts.
**Date:** 2026-05-30.

**Question:** is the triangular reversion **consistent** across relationships
(pairs/instruments), years, and sessions — a stable structure, or a few-cell
fluke?

---

## 1. Relationship (pair/instrument) consistency

**All 8 relationships revert positively at every horizon** (Phase 3 §2), P(reverts)
0.87–0.98. There is **no** relationship that fails to revert. By the dominant
split:
- **JPY crosses (EUR/GBP/AUD/NZD_JPY):** genuine multi-bar reversion (half-life
  4.8–9.6 bars), progressive over horizons.
- **Non-JPY (EUR_GBP, EUR_CHF, GBP_CHF, EUR_AUD):** revert too, but front-loaded /
  ≤1-bar (microstructure-dominated).

The reversion is **instrument-universal** — the broadest-based effect the
programme has produced.

## 2. Year consistency (pooled stretched, 60-min mean rev_bp)

```
year   mean_rev_bp   n
2021      0.464      603
2022      0.464     2520
2023      0.457     2525
2024      0.426     2501
2025      0.481     2635
2026      0.403     1077
```

**Stable every year** (0.40–0.48 bp), same sign throughout. No year reverses or
dominates — the structure persists across the whole 2021–2026 sample, including
2022 risk-off and 2024–25. This is the opposite of the prior families' year-to-year
sign flips.

## 3. Session consistency (pooled stretched, 60-min mean rev_bp)

```
session     mean_rev_bp   n
asia          0.394      2691
london        0.405      2762
overlap       0.473      2311
new_york      0.486      2633
late          0.558      1464
```

**Reverts in every session** (0.39–0.56 bp). Mildly larger in the thin **late**
session (0.558) — consistent with a microstructure component being a bit stronger
when liquidity is thin (the §11 staleness story) — but the structure is present and
same-signed in the liquid london / overlap / NY sessions too.

## 4. Reading

The triangular reversion is **highly consistent cross-sectionally**: same sign and
comparable magnitude across **all 8 relationships, all 6 years, and all 5
sessions**. This is a *stable, broad-based* structure — unlike S2 (currency
strength) and C1-on-crosses, which were sign-incoherent across slices. Stability is
genuine.

**Caveat carried to Phase 7:** stability does **not** by itself settle the
genuine-RV-vs-no-arb-band question. A no-arbitrage / stale-quote effect *would also*
be stable across years and sessions (it is a structural property of quoting, not a
regime trade). The slightly larger thin-session reversion and the front-loaded
horizon profile (Phase 3 §3) are consistent with a sizable microstructure
component. The verdict (Phase 7) weighs this stable, broad reversion against the
§11 scale/half-life/horizon evidence.

---

## 5. Phase-4 reading (no verdict here)

The reversion is **stable and instrument-universal** across pairs, years, and
sessions — a real, broad structure, not a fluke. Whether that structure is an
exploitable RV factor or a stable-but-within-cost-band no-arb/microstructure
property is the §11/Phase-7 question. Phase 5 quantifies null separation; Phase 6
tests definitional robustness.
