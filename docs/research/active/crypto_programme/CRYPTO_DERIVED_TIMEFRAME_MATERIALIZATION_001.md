# Crypto Derived Timeframe Materialization 001 (Phase 4)

**Sprint:** `crypto-full-backfill-and-canonical-dataset-001` · Phase 4
**Date:** 2026-06-01
**Alignment:** UTC (`alignment_tz=UTC`, `alignment_hour=0`)
**Policy:** Omit incomplete buckets

---

## 1. Row counts by asset and timeframe

| Timeframe | BTC_USD rows | ETH_USD rows |
|-----------|-------------|-------------|
| M5 | 525,706 | 525,699 |
| M15 | 175,197 | 175,189 |
| H1 | 43,764 | 43,756 |
| H4 | 10,907 | 10,899 |
| D1 | 1,783 | 1,779 |

---

## 2. First/last timestamp by asset/timeframe

| Asset | TF | First (UTC) | Last (UTC) |
|-------|-----|-------------|------------|
| BTC_USD | M5 | 2021-05-31T00:00:00Z | 2026-05-31T23:50:00Z |
| BTC_USD | M15 | 2021-05-31T00:00:00Z | 2026-05-31T23:30:00Z |
| BTC_USD | H1 | 2021-05-31T00:00:00Z | 2026-05-31T22:00:00Z |
| BTC_USD | H4 | 2021-05-31T00:00:00Z | 2026-05-31T16:00:00Z |
| BTC_USD | D1 | 2021-05-31T00:00:00Z | 2026-05-29T00:00:00Z |
| ETH_USD | M5 | 2021-05-31T00:00:00Z | 2026-05-31T23:50:00Z |
| ETH_USD | M15 | 2021-05-31T00:00:00Z | 2026-05-31T23:30:00Z |
| ETH_USD | H1 | 2021-05-31T00:00:00Z | 2026-05-31T22:00:00Z |
| ETH_USD | H4 | 2021-05-31T00:00:00Z | 2026-05-31T16:00:00Z |
| ETH_USD | D1 | 2021-05-31T00:00:00Z | 2026-05-29T00:00:00Z |

D1 last bar at 2026-05-29 reflects omit-incomplete-bucket policy: 2026-05-30 and 2026-05-31 UTC days are incomplete at backfill cutoff (`2026-05-31T23:57:53Z`).

---

## 3. D1 availability

| Asset | D1 rows | ~5y expected | Status |
|-------|---------|--------------|--------|
| BTC_USD | 1,783 | ~1,826 | **Available** |
| ETH_USD | 1,779 | ~1,826 | **Available** |

D1 is non-zero for both assets — satisfies Family C pre-diagnostic requirement (≥5y D1 coverage with complete UTC days).

M15 rows (~175k per asset) exceed the ≥1y requirement by a wide margin (~5y).

---

## 4. Materialization manifest paths

| Asset | Run ID | Manifest |
|-------|--------|----------|
| BTC_USD | `73337345-b31c-4df2-ad89-cd30195d9795` | `research/crypto/materialization/73337345-b31c-4df2-ad89-cd30195d9795.json` |
| ETH_USD | `c6cc0cbf-4774-4dbd-a309-4c743538d87d` | `research/crypto/materialization/c6cc0cbf-4774-4dbd-a309-4c743538d87d.json` |

M1 rows read: BTC 2,629,499; ETH 2,629,463.

---

## 5. Verification result

| Check | Result |
|-------|--------|
| Materialization runs | PASS (both instruments, no errors) |
| Duplicate derived bars | PASS (0 duplicates — `COUNT(*) == COUNT(DISTINCT time_utc)` per TF) |
| UTC alignment | PASS (crypto design convention) |
| Incomplete bucket omission | PASS (D1 stops at last complete UTC day) |
| OHLCV recomputation | PASS (aggregation via shared `aggregate_m1_candles` with D1→`D` candle mapping fix) |
| Aggregation config hash | `f9b7246b79a0635c` (forex canonical hash; crypto uses UTC override at runtime) |

**Note:** `verify_materialized_pair()` defaults to forex NY alignment (`America/New_York`, hour 17) and does not accept UTC overrides. It is not used for crypto verification. Crypto materialization explicitly passes `alignment_tz=UTC`, `alignment_hour=0`.

**Code fix applied:** `timeframe_aggregation.py` maps D1 target to Candle granularity `D` (storage remains `D1` via `STORAGE_GRANULARITY`).

---

## 6. Known warnings

| Warning | Impact |
|---------|--------|
| D1 last bar 2026-05-29 | Last 2 UTC days incomplete at cutoff — expected |
| H4 last bar 2026-05-31T16:00Z | Last H4 bucket incomplete at cutoff — expected |
| Exchange-side M1 gaps | Propagate as omitted buckets in derived TFs — acceptable |
| Aggregation config hash | Forex fingerprint; crypto UTC alignment documented separately in manifests |

---

## 7. Family C pre-diagnostic needs

| Requirement | Status |
|-------------|--------|
| M15 available (≥1y) | **PASS** (~5y, 175k bars/asset) |
| D1 available (≥5y) | **PASS** (~1,780 complete UTC days/asset) |
| H1/H4 for horizon ladder | **PASS** |
| UTC-aligned buckets | **PASS** |

Derived timeframes **satisfy** Family C Trend Persistence pre-diagnostic data needs.

---

## 8. Elapsed time

| Asset | Elapsed |
|-------|---------|
| BTC_USD | ~2 min 4 s |
| ETH_USD | ~2 min 2 s |
