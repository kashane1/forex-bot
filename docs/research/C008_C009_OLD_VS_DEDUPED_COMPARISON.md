# C008/C009 Old vs Deduped Comparison

**Date:** 2026-05-27  
**Branch:** `infra-deduped-c008-c009-rerun-forensic-only-001`  
**Artifact:** [`research/deduped_c008_c009_rerun/old_vs_deduped_metric_comparison.json`](../../research/deduped_c008_c009_rerun/old_vs_deduped_metric_comparison.json)

> **Forensic only** — `strategy_evidence: false`. No parameter recommendations.

---

## Summary table

| campaign | metric | original | deduped | classification |
|---|---|---:|---:|---|
| C008 | train trades | 216 | 216 | CONFIRMED_DEDUP_SAFE |
| C008 | train exp R | −0.017 | −0.025 | CONFIRMED_DEDUP_SAFE |
| C008 | validation trades | 138 | 138 | CONFIRMED_DEDUP_SAFE |
| C008 | validation exp R | +0.172 | +0.161 | CONFIRMED_DEDUP_SAFE |
| C008 | train gate | FAIL | FAIL | CONFIRMED_DEDUP_SAFE |
| C008 | validation positive | yes | yes | CONFIRMED_DEDUP_SAFE |
| C009 | train trades | 252 | 252 | CONFIRMED_DEDUP_SAFE |
| C009 | train exp R | −0.062 | −0.025 | MATERIAL_CHANGE |
| C009 | validation trades | 151 | 151 | CONFIRMED_DEDUP_SAFE |
| C009 | validation exp R | +0.170 | +0.186 | CONFIRMED_DEDUP_SAFE |
| C009 | train gate | FAIL | FAIL | CONFIRMED_DEDUP_SAFE |
| C009 | validation positive | yes | yes | CONFIRMED_DEDUP_SAFE |

Tolerance for CONFIRMED: ±0.02R on expectancy.

---

## Exit reason distribution (deduped base, train+val)

### C008

| exit | share | exp R | original diagnostic |
|---|---:|---:|---|
| stop | 68% | −0.796 | 68% / −0.795 |
| time | 32% | +1.864 | 32% / +1.880 |

**Stop/time split:** **persists** (CONFIRMED_DEDUP_SAFE).

### C009

| exit | share | exp R | original diagnostic |
|---|---:|---:|---|
| stop | 56% | −0.789 | 56% / −0.789 |
| target | 41% | +1.130 | 41% / +1.182 |
| time | 2% | +0.578 | 2% / +0.578 |

**Midline target capping:** **persists** — target exp ~+1.13R vs C008 time ~+1.86R on validation.

---

## Material changes

| finding | classification | note |
|---|---|---|
| C009 train exp −0.062 → −0.025 | MATERIAL_CHANGE | Still fails gate; likely engine/float path not entry-set change (trade count identical) |
| Duplicate rows in SQLite | SUPERSEDED | 106k duplicates dropped; redundant identical bars |
| Original LIKELY_CONTAMINATED label | SUPERSEDED for headline metrics | Deduped forensic ledger now canonical for descriptive claims |
| Promotion eligibility | STILL_BLOCKED | Train gate fail; financing unmodeled; test lockbox closed |

---

## Diagnostic questions answered

| # | answer |
|---|---|
| 1 | C008 replayed on deduped inputs with frozen rules: **yes** |
| 2 | C009 replayed on deduped inputs with frozen rules: **yes** |
| 3 | Headline metrics materially change: **mostly no**; C009 train exp shifted but gate outcome unchanged |
| 4 | Train fail / validation positive persists: **yes** |
| 5 | C009 winner-capping persists: **yes** |
| 6 | Stop/time split persists: **yes** |
| 7 | MAE/MFE persists: **yes** (see deduped MAE/MFE doc) |
| 8 | Prior artifacts: headline metrics **CONFIRMED**; integrity label **SUPERSEDED** by deduped forensic ledger |

---

## Rules observed

No tuned parameters. No approval claims. No test lockbox opened.
