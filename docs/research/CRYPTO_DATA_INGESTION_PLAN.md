# Crypto Data — Ingestion Plan (Phase 4)

**Sprint:** `crypto-data-design-001` · Phase 4
**Date:** 2026-05-31
**Type:** Plan only. No ingestion executed.

---

## 1. Spot-first vs futures-later

| Phase | Scope |
|-------|-------|
| **Ingestion v1** | Coinbase spot `BTC-USD`, `ETH-USD` → canonical `BTC_USD`, `ETH_USD` |
| **Ingestion v1b** | Optional Binance USDT cross-venue sample (not dual canonical) |
| **Later** | Perpetual OHLCV, funding rates, open interest (Family E) |

Futures does **not** block v1. Schema hooks documented in `CRYPTO_DATA_SCHEMA.md`.

---

## 2. End-to-end pipeline (proposed)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ Coinbase REST   │────▶│ ingest_crypto_   │────▶│ Postgres            │
│ candles (M1)    │     │ candles.py       │     │ market_data.candles │
└─────────────────┘     └──────────────────┘     └──────────┬──────────┘
                                                              │
┌─────────────────┐     ┌──────────────────┐                  │
│ materialize_    │◀────│ validate_crypto_ │◀─────────────────┘
│ crypto_tfs.py   │     │ store.py         │
└────────┬────────┘     └──────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│ M5,M15,H1,H4,D1 │────▶│ export +         │
│ in Postgres     │     │ provenance.json  │
└─────────────────┘     └──────────────────┘
```

### Step 0 — Operator authorization

Require sign-off on:

- `CRYPTO_DATA_SOURCE_EVALUATION.md`
- `CRYPTO_DATA_SCHEMA.md`
- `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md`
- This plan

### Step 1 — Registry module

**New:** `research/crypto/registry.py`

```python
CANONICAL_INSTRUMENTS = ("BTC_USD", "ETH_USD")
VENUE_SYMBOLS = {"BTC_USD": "BTC-USD", "ETH_USD": "ETH-USD"}
PRIMARY_VENUE = "coinbase"
```

### Step 2 — Ingestion script

**New:** `scripts/ingest_crypto_candles_postgres.py`

Pattern from `scripts/ingest_oanda_candles_postgres.py`:

| Feature | Behavior |
|---------|----------|
| Args | `--instrument BTC_USD`, `--granularity M1`, `--start`, `--end` (required) |
| Chunking | Max N candles per request (venue limit); walk forward in time |
| Retry | httpx + tenacity on 429/5xx with backoff |
| Complete only | Exclude incomplete trailing bar |
| Output | Upsert via `PostgresCandleStore` |
| Manifest | Write `research/crypto/manifests/{batch_id}.json` |
| Blocked | Exit `BLOCKED` if Postgres not configured (same as OANDA path) |
| Credentials | Public endpoints: no key; optional API key from env for higher limits |

**No broker/trading endpoints.** Market data only.

### Step 3 — Validation script

**New:** `scripts/validate_crypto_store.py`

- Gap report
- OHLC invariants
- Coverage ratio vs expected bar count
- Optional sha256 export vs sidecar

### Step 4 — Materialization

**New:** `scripts/materialize_crypto_derived_timeframes.py`

- Wrap existing `m1_timeframe_materialization.materialize_pair`
- Targets: M5, M15, H1, H4, D1 (add D1 to supported targets if missing)
- Output manifest to `research/crypto/materialization/`

### Step 5 — Export (optional)

**New:** `scripts/export_crypto_research_candles.py`

- Mirror `export_postgres_research_candles.py` / Lean parity CSV layout
- Gitignored bulk under `research/crypto/exports/`
- Committed provenance sidecars only

### Step 6 — Orchestrator

**New:** `scripts/prepare_crypto_research_data.py`

Mirror `prepare_local_research_data.py`:

1. ingest M1 (if authorized)
2. validate store
3. materialize derived TFs
4. export + provenance
5. `check_research_freeze.py`

`--dry-run` prints plan only.

---

## 3. Code reuse vs new modules

| Component | Reuse | New work |
|-----------|-------|----------|
| `PostgresCandleStore` / `CandleRecord` | ✓ extend | `asset_class` column optional |
| `get_research_database_config` | ✓ | |
| Chunked HTTP ingest pattern | ✓ pattern | Coinbase response parser |
| `m1_timeframe_materialization` | ✓ core logic | D1 target; crypto pair list |
| Provenance sidecar format | ✓ pattern | crypto-specific fields |
| OANDA-specific guards | ✗ | Do not call OANDA scripts |
| Factor / campaign code | ✗ | Out of scope |

**Estimated new code (implementation sprint):** ~400–600 lines across registry, ingest, validate, materialize wrapper, tests.

---

## 4. Storage estimates (not ingested)

Assumptions: 2 instruments, M1 base, 5y history.

| Metric | BTC | ETH | Total |
|--------|-----|-----|-------|
| M1 bars (5y) | ~2.6M | ~2.6M | ~5.2M |
| Row size (Postgres, mid+metadata) | ~200 B | ~200 B | |
| Raw M1 storage | ~520 MB | ~520 MB | **~1.0 GB** |
| Derived (M5–D1) | ~30% of M1 | | **~300 MB** |
| **Total Postgres (5y, 2 assets)** | | | **~1.3 GB** |

10y BTC-only M1: ~2 GB additional.

**Git:** zero bulk — all data local/gitignored. Committed artifacts: manifests + provenance JSON only (<100 KB).

---

## 5. Ingestion sequence (authorized sprint)

| Order | Task | Window |
|-------|------|--------|
| 1 | Pilot: BTC_USD M1, 7 days | Smoke test |
| 2 | Validate pilot | Gate |
| 3 | BTC_USD M1 full 5y | Chunked backfill |
| 4 | ETH_USD M1 full 5y | Chunked backfill |
| 5 | Materialize M5–D1 both | |
| 6 | Cross-venue sample (Kraken/Binance), 30d | Validation CSV only |
| 7 | Full validation report | Operator review |
| 8 | **Then** Family C exploratory diagnostics | Separate sprint |

**Rate-limit budget (Coinbase):** implement conservative 100ms inter-request delay; adjust from response headers.

**Binance backfill (optional):** only if Coinbase gaps exceed 0.5% — fill gaps from secondary source with gap-fill flag in provenance.

---

## 6. Environment and secrets

| Variable | Purpose |
|----------|---------|
| `RESEARCH_DATABASE_URL` | Postgres (existing) |
| `COINBASE_API_KEY` | Optional; public candles may not require |
| `COINBASE_API_SECRET` | Optional |

Never commit. Document in runbook stub only.

---

## 7. Tests (implementation sprint)

| Test | Scope |
|------|-------|
| `test_crypto_registry.py` | Symbol mapping |
| `test_parse_coinbase_candles.py` | Fixture JSON → CandleRecord |
| `test_crypto_gap_report.py` | Synthetic gaps detected |
| Integration | Blocked without Postgres (same pattern as OANDA ingest tests) |

---

## 8. Explicit out of scope

- Factor construction (Family C)
- Campaigns / front gates
- Live trading loops
- Perpetual/funding ingestion
- Large data commit to git

---

## Related documents

- `CRYPTO_DATA_DESIGN_001_PLAN.md`
- `CRYPTO_DATA_SOURCE_EVALUATION.md`
- `CRYPTO_DATA_SCHEMA.md`
- `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md`
- `CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md` — Stage 2 / Family C sequencing
