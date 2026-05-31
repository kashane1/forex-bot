# Crypto Full Backfill and Canonical Dataset Sprint 001 — Plan

**Sprint:** `crypto-full-backfill-and-canonical-dataset-001`
**Date:** 2026-05-31
**Branch:** `main` (direct work, no feature branch)
**Type:** Data sprint only — ingestion, validation, materialization, readiness gate

---

## 1. Purpose

Run the authorized full historical Coinbase spot M1 backfill for `BTC_USD` and `ETH_USD`, validate the canonical crypto dataset against design requirements, materialize derived timeframes (M5/M15/H1/H4/D1), freeze the spot cost model, and determine whether the dataset is ready for Family C Trend Persistence diagnostics.

Builds on the accepted 7-day pilot documented in `CRYPTO_DATA_INGESTION_001_PILOT_RESULT.md`.

---

## 2. Non-goals

| Excluded | Rationale |
|----------|-----------|
| Factor construction | Family C diagnostics is a separate sprint |
| Strategy creation | Research freeze gate |
| Campaign creation | No front-gate runs |
| Family C diagnostics | Blocked until this sprint completes |
| Front-gate runs | Out of scope |
| Strategy approval | `configs/approved_strategies.yaml` must remain empty |
| Paper/demo/live enablement | Trading loops remain frozen |
| Broker/trading API calls | Market-data endpoints only |
| Raw data commit | Bulk data gitignored/local only |
| Cross-venue backfill | Coinbase canonical only in v1 |
| Gap interpolation | Report only; no auto-fix |
| Outlier auto-fix | Quarantine/report only |

---

## 3. Target instruments

| Canonical | Venue symbol | Asset class |
|-----------|--------------|-------------|
| `BTC_USD` | `BTC-USD` | crypto spot |
| `ETH_USD` | `ETH-USD` | crypto spot |

Registry: `research/crypto/registry.py`

---

## 4. Requested window

| Parameter | Value |
|-----------|-------|
| Base granularity | M1 |
| Requested start | `2021-05-31T00:00:00Z` (5 years before sprint run date) |
| Requested end | Current UTC at backfill execution time |
| Minimum history | 5 years for both assets |

Pilot 7-day window (`2026-05-24` → `2026-05-31`) remains in Postgres and will be superseded/extended by the full backfill via idempotent upsert.

---

## 5. Source and endpoint

| Field | Value |
|-------|-------|
| Venue | Coinbase Exchange public REST |
| Source tag | `coinbase-spot` |
| Endpoint | `GET https://api.exchange.coinbase.com/products/{product_id}/candles` |
| Auth | None required (public market data) |
| Granularity param | `60` (M1) |
| Response format | `[time, low, high, open, close, volume]` arrays |

Implementation: `research/crypto/coinbase.py`, `scripts/ingest_crypto_candles_postgres.py`

---

## 6. Expected row counts

Assumptions: 5 calendar years ≈ 1,826 days × 1,440 min/day.

| Instrument | Expected M1 bars (5y) | Approx. API chunks (300/request) |
|------------|----------------------|----------------------------------|
| BTC_USD | ~2,629,440 | ~8,765 |
| ETH_USD | ~2,629,440 | ~8,765 |
| **Total M1** | **~5,258,880** | **~17,530** |

Derived timeframe estimates (both assets combined):

| Timeframe | Approx. rows (5y, complete buckets) |
|-----------|-------------------------------------|
| M5 | ~1,051,776 |
| M15 | ~350,592 |
| H1 | ~87,648 |
| H4 | ~21,912 |
| D1 | ~3,652 |

Postgres storage estimate: ~1.3 GB total (M1 + derived). Local only.

---

## 7. Rate-limit handling

| Control | Setting |
|---------|---------|
| Max candles per request | 300 (`MAX_CANDLES_PER_REQUEST`) |
| Inter-request delay | 100 ms (`REQUEST_DELAY_SECONDS`) |
| Retry policy | tenacity: 3 attempts, exponential backoff 1–8 s on `httpx.HTTPError` |
| Chunk walk | Forward in time via `iter_coinbase_chunks()` |
| Estimated API time | ~15 min per instrument (8765 × 0.1 s) + fetch latency |
| On 429/5xx after retries | Stop safely, document partial state, do not claim gate passed |

If full 5y backfill is blocked by API limits, local DB issues, or rate limits: document blocker and produce largest safe partial backfill summary.

---

## 8. Retry/idempotency plan

| Mechanism | Behavior |
|-----------|----------|
| Upsert key | `(instrument, granularity, time_utc, source)` via `PostgresCandleStore.upsert_candles()` |
| Re-run safety | Re-ingesting same window updates existing rows; no duplicate PK |
| Batch identity | UUID `batch_id` per run; written to manifest and `fetch_batch_id` on records |
| Ingestion run log | `store.record_ingestion_run()` tracks status, counts, errors |
| Partial failure | Exception → manifest status `FAIL`; prior upserts retained |
| Pilot overlap | 7-day pilot data upserted in place; no delete required |

---

## 9. Validation gates

Run `scripts/validate_crypto_store.py` over full requested M1 window per instrument.

| Check | Threshold / action |
|-------|-------------------|
| Timestamp monotonicity | Strictly increasing |
| OHLC invariants | high ≥ max(o,c,l); low ≤ min(o,c,h) |
| Duplicate bars | Zero on PK |
| Coverage | ≥ 99.5% (`actual / expected`) per asset |
| Gap detection | Report all gaps > 1 bar; no interpolation |
| Volume | Non-negative |
| Zero-price bars | Quarantine/report |
| Single-bar return outliers | Flag \|return\| > 20% on M1 |
| Flash wick outliers | Flag (high-low)/mid > 15% |
| Stale flat runs | Flag > 60 consecutive identical closes |

Classification: PASS / WARN / FAIL per instrument. Coverage below 99.5% → FAIL unless exchange-side gap accepted by human review.

Materialization eligibility: M1 validation PASS or WARN with coverage ≥ 99.5%.

Family C eligibility: full backfill complete, M1 coverage accepted, D1 and M15 available, cost model frozen, gap report reviewed, freeze gate passes.

---

## 10. Materialization plan

Script: `scripts/materialize_crypto_derived_timeframes.py`

| Target | Alignment |
|--------|-----------|
| M5, M15, H1, H4, D1 | UTC-aligned buckets; incomplete trailing buckets omitted |

Process:

1. Materialize per instrument after M1 validation passes coverage gate.
2. Targets: `M5,M15,H1,H4,D1` (default).
3. Write manifest to `research/crypto/materialization/{run_id}.json`.
4. Verify row counts, first/last timestamps, no duplicate derived bars.

D1 expected to be non-zero after full 5y window (unlike 7-day pilot where D1 = 0 under omit policy).

---

## 11. Data-not-committed policy

| Committed | Not committed |
|-----------|---------------|
| Sprint plan/result/validation docs | Raw M1 CSV exports |
| Compact batch manifests (`research/crypto/manifests/`) | Postgres dumps |
| Materialization manifests (`research/crypto/materialization/`) | `.env`, API keys |
| Small validation artifacts (`research/crypto/validation/`) if compact | Bulk exports under `research/crypto/exports/` |

All bulk candle data: local Postgres only, gitignored.

---

## 12. Safety rules

- Do not create factors, strategies, or campaigns.
- Do not run Family C diagnostics or front gates.
- Do not approve any strategy.
- Do not enable paper/demo/live.
- Do not call broker/trading APIs — market-data endpoints only.
- Keep `configs/approved_strategies.yaml` empty (`approved: []`).
- Preserve research freeze/archive gates.
- Commit after each meaningful phase.
- Work directly on `main` — no branch or worktree.

---

## 13. Expected deliverables

| Phase | Deliverable |
|-------|-------------|
| 0 | This plan + baseline commit |
| 1 | `CRYPTO_FULL_BACKFILL_001_PREFLIGHT.md` |
| 2 | `CRYPTO_FULL_BACKFILL_001_RESULT.md` + batch manifests |
| 3 | `CRYPTO_CANONICAL_DATASET_VALIDATION_001.md` + validation artifacts |
| 4 | `CRYPTO_DERIVED_TIMEFRAME_MATERIALIZATION_001.md` + materialization manifests |
| 5 | `CRYPTO_COST_MODEL_001.md` |
| 6 | `CRYPTO_FAMILY_C_PREDIAGNOSTIC_READINESS_001.md` |
| 7 | `NEXT_PROMPT_CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001.md` or `NEXT_PROMPT_CRYPTO_DATA_REPAIR_OR_RETRY_001.md` |
| 8 | `CRYPTO_FULL_BACKFILL_AND_CANONICAL_DATASET_001_SUMMARY.md` |

---

## 14. Phase 0 baseline (2026-05-31)

| Check | Result |
|-------|--------|
| Branch | `main` |
| Working tree | Clean |
| Pilot docs | Present; pilot accepted for full 5y backfill |
| Ingestion scripts | `ingest_crypto_candles_postgres.py`, `validate_crypto_store.py`, `materialize_crypto_derived_timeframes.py` |
| Postgres connectivity | PASS (`localhost:5432/forex_bot`) |
| `approved_strategies.yaml` | Empty (`approved: []`) |
| `pytest tests/ -q` | 2471 passed |
| `check_research_freeze.py` | ALL CHECKS PASSED |
| `validate_research_archive.py` | ALL CHECKS PASSED |
| `scan_artifacts_for_secrets.py` | PASSED |
| `ruff check` | 25 pre-existing issues (import sorting E402/I001, unused imports F401 in crypto test modules) — documented, not expanded in this sprint |

Current Postgres state (pilot only): BTC_USD M1 10,043 rows; ETH_USD M1 10,041 rows; derived M5–H1 from pilot materialization.

---

## Related documents

- `CRYPTO_DATA_DESIGN_001_SUMMARY.md`
- `CRYPTO_DATA_INGESTION_001_PILOT_RESULT.md`
- `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md`
- `CRYPTO_DATA_SCHEMA.md`
- `CRYPTO_DATA_INGESTION_PLAN.md`
