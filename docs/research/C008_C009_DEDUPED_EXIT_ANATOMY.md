# C008/C009 Deduped Exit Anatomy

**Date:** 2026-05-27  
**Branch:** `infra-deduped-c008-c009-rerun-forensic-only-001`  
**Artifact:** [`research/deduped_c008_c009_rerun/deduped_exit_anatomy.json`](../../research/deduped_c008_c009_rerun/deduped_exit_anatomy.json)

> **Forensic only** — `strategy_evidence: false`. Base cost only.

---

## C008 train vs validation (deduped replay)

| split | stop share | stop exp R | time share | time exp R |
|---|---:|---:|---:|---:|
| train | 71% | −0.802 | 29% | +1.894 |
| validation | 64% | −0.785 | 36% | +1.827 |

Matches pre-replay stop/exit diagnostics within rounding (**persists: yes**).

Validation winners remain time-exit dominated. Train losers remain stop dominated.

---

## C009 train vs validation (deduped replay)

| split | stop | target | time |
|---|---:|---:|---:|
| train stop/target/time share | 60% / 38% / 1% | | |
| train exp R by exit | −0.799 / +1.112 / +0.598 | | |
| validation stop/target/time share | 50% / 45% / 5% | | |
| validation exp R by exit | −0.768 / +1.154 / +0.516 | | |

**Midline target capping persists: yes** — target median ~+1.27R vs C008 time median ~+1.41R on validation; C008 time exp +1.83R vs C009 target +1.15R on validation in prior sprint.

---

## Cross-campaign pathology (deduped)

| pathology | persists |
|---|---|
| stop/time sign split (C008) | **yes** |
| C009 target replaces C008 time exits | **yes** |
| delayed reversion via 40-bar time stop (C008) | **yes** (time exp +1.86R, avg bars 40) |
| train stop dominance | **yes** |

---

## Comparison to contaminated-era diagnostics

Exit shares and expectancies match `research/exit_diagnostics/c008_c009_exit_forensics.json` and `cross_campaign_exit_matrix.json` C008/C008 rows — **CONFIRMED_DEDUP_SAFE** for exit anatomy descriptive claims.
