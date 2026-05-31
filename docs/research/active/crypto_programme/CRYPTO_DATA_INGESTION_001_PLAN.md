# Crypto Data Ingestion Sprint 001 — Plan (Phase 0)

**Sprint:** `crypto-data-ingestion-001`
**Branch:** `main`
**Date:** 2026-05-31
**Type:** Ingestion infrastructure + pilot backfill. No factors, campaigns, or strategies.

---

## Purpose

Implement Coinbase spot M1 ingestion for `BTC_USD` and `ETH_USD` into the existing Postgres research store, validate data quality, materialize derived timeframes, and run a 7-day pilot backfill.

Design locked in `CRYPTO_DATA_DESIGN_001_SUMMARY.md`.

---

## Non-goals

- No factor validation, front gates, campaigns, or strategies
- No approval changes (`approved: []` stays empty)
- No paper/demo/live enablement
- No broker/trading API calls (market-data only)
- No full 5y backfill in this sprint (pilot only)
- No bulky data committed to git

---

## Phases

| Phase | Deliverable |
|-------|-------------|
| 0 | This plan; freeze gate PASS |
| 1 | `research/crypto/registry.py`, `crypto_pairs.py`, materialization hooks, tests |
| 2 | `scripts/ingest_crypto_candles_postgres.py`, manifests, tests |
| 3 | `scripts/validate_crypto_store.py`, `scripts/materialize_crypto_derived_timeframes.py` |
| 4 | 7-day M1 pilot + `CRYPTO_DATA_INGESTION_001_PILOT_RESULT.md` |
| 5 | `CRYPTO_DATA_INGESTION_001_SUMMARY.md`, full validation |

---

## Safety

Run `python scripts/check_research_freeze.py` at Phase 0 and Phase 5.

---

## Related

- `CRYPTO_DATA_INGESTION_PLAN.md`
- `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md`
- `NEXT_PROMPT_CRYPTO_DATA_INGESTION_001.md`
