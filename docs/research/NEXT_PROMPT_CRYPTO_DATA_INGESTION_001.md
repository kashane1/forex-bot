# Next Prompt — Crypto Data Ingestion Sprint 001

**Status:** EXECUTED · see [`active/crypto_programme/CRYPTO_DATA_INGESTION_001_SUMMARY.md`](active/crypto_programme/CRYPTO_DATA_INGESTION_001_SUMMARY.md)

---

## Context

Forex programme archived. Crypto data design complete (Coinbase spot primary, BTC/USD + ETH/USD only). This sprint implements ingestion and validation scripts per the design docs — **no factor diagnostics, campaigns, or strategies**.

See:
- [`active/crypto_programme/CRYPTO_DATA_DESIGN_001_SUMMARY.md`](active/crypto_programme/CRYPTO_DATA_DESIGN_001_SUMMARY.md)
- [`active/crypto_programme/CRYPTO_DATA_INGESTION_PLAN.md`](active/crypto_programme/CRYPTO_DATA_INGESTION_PLAN.md)
- [`CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md`](CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md)

---

## Goal

Implement minimal BTC/USD and ETH/USD spot M1 ingestion into Postgres, materialize derived timeframes, validate data quality, and produce a pilot backfill — without creating factors, strategies, or campaigns.

---

## Hard rules

- Do **not** create factors, strategies, or campaigns
- Do **not** run factor validation or front-gate screens
- Do **not** approve any strategy
- Do **not** enable paper/demo/live
- Do **not** call broker/trading APIs (market-data endpoints only)
- Do **not** commit secrets, raw databases, or bulky artifacts
- Keep `configs/approved_strategies.yaml` empty
- Work on `main` only; commit after each meaningful phase
- Pilot backfill first (7 days M1); full 5y backfill only after pilot validation passes

---

## The prompt

> We are starting the cryptocurrency data ingestion sprint on `main`.
>
> **PHASE 0 — baseline**
> 1. Verify freeze gate passes.
> 2. Create `docs/research/active/crypto_programme/CRYPTO_DATA_INGESTION_001_PLAN.md`.
> 3. Commit.
>
> **PHASE 1 — registry and store**
> 1. Add `research/crypto/registry.py` with canonical instruments and venue symbols.
> 2. Extend Postgres candle store / instrument registry for crypto if needed.
> 3. Tests for registry and instrument mapping.
> 4. Commit.
>
> **PHASE 2 — ingest script**
> 1. Implement `scripts/ingest_crypto_candles_postgres.py` (Coinbase public candles, chunked, idempotent).
> 2. Write batch manifests under `research/crypto/manifests/`.
> 3. Unit tests with mocked HTTP responses.
> 4. Commit.
>
> **PHASE 3 — validation and materialization**
> 1. Implement `scripts/validate_crypto_store.py` per validation requirements.
> 2. Wire M1 → M5/M15/H1/H4/D1 materialization (reuse forex patterns).
> 3. Commit.
>
> **PHASE 4 — pilot backfill**
> 1. Run 7-day M1 pilot for BTC_USD and ETH_USD (local Postgres only; gitignore data).
> 2. Document results in `CRYPTO_DATA_INGESTION_001_PILOT_RESULT.md`.
> 3. Commit docs only (no raw candle dumps).
>
> **PHASE 5 — summary**
> 1. Run full test suite + freeze gate.
> 2. Create `CRYPTO_DATA_INGESTION_001_SUMMARY.md`.
> 3. Commit.

---

## Success criteria

- Ingest + validate scripts exist and are tested
- Pilot backfill documented; validation gates pass on pilot window
- No strategy/campaign/factor artifacts
- `approved: []` unchanged
- Freeze gate passes
