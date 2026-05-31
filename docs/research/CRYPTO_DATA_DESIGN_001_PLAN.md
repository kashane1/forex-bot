# Crypto Data Design Sprint 001 — Plan (Phase 0)

**Sprint:** `crypto-data-design-001`
**Branch:** `main` (no branch or worktree)
**Date:** 2026-05-31
**Type:** Documentation only. No data ingestion, no factors, no campaigns.

---

## Purpose

Design minimal BTC/USD and ETH/USD spot data infrastructure before any cryptocurrency factor diagnostics. Produce source evaluation, canonical schema, validation requirements, and an ingestion plan that reuses existing forex research patterns where feasible.

**Prerequisite:** Forex archive cleanup proposal reviewed; cleanup **not** executed in this sprint.

**Next programme step after this sprint:** authorized data ingestion sprint (separate, operator-approved).

**First factor family (after data validation):** Family C — Trend Persistence. Not MTF confluence.

---

## Non-goals

- No factor validation, front gates, campaigns, or strategies
- No approval changes; `configs/approved_strategies.yaml` stays empty
- No paper/demo/live enablement
- No broker/trading API calls (design references public market-data APIs only)
- No ingestion of large datasets until source, schema, and cost-model decisions are written (Phases 1–3)
- No forex archive cleanup execution

---

## Safety rules

1. Research freeze intact — run `python scripts/check_research_freeze.py` at Phase 0 and Phase 5.
2. Work on `main` only; commit after each meaningful phase.
3. No secrets, raw databases, or bulky artifacts committed.
4. Documentation and optional minimal schema stubs only — no production ingestion code required in this sprint.

---

## Baseline audit — existing forex abstractions

### Postgres candle store (`src/forex_bot/data/postgres_candle_store.py`)

- Schema: `market_data.instruments`, `market_data.candles`
- `CandleRecord`: instrument, granularity, time_utc, complete, volume, bid/ask/mid OHLC, spread_*, source, fetch_batch_id, data_hash, fetched_at_utc
- Primary key: `(instrument, granularity, time_utc)`
- Idempotent upsert with keep-last semantics
- **Reusable for crypto:** schema pattern, provenance fields, chunking/resume discipline

### OANDA ingestion (`scripts/ingest_oanda_candles_postgres.py`, `scripts/ingest_oanda_m1_candles.py`)

- Chunked HTTP fetch with retry, complete-candles-only filter
- Requires `--start` / `--end`; never unbounded history
- Writes manifest JSON per batch; credentials from env (never committed)
- **Reusable pattern:** chunk loop, batch ID, blocked-without-credentials guard

### Materialization (`scripts/materialize_m1_derived_timeframes.py`, `src/forex_bot/data/m1_timeframe_materialization.py`)

- M1 → M5, M15, H1, H4 (plus diagnostic M3, M30)
- Aggregation config hash for reproducibility
- Verification pass after materialization
- **Reusable for crypto:** same M1-base → higher-TF pipeline; extend granularity set to include D1

### Local data orchestration (`scripts/prepare_local_research_data.py`)

- Ordered, guarded pipeline with `--dry-run`
- Refuses live environment
- **Reusable pattern:** orchestrator with explicit steps and final freeze gate

### Provenance conventions (forex programme)

- Sidecar JSON: `rate_provenance.json`, `*.provenance.json` (Lean parity)
- Fields: source, fetch window, series mapping, hashes, attribution
- Committed small artifacts under `docs/research/`; bulk data gitignored
- **Reusable for crypto:** same sidecar + manifest pattern under `research/crypto/`

### Research freeze / archive validation

- `scripts/check_research_freeze.py`, `scripts/validate_research_archive.py`
- Unchanged by this sprint; must pass at end

---

## Phases and deliverables

| Phase | Deliverable | Commit |
|-------|-------------|--------|
| 0 | This plan | Yes |
| 1 | `CRYPTO_DATA_SOURCE_EVALUATION.md` | Yes |
| 2 | `CRYPTO_DATA_SCHEMA.md` | Yes |
| 3 | `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md` | Yes |
| 4 | `CRYPTO_DATA_INGESTION_PLAN.md` | Yes |
| 5 | `CRYPTO_DATA_DESIGN_001_SUMMARY.md` + validation | Yes |

---

## Validation commands (Phase 5)

```bash
pytest tests/ -q
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
git status --short
grep "^approved:" configs/approved_strategies.yaml
```

---

## Success criteria

- Source, schema, cost model, and validation requirements documented
- Ingestion plan identifies code reuse vs new modules
- Storage estimate provided; no large data committed
- Freeze gate passes
- No strategy, campaign, or factor work created
