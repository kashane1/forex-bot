# Crypto Full Backfill Sprint 001 — Preflight (Phase 1)

**Sprint:** `crypto-full-backfill-and-canonical-dataset-001` · Phase 1
**Date:** 2026-05-31
**Decision:** **GO** for full 5y M1 backfill

---

## 1. Command shape

```bash
# Full backfill (one instrument per run)
python scripts/ingest_crypto_candles_postgres.py \
  --instrument BTC_USD \
  --granularity M1 \
  --start 2021-05-31T00:00:00Z \
  --end <CURRENT_UTC>

python scripts/ingest_crypto_candles_postgres.py \
  --instrument ETH_USD \
  --granularity M1 \
  --start 2021-05-31T00:00:00Z \
  --end <CURRENT_UTC>
```

Materialization (post-validation):

```bash
python scripts/materialize_crypto_derived_timeframes.py \
  --instrument BTC_USD \
  --start 2021-05-31T00:00:00Z \
  --end <CURRENT_UTC> \
  --targets M5,M15,H1,H4,D1
```

---

## 2. Dry-run result

Materialization dry-run for BTC_USD over requested 5y window (current M1 data = pilot + preflight only):

| Target | Rows (dry-run) | First UTC | Last UTC |
|--------|----------------|-----------|----------|
| M5 | 1,987 | 2026-05-24T23:15Z | 2026-05-31T23:50Z |
| M15 | 638 | 2026-05-24T23:15Z | 2026-05-31T23:30Z |
| H1 | 132 | 2026-05-25T00:00Z | 2026-05-31T22:00Z |
| H4 | 9 | 2026-05-25T00:00Z | 2026-05-31T16:00Z |
| D1 | 0 | — | — (expected until full window ingested) |

Dry-run confirms UTC alignment and omit-incomplete-bucket policy. Full backfill will populate ~5y of M1 before materialization.

---

## 3. Source venue

| Field | Value |
|-------|-------|
| Venue | Coinbase Exchange public REST |
| Source tag | `coinbase-spot` |
| Endpoint | `GET /products/{BTC-USD\|ETH-USD}/candles?granularity=60` |
| Auth | None (public market data) |

---

## 4. Symbols

| Canonical | Coinbase product |
|-----------|------------------|
| `BTC_USD` | `BTC-USD` |
| `ETH_USD` | `ETH-USD` |

---

## 5. Target storage

| Field | Value |
|-------|-------|
| Engine | Local Postgres |
| Connection | `FOREX_BOT_RESEARCH_DATABASE_URL` → `localhost:5432/forex_bot` |
| Schema | `market_data.candles` (via `PostgresCandleStore.ensure_schema()`) |
| Upsert | Idempotent on `(instrument, granularity, time_utc, source)` |

---

## 6. Expected date range

| Parameter | Value |
|-----------|-------|
| Start | `2021-05-31T00:00:00Z` |
| End | Current UTC at execution (`2026-05-31T23:57Z` at preflight time) |
| Span | ~5 calendar years |

---

## 7. Expected row-count estimate

| Instrument | Expected M1 bars | API chunks (300/request) |
|------------|-----------------|--------------------------|
| BTC_USD | ~2,629,440 | 8,770 |
| ETH_USD | ~2,629,440 | 8,770 |

Chunk verification (`iter_coinbase_chunks`):

- Total chunks for 5y window: **8,770**
- Chunk span: **300 minutes** (5 hours) per request
- First chunk: `2021-05-31T00:00Z` → `2021-05-31T04:59Z`
- Last chunk: `2026-05-31T21:00Z` → `2026-05-31T23:59Z`

Estimated API wall time: ~15 min/instrument (8,770 × 0.1 s delay) + fetch/upsert latency → **~30–60 min total**.

---

## 8. Preflight ingest results (2-hour smoke)

| Instrument | Window | Fetched | Upserted | Status |
|------------|--------|---------|----------|--------|
| BTC_USD | 2026-05-31T21:57:35Z → 23:57:35Z | 118 | 118 | PASS |
| ETH_USD | 2026-05-31T21:57:36Z → 23:57:36Z | 118 | 118 | PASS |

Idempotency re-run (BTC, same window):

- Second run: fetched 118, upserted 118
- Row count in window after re-run: **118** (not 236) — upsert replaces, no duplicates

Manifests written to `research/crypto/manifests/` (preflight batches; full backfill will produce separate manifests).

---

## 9. Rate-limit/retry behavior

| Control | Setting |
|---------|---------|
| Max candles/request | 300 |
| Inter-request delay | 100 ms |
| Retry | 3 attempts, exponential backoff 1–8 s on HTTP errors |
| Chunk walk | Forward in time |

Observed: no 429 errors during preflight. Full backfill estimated ~17,540 total API calls.

---

## 10. Known risks

| Risk | Mitigation |
|------|------------|
| Coinbase rate limiting on ~17k requests | 100 ms delay; tenacity retry; stop safely on persistent 429 |
| Long runtime (~30–60 min) | Run sequentially per instrument; capture elapsed time |
| Exchange-side gaps in 5y history | Report in validation; do not interpolate; human review if coverage 99.5–100% |
| Postgres upsert volume (~5.2M rows) | Batch upsert via existing store; local disk ~1 GB |
| Pilot overlap | Idempotent upsert handles overlap with 7-day pilot data |
| D1 zero until full window | Expected; D1 materializes after complete UTC days exist |

---

## 11. Confirmed checks

| Check | Result |
|-------|--------|
| Chunking behavior | 300-bar chunks, 8,770 for 5y ✓ |
| Idempotent upsert | Re-run produces same row count ✓ |
| Manifests under `research/crypto/manifests/` | ✓ |
| No raw data export staged | ✓ (git status clean except manifests) |
| Postgres destination/schema | ✓ |
| Public endpoints only | ✓ |

---

## 12. Go/no-go

**GO** — Proceed with full 5y M1 backfill for BTC_USD then ETH_USD.
