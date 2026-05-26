# Cross-Campaign Exit Pathology Matrix

**Date:** 2026-05-26  
**Branch:** `research-stop-and-exit-diagnostics-001`  
**Artifacts:** [`cross_campaign_exit_matrix.json`](../../research/exit_diagnostics/cross_campaign_exit_matrix.json), [`cross_campaign_exit_matrix.csv`](../../research/exit_diagnostics/cross_campaign_exit_matrix.csv)

> **Diagnostic only** — `strategy_evidence: false`. No strategy approved. Contaminated campaigns labeled throughout.

---

## Headline: stop/time split is **not** C008-specific

The C008 pattern — hard stops at ~−0.79R expectancy, time exits at strongly positive expectancy — appears across **multiple rejected campaigns**, including the **C011 random-entry null**. This suggests a **structural exit-framework artifact** (stop + time-stop coexistence) rather than a mean-reversion-only pathology.

---

## Exit reason summary (all trades, all folds)

| campaign | integrity | trades | overall exp R | stop share | stop exp R | time share | time exp R | other dominant exit |
|---|---|---:|---:|---:|---:|---:|---:|---|
| C008 | CONTAMINATED | 823 | +0.061 | 68% | −0.795 | 32% | +1.880 | — |
| C009 | CONTAMINATED | 403 | +0.054 | 56% | −0.789 | 2% | +0.578 | target 41% (+1.18R) |
| C010 | CONTAMINATED | 2,791 | −0.041 | 24% | −0.792 | 75% | +0.193 | — |
| C011 null | NULL_RERUN | 1,180 | −0.003 | 20% | −0.831 | 79% | +0.209 | — |
| C012 | CONTAMINATED | 3,726 | −0.052 | 20% | −0.818 | 79% | +0.145 | — |
| C013 | CONTAMINATED | 7,940 | −0.056 | 23% | −0.948 | 77% | +0.211 | — |
| C014 | CONTAMINATED | 720 | −0.148 | 24% | −0.808 | 75% | +0.067 | — |
| C015 | **DEDUP_SAFE** | 375 | −0.010 | 59% | −0.876 | 41% | +1.259 | — |
| C016 | UNKNOWN | 137 | −0.063 | 64% | −0.766 | 35% | +1.194 | — |
| C017 | UNKNOWN | 230 | −0.023 | 28% | −0.889 | 67% | +0.339 | — |
| C002 | CONTAMINATED | 1,032 | −0.135 | 19% | −0.818 | — | — | trailing 81% (+0.030R) |
| C003 | CONTAMINATED | 628 | −0.118 | 19% | −0.751 | — | — | trailing 81% (+0.031R) |
| C004 | CONTAMINATED | 812 | −0.192 | 21% | −0.723 | — | — | trailing 81% (−0.054R) |
| C007 | CONTAMINATED | 1,109 | −0.131 | 21% | −0.724 | — | — | trailing 79% (+0.025R) |

Hard-stop expectancy clusters near **−0.75R to −0.95R** regardless of strategy family. Time-exit expectancy is **positive** in most stop+time campaigns but **does not lift overall expectancy above zero** except in pooled C008 baseline (contaminated).

---

## Campaigns dominated by hard stops

- **C008** (68% stop) — train losers 98% stops; validation winners 100% time exits (post-mortem finding, confirmed).
- **C009** (56% stop) — midline target absorbed 41% of exits; time exits rare (2%).
- **C015 deduped** (59% stop) — dedup-safe; still negative overall despite +1.26R time exits.
- **C016** (64% stop) — weekly momentum; time exits +1.19R but too few to offset stops.

---

## Campaigns dominated by time exits

- **C010–C014, C011 null, C017:** 67–79% time exits; time exp +0.07R to +0.34R; overall still ≤0 or negative.
- **C011 null** is critical: random entries with identical stop/time machinery show the same sign split — **time positive, stop negative** — without any edge thesis.

---

## Target exits capped winners (C009)

C009 replaced C008's open-ended 40-bar hold with **midline target** exits:

| exit | C008 share | C009 share | C008 exp R | C009 exp R |
|---|---:|---:|---:|---:|
| time | 32% | 2% | +1.880 | +0.578 |
| target | — | 41% | — | +1.182 |
| stop | 68% | 56% | −0.795 | −0.789 |

Target exits are 100% winners at ~+1.18R but **lower tail** than C008 time exits (+1.88R). Train overall worsened (−0.025R vs C008 train −0.017R per post-mortem gates).

---

## Trailing-stop campaigns (C002–C004, C007)

Trend-family campaigns exit primarily via **trailing_stop** (~80%):

- Trailing exp ≈ **0R** (slightly positive C002/C003/C007; negative C004).
- Hard stops remain −0.72R to −0.82R at ~20% share.
- Trailing did **not** rescue negative overall expectancy.

---

## Ambiguous exits and gap fills

- **ambiguous_exit** field present on C010–C017 fold CSVs — available for future slice but not dominant in aggregate exit_reason counts.
- **gap_fill** present on C015–C017 deduped/fold artifacts; absent on C008/C009 baseline schema.
- No campaign in this matrix shows gap_fill as a primary exit_reason bucket at aggregate level.

---

## Diagnostic answers (questions 1, 3, 4 partial)

1. **Not C008-unique.** Stop/time sign split appears in C010–C017, C015, C016, and **C011 null**.
3. **Time exits are not obviously validation-only luck** at the framework level — null baseline also shows positive time-stop expectancy. C008 validation concentration remains suspicious given contamination + fold leakage risk.
4. **C009 midline target** redirected winners from 40-bar time exits to capped ~+1.18R targets; train expectancy worsened.

---

## Rules observed

- No new strategy claims.
- No parameter recommendations.
- No approval.
- Contaminated rows labeled; C015 deduped preferred for clean cross-campaign reference.
