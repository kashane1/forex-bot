# Next Prompt — Crypto Data Design Sprint 001

**Sprint type:** Data design only. Not a strategy sprint.
**Branch:** `main` — work directly on main; do not create a branch or worktree.
**Prerequisite:** `FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md` reviewed (brief review OK; do not execute cleanup yet)
**Date authored:** 2026-05-31

---

## Context

The forex strategy-search programme is complete and archived. The next programme targets cryptocurrency research with a minimal universe: **BTC/USD and ETH/USD only**. No altcoins. No strategy work until data infrastructure is designed and validated.

See:
- `docs/research/FOREX_PROGRAMME_FINAL_STATE.md`
- `docs/research/CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md`
- `docs/research/FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md`

---

## Goal

Design minimal BTC/USD and ETH/USD data schema, choose source options, document requirements, and produce a data ingestion plan — **without ingesting large datasets or creating factors/strategies/campaigns**.

---

## Hard rules

- Do **not** create factors, strategies, or campaigns
- Do **not** run factor validation or front-gate screens
- Do **not** approve any strategy
- Do **not** enable paper/demo/live
- Do **not** call broker/trading APIs
- Do **not** ingest large datasets until source, schema, and cost-model decisions are written down
- Do **not** commit secrets, raw databases, or bulky artifacts
- Keep `configs/approved_strategies.yaml` empty
- Work on `main` only; do not create a branch or worktree
- Commit after each meaningful phase

---

## The prompt

> We are starting the cryptocurrency data design sprint on `main`.
>
> Work directly on main. Do not create a branch or worktree. Commit after each meaningful phase.
>
> **Context:** The forex programme is archived (no approved strategies). The cleanup proposal has been reviewed; do not execute archive cleanup in this sprint. The crypto programme roadmap (`CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md`) specifies BTC/USD + ETH/USD, spot-first, with futures/funding hooks for later. Stage 1 is data design only — no ingestion of large datasets until source, schema, and cost-model decisions are documented.
>
> **Goal:** Produce a complete data ingestion plan for BTC/USD and ETH/USD spot OHLCV that reuses existing ingestion abstractions where possible.
>
> ---
>
> **PHASE 0 — baseline audit**
>
> 1. Verify branch, working tree, freeze gate (`python scripts/check_research_freeze.py`).
> 2. Inspect existing data ingestion abstractions:
>    - `scripts/ingest_oanda_candles_postgres.py`, `scripts/ingest_oanda_m1_candles.py`
>    - `scripts/prepare_local_research_data.py`, `scripts/export_postgres_research_candles.py`
>    - `research/` data store patterns, provenance JSON conventions
>    - `docs/research/` data provenance docs from forex programme
> 3. Create `docs/research/CRYPTO_DATA_DESIGN_001_PLAN.md` with phases, safety rules, deliverables.
> 4. Commit.
>
> **PHASE 1 — source evaluation**
>
> 1. Evaluate free/low-cost data source options for BTC/USD and ETH/USD spot OHLCV:
>    - Exchange APIs (Coinbase, Binance, Kraken, etc.) — document rate limits, history depth, bid/ask availability
>    - Aggregator APIs (CryptoCompare, CoinGecko, etc.)
>    - Public datasets (Kaggle, academic)
> 2. Document trade-offs: cost, history depth, granularity, reliability, licensing, bid/ask vs mid-only.
> 3. Create `docs/research/CRYPTO_DATA_SOURCE_EVALUATION.md`.
> 4. Commit.
>
> **PHASE 2 — schema design**
>
> 1. Design minimal canonical schema for BTC/USD and ETH/USD:
>    - Symbol mapping conventions
>    - OHLCV fields (open, high, low, close, volume)
>    - Timestamp (UTC), timezone policy
>    - Bid/ask or spread proxy fields
>    - Provenance metadata (source, fetch_time, version)
>    - Gap/missing-bar policy
> 2. Define materialized timeframe requirements: 1m base → 5m, 15m, 1h, 4h, 1d
> 3. Design hooks for future futures/funding/OI fields (schema only, no data)
> 4. Create `docs/research/CRYPTO_DATA_SCHEMA.md`.
> 5. Commit.
>
> **PHASE 3 — cost and provenance requirements**
>
> 1. Define cost model assumptions for crypto (maker/taker fees, spread, slippage proxy)
> 2. Define provenance and reproducibility requirements (match forex programme standards)
> 3. Define minimum historical depth (5y minimum, 10y desirable for BTC)
> 4. Define validation checks (gap detection, outlier bounds, cross-venue consistency)
> 5. Create `docs/research/CRYPTO_DATA_VALIDATION_REQUIREMENTS.md`.
> 6. Commit.
>
> **PHASE 4 — ingestion plan**
>
> 1. Produce end-to-end ingestion plan reusing existing abstractions where feasible
> 2. Document spot-first vs futures-later decision
> 3. Identify what code changes would be needed (plan only, minimal implementation)
> 4. Estimate storage requirements (do not ingest yet)
> 5. Create `docs/research/CRYPTO_DATA_INGESTION_PLAN.md`.
> 6. Commit.
>
> **PHASE 5 — validation and summary**
>
> 1. Run: `pytest tests/ -q`, `python scripts/check_research_freeze.py`, `python scripts/validate_research_archive.py`
> 2. Verify: no factors, strategies, campaigns created; `approved: []`; no large data committed
> 3. Create `docs/research/CRYPTO_DATA_DESIGN_001_SUMMARY.md`.
> 4. Commit.
>
> ---
>
> **Deliverables:**
> - `CRYPTO_DATA_DESIGN_001_PLAN.md`
> - `CRYPTO_DATA_SOURCE_EVALUATION.md`
> - `CRYPTO_DATA_SCHEMA.md`
> - `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md`
> - `CRYPTO_DATA_INGESTION_PLAN.md`
> - `CRYPTO_DATA_DESIGN_001_SUMMARY.md`
>
> **Success criteria:**
> - Complete data design documented
> - Source options evaluated with trade-offs
> - Schema supports spot-first + futures hooks
> - No strategy, campaign, or factor work
> - No large data ingestion without authorization
> - Freeze gate still passes

---

## Operator notes

- This sprint produces documentation and minimal schema stubs only.
- Actual ingestion is a separate sprint after operator review and authorization.
- First factor family after data validation will be Family C (Trend Persistence) per the crypto roadmap — not MTF confluence. If raw persistence is not worth testing, MTF confluence is unlikely to add edge.
