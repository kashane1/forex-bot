# Crypto Data Ingestion Sprint 001 — Pilot Result (Phase 4)

**Sprint:** `crypto-data-ingestion-001` · Phase 4
**Date:** 2026-05-31
**Window:** 7-day M1 pilot ending 2026-05-31T23:11Z

---

## Pilot configuration

| Parameter | Value |
|-----------|-------|
| Source | Coinbase Exchange public REST (`coinbase-spot`) |
| Instruments | `BTC_USD`, `ETH_USD` |
| Granularity | M1 |
| Start (UTC) | 2026-05-24T23:11Z |
| End (UTC) | 2026-05-31T23:11Z |
| Storage | Local Postgres (`FOREX_BOT_RESEARCH_DATABASE_URL`) |

---

## Ingestion results

| Instrument | Fetched | Upserted | Batch manifest |
|------------|---------|----------|----------------|
| BTC_USD | 10,043 | 10,043 | `research/crypto/manifests/7c05a4c2-3cb9-411e-ae6e-5ff1a94e28d1.json` |
| ETH_USD | 10,041 | 10,041 | `research/crypto/manifests/3add769b-f73b-4dc0-b4eb-1e2d08826d37.json` |

Both runs: `status: PASS`.

---

## Validation results

| Instrument | Expected bars | Actual | Coverage | Gaps | Status |
|------------|---------------|--------|----------|------|--------|
| BTC_USD | 10,081 | 10,043 | 99.62% | 37 | WARN |
| ETH_USD | 10,081 | 10,041 | 99.60% | 39 | WARN |

Coverage exceeds the 99.5% gate. Gap warnings reflect exchange-side missing minutes at window edges and brief feed gaps — documented, not interpolated.

---

## Materialization results

UTC-aligned derived timeframes materialized for both instruments:

| Target | BTC rows | ETH rows | Notes |
|--------|----------|----------|-------|
| M5 | 1,979 | 1,977 | PASS |
| M15 | 635 | 633 | PASS |
| H1 | 132 | 130 | PASS |
| H4 | 9 | 8 | PASS |
| D1 | 0 | 0 | Expected — 7-day window too short for complete UTC D1 buckets under omit policy |

Manifests: `research/crypto/materialization/5c86c7e3-*.json`, `55dcc3dd-*.json`

---

## Decision

**Pilot accepted for full 5y backfill authorization.** M1 ingest, validation, and M5–H4 materialization behave as designed. D1 materialization deferred to full-window backfill.

---

## Next step

Operator may authorize full 5y M1 backfill sprint (separate from this sprint's scope).
