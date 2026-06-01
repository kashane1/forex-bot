# Crypto Full Backfill Sprint 001 — Result (Phase 2)

**Sprint:** `crypto-full-backfill-and-canonical-dataset-001` · Phase 2
**Date:** 2026-05-31 → 2026-06-01 (UTC)
**Decision:** **COMPLETE** — full 5y M1 backfill succeeded for both instruments

---

## 1. Requested window

| Parameter | Value |
|-----------|-------|
| Start (UTC) | `2021-05-31T00:00:00Z` |
| End (UTC) | `2026-05-31T23:57:53Z` |
| Granularity | M1 |
| Source | Coinbase Exchange public REST (`coinbase-spot`) |

---

## 2. BTC_USD results

| Metric | Value |
|--------|-------|
| Status | PASS |
| Batch ID | `e22d34a8-c065-4225-b703-179464720c78` |
| Manifest | `research/crypto/manifests/e22d34a8-c065-4225-b703-179464720c78.json` |
| Requested start | `2021-05-31T00:00:00Z` |
| Requested end | `2026-05-31T23:57:53Z` |
| Actual first bar | `2021-05-31T00:00:00Z` |
| Actual last bar | `2026-05-31T23:57:00Z` |
| Candles fetched | 2,629,439 |
| Candles upserted | 2,629,439 |
| Expected bars | 2,630,878 |
| Coverage | 99.945% |
| Failures/retries | 0 (no errors in manifest) |
| Started (UTC) | `2026-05-31T23:57:54Z` |
| Finished (UTC) | `2026-06-01T00:47:23Z` |
| Elapsed | ~49 min 29 s |

---

## 3. ETH_USD results

| Metric | Value |
|--------|-------|
| Status | PASS |
| Batch ID | `0d50f9aa-7e3c-404a-8644-95f70f57ac8c` |
| Manifest | `research/crypto/manifests/0d50f9aa-7e3c-404a-8644-95f70f57ac8c.json` |
| Requested start | `2021-05-31T00:00:00Z` |
| Requested end | `2026-05-31T23:57:53Z` |
| Actual first bar | `2021-05-31T00:00:00Z` |
| Actual last bar | `2026-05-31T23:57:00Z` |
| Candles fetched | 2,629,403 |
| Candles upserted | 2,629,403 |
| Expected bars | 2,630,878 |
| Coverage | 99.944% |
| Failures/retries | 0 (no errors in manifest) |
| Started (UTC) | `2026-06-01T00:47:28Z` |
| Finished (UTC) | `2026-06-01T01:37:46Z` |
| Elapsed | ~50 min 18 s |

---

## 4. Combined summary

| Instrument | Rows upserted | Coverage | API chunks (est.) | Elapsed |
|------------|---------------|----------|-------------------|---------|
| BTC_USD | 2,629,439 | 99.945% | 8,770 | ~49 min |
| ETH_USD | 2,629,403 | 99.944% | 8,770 | ~50 min |
| **Total** | **5,258,842** | — | **~17,540** | **~100 min** |

Missing bars (exchange-side gaps, not interpolated):

| Instrument | Missing | Gap count (approx.) |
|------------|---------|---------------------|
| BTC_USD | 1,439 | To be detailed in Phase 3 validation |
| ETH_USD | 1,475 | To be detailed in Phase 3 validation |

Both instruments exceed the 99.5% coverage gate.

---

## 5. Manifest paths

| Run | Manifest |
|-----|----------|
| BTC full backfill | `research/crypto/manifests/e22d34a8-c065-4225-b703-179464720c78.json` |
| ETH full backfill | `research/crypto/manifests/0d50f9aa-7e3c-404a-8644-95f70f57ac8c.json` |
| Preflight BTC (2h) | `research/crypto/manifests/1d00f0c0-554d-4970-9141-a6480170316f.json` |
| Preflight ETH (2h) | `research/crypto/manifests/04fb6b49-e908-4c79-9f81-6713785305bc.json` |
| Pilot (prior sprint) | `research/crypto/manifests/7c05a4c2-*.json`, `3add769b-*.json` |

---

## 6. Storage

| Field | Value |
|-------|-------|
| Destination | Local Postgres `market_data.candles` |
| Raw data committed to git | **No** |
| DB dumps committed | **No** |

---

## 7. Blockers

**None.** Full 5y backfill completed without API limit, rate limit, or DB failures.

---

## 8. Next step

Phase 3: run `scripts/validate_crypto_store.py` over full window; produce gap/outlier report.
