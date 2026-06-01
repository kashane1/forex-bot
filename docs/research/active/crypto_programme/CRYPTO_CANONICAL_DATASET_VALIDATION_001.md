# Crypto Canonical Dataset Validation 001 (Phase 3)

**Sprint:** `crypto-full-backfill-and-canonical-dataset-001` · Phase 3
**Date:** 2026-06-01
**Window:** `2021-05-31T00:00:00Z` → `2026-05-31T23:57:53Z`
**Granularity:** M1

---

## 1. BTC_USD validation table

| Check | Result | Notes |
|-------|--------|-------|
| Timestamp monotonicity | PASS | No duplicate or backward timestamps |
| OHLC invariants | PASS | 0 failures |
| Duplicate bars | PASS | 0 duplicates |
| Expected bars | 2,630,878 | |
| Actual bars | 2,629,439 | |
| Coverage | **99.945%** | Above 99.5% gate |
| Gap count | 1,439 missing bars | Exchange-side feed gaps |
| Volume non-negative | PASS | 0 negative volume rows |
| Zero-price bars | PASS | 0 |
| Single-bar return outliers (>20%) | PASS | 0 quarantined |
| Flash-wick outliers (>15% range/mid) | PASS | 0 quarantined |
| Stale flat runs (>60 identical closes) | PASS | 0 runs |
| **Classification** | **WARN** | Gaps detected; coverage gate passes |

---

## 2. ETH_USD validation table

| Check | Result | Notes |
|-------|--------|-------|
| Timestamp monotonicity | PASS | No duplicate or backward timestamps |
| OHLC invariants | PASS | 0 failures |
| Duplicate bars | PASS | 0 duplicates |
| Expected bars | 2,630,878 | |
| Actual bars | 2,629,403 | |
| Coverage | **99.944%** | Above 99.5% gate |
| Gap count | 1,475 missing bars | Exchange-side feed gaps |
| Volume non-negative | PASS | 0 negative volume rows |
| Zero-price bars | PASS | 0 |
| Single-bar return outliers (>20%) | PASS | 0 quarantined |
| Flash-wick outliers (>15% range/mid) | PASS | 0 quarantined |
| Stale flat runs (>60 identical closes) | PASS | 0 runs |
| **Classification** | **WARN** | Gaps detected; coverage gate passes |

---

## 3. Coverage summary

| Instrument | Coverage | Gate (≥99.5%) |
|------------|----------|---------------|
| BTC_USD | 99.945% | PASS |
| ETH_USD | 99.944% | PASS |

Missing bars are attributed to Coinbase exchange-side feed outages (not interpolated).

---

## 4. Gap analysis

### Largest gaps (BTC_USD)

| From (UTC) | To (UTC) | Missing bars |
|------------|----------|--------------|
| 2026-05-08T01:16:00Z | 2026-05-08T07:48:00Z | 391 |
| 2025-10-25T15:13:00Z | 2025-10-25T21:03:00Z | 349 |
| 2023-03-04T16:59:00Z | 2023-03-04T21:37:00Z | 277 |
| 2024-10-26T16:06:00Z | 2024-10-26T17:18:00Z | 71 |
| 2024-05-31T22:11:00Z | 2024-05-31T23:19:00Z | 67 |

### Largest gaps (ETH_USD)

| From (UTC) | To (UTC) | Missing bars |
|------------|----------|--------------|
| 2026-05-08T01:15:00Z | 2026-05-08T07:50:00Z | 394 |
| 2025-10-25T15:12:00Z | 2025-10-25T21:03:00Z | 350 |
| 2023-03-04T17:00:00Z | 2023-03-04T21:39:00Z | 278 |
| 2024-10-26T16:06:00Z | 2024-10-26T17:18:00Z | 71 |
| 2024-05-31T22:11:00Z | 2024-05-31T23:19:00Z | 67 |

BTC and ETH share the same outage windows — consistent with exchange-side maintenance/outages, not instrument-specific corruption.

---

## 5. Outlier summary

| Outlier type | BTC_USD | ETH_USD |
|--------------|---------|---------|
| Zero-price bars | 0 | 0 |
| Single-bar return >20% | 0 | 0 |
| Flash wick >15% | 0 | 0 |
| Stale flat runs >60 bars | 0 | 0 |

No bars quarantined. No auto-fix applied.

---

## 6. Quarantine decisions

| Decision | Rationale |
|----------|-----------|
| Gaps: **report only** | Coverage ≥99.5%; gaps align across BTC/ETH at same timestamps → exchange-side |
| Outliers: **none to quarantine** | Zero flagged bars |
| Interpolation: **not applied** | Per design requirements |

---

## 7. PASS/WARN/FAIL classification

| Instrument | Script status | Coverage gate | Overall |
|------------|---------------|---------------|---------|
| BTC_USD | WARN (gaps) | PASS | **PASS with warnings** |
| ETH_USD | WARN (gaps) | PASS | **PASS with warnings** |

No FAIL conditions. OHLC, monotonicity, and coverage gates all pass.

---

## 8. Materialization eligibility

**Eligible.** M1 coverage exceeds 99.5% for both instruments. Proceed to Phase 4 materialization of M5/M15/H1/H4/D1.

---

## 9. Family C diagnostic eligibility (pre-materialization)

**Pending Phase 4–6.** M1 validation passes coverage gate. Full Family C readiness requires:

- D1 and M15 derived timeframes materialized
- Cost model frozen
- Gap report reviewed (this document)
- Operator review of exchange-side gaps

Preliminary: no data quality blockers beyond documented exchange gaps.

---

## 10. Validation artifacts

| Artifact | Path |
|----------|------|
| Outlier/gap scan JSON | `research/crypto/validation/canonical_m1_outlier_scan_001.json` |
| Validation script output | Run via `scripts/validate_crypto_store.py` |

---

## 11. Operator review required

Human review requested for:

1. Acceptance of exchange-side gaps (May 2026, Oct 2025, Mar 2023 outages) given 99.94%+ coverage
2. Confirmation that gap windows do not overlap critical diagnostic windows (Family C uses M15/H1/H4/D1 — gap impact diluted by aggregation)

No interpolation or auto-fix recommended.
