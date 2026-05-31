# Crypto Data Design Sprint 001 — Summary (Phase 5)

**Sprint:** `crypto-data-design-001`
**Branch:** `main`
**Date:** 2026-05-31
**Type:** Documentation only. No data ingested.

---

## 1. Branch and commits

| Phase | Commit | Deliverable |
|-------|--------|-------------|
| 0 | `59eddcf` | `CRYPTO_DATA_DESIGN_001_PLAN.md` |
| 1 | `0b8818b` | `CRYPTO_DATA_SOURCE_EVALUATION.md` |
| 2 | `0793938` | `CRYPTO_DATA_SCHEMA.md` |
| 3 | `45675c9` | `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md` |
| 4 | `8347d90` | `CRYPTO_DATA_INGESTION_PLAN.md` |
| 5 | *(this commit)* | `CRYPTO_DATA_DESIGN_001_SUMMARY.md` |

Prior prompt update: `72b8b66` (`NEXT_PROMPT_CRYPTO_DATA_DESIGN_001.md`).

---

## 2. Decisions locked

| Decision | Choice |
|----------|--------|
| Primary source | Coinbase spot `BTC-USD`, `ETH-USD` |
| Secondary source | Binance `BTCUSDT` / `ETHUSDT` (USDT basis documented) |
| Cross-venue check | Kraken sample windows |
| Symbol IDs | `BTC_USD`, `ETH_USD` |
| Spot vs futures | Spot first; perpetual/funding hooks schema-only |
| Base granularity | M1 ingested → M5, M15, H1, H4, D1 materialized |
| Bid/ask | Mid from API; half-spread bps proxy (5 BTC / 8 ETH default) |
| Cost stack | Spread + taker fees (1.2% RT default) + horizon slippage bps |
| Min history | 5y both assets; 10y BTC desirable |
| Storage (5y, 2 assets, M1+derived) | ~1.3 GB Postgres local, gitignored |

---

## 3. Validation results

| Check | Result |
|-------|--------|
| `pytest tests/ -q` | PASS — 2460 |
| `check_research_freeze.py` | PASS |
| `validate_research_archive.py` | PASS |
| `approved_strategies.yaml` | `approved: []` |
| Large data committed | None |
| Factors / campaigns / strategies | None created |
| Forex archive cleanup executed | No |

---

## 4. Code reuse plan

- Extend `PostgresCandleStore` / `CandleRecord` with crypto instruments
- New `scripts/ingest_crypto_candles_postgres.py` (pattern from OANDA ingest)
- Reuse `m1_timeframe_materialization` for derived TFs (+ D1)
- Provenance sidecars match forex Lean/FRED conventions
- Orchestrator: `prepare_crypto_research_data.py` with `--dry-run`

---

## 5. Next steps (operator)

1. Review this summary and Phase 1–4 documents
2. **Authorize ingestion sprint** (explicit operator OK required)
3. Implement registry + ingest + validate scripts (~400–600 LOC)
4. Pilot 7-day M1 backfill → full 5y backfill
5. Run validation gate from `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md`
6. **Only then:** Family C (Trend Persistence) exploratory diagnostics — not MTF confluence

---

## 6. Files to review first

1. `CRYPTO_DATA_SOURCE_EVALUATION.md` — source choice rationale
2. `CRYPTO_DATA_SCHEMA.md` — field definitions and futures hooks
3. `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md` — cost model and gates
4. `CRYPTO_DATA_INGESTION_PLAN.md` — implementation sequence and storage
5. `CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md` — programme context

---

## 7. Safety confirmations

| Item | Status |
|------|--------|
| Research freeze intact | ✓ |
| Paper/demo/live blocked | ✓ |
| No broker trading APIs called | ✓ |
| No secrets committed | ✓ |
| No bulky data committed | ✓ |
| Forex cleanup not executed | ✓ |
