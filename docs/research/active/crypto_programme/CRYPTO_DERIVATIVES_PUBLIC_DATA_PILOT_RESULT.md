# Crypto Derivatives — Public Data Pilot Result (Family E Prep, Phase 5)

**Sprint:** `crypto-family-e-derivatives-data-prep-001` · Phase 5
**Date:** 2026-06-02
**Type:** Tiny public-data pilot. No factor, no campaign, no strategy, no edge inference.

---

## 1. Summary

A tiny BTC + ETH derivatives pilot **succeeded** using **OKX public market data** after the primary hierarchy (Binance, Bybit) was geo-blocked from this host. Funding-rate history (BTC + ETH) and a BTC open-interest snapshot were fetched, parsed, and validated **PASS** with no credentials and no trading endpoints.

## 2. Source selection at runtime (honest substitution)

The Phase 1 hierarchy is Binance USDⓈ-M → Bybit → Kraken Futures, with documented failover. At runtime from this host:

| Venue | Endpoint probed | Result |
|-------|-----------------|--------|
| Binance USDⓈ-M | `/fapi/v1/fundingRate` | **HTTP 451** (Unavailable For Legal Reasons — geo-blocked) |
| Bybit v5 | `/v5/market/funding/history` | **HTTP 403** (Forbidden — geo-blocked) |
| Kraken Futures | `/derivatives/api/v3/historicalfundingrates?symbol=PI_XBTUSD` | HTTP 404 (reachable; path/symbol stale — `v3 PI_*` deprecated, now `v4 PF_*`) |
| **OKX v5** | `/api/v5/public/funding-rate-history` | **HTTP 200 — used** |
| Deribit | `/public/get_funding_rate_history` | HTTP 200 (reachable; continuous-funding model, not pooled) |

**No VPN / geo-evasion was used.** The geo-block is recorded as a real-world constraint. OKX was the cleanest reachable venue with an 8h funding model compatible with the canonical schema.

## 3. Commands run

```
python scripts/ingest_crypto_derivatives_public_data.py \
  --source okx --instrument BTC_PERP_USD --data-class funding --limit 30 --execute-public-fetch
python scripts/ingest_crypto_derivatives_public_data.py \
  --source okx --instrument ETH_PERP_USD --data-class funding --limit 30 --execute-public-fetch
python scripts/ingest_crypto_derivatives_public_data.py \
  --source okx --instrument BTC_PERP_USD --data-class open_interest --execute-public-fetch
```

All other fetches default to **dry-run**; the real fetch happened only behind `--execute-public-fetch`.

## 4. Data fetched and validation

| Instrument | Native symbol | Class | Rows | UTC window | Cadence | Validation |
|------------|---------------|-------|------|------------|---------|------------|
| `BTC_PERP_USD` | `BTC-USDT-SWAP` | funding | 30 | 2026-05-23T16:00 → 2026-06-02T08:00 | 8h | **PASS** (0 issues) |
| `ETH_PERP_USD` | `ETH-USDT-SWAP` | funding | 30 | 2026-05-23T16:00 → 2026-06-02T08:00 | 8h | **PASS** (0 issues) |
| `BTC_PERP_USD` | `BTC-USDT-SWAP` | open_interest | 1 | 2026-06-02 snapshot | snapshot | **PASS** |

Validation ran through the real parsers (`parse_okx_funding`, `parse_okx_open_interest`) and helpers (`validate_funding`, `validate_open_interest`): BTC/ETH-only ✓, monotonic ✓, no duplicates ✓, 8h cadence consistent ✓, no extreme-outlier flags ✓. Overall **PASS**.

Funding sanity (informational only, **not** a signal): rates clustered near +0.0001 (1 bp / 8h) with occasional small negatives — typical mild-contango perp funding. **Quote currency is USDT**, flagged non-interchangeable with USD without basis adjustment.

## 5. Basis diagnostics

**Deferred.** Basis requires aligned perp OHLCV + spot, and the USDT-quoted OKX perp vs USD-quoted Coinbase spot would confound basis with USDT/USD. The basis computation path (`compute_basis`, `basis_computable`) is implemented and unit-tested, but no basis series was materialized in the pilot. No factor diagnostic was run.

## 6. Raw-data location policy

- Raw OKX responses written to `research/crypto/derivatives/raw/` — **gitignored**, local-only.
- Committed: the 3 compact manifests (`research/crypto/derivatives/manifests/*.json`) with repo-relative raw-path references; no raw payloads, no absolute machine paths, no credentials.

## 7. Is full backfill ready?

**Partially.** The pipeline (resolve → fetch → parse → validate → manifest) works end-to-end on OKX. Before a full Family E backfill:

1. Decide canonical venue under the geo constraint — OKX (USDT) is reachable here; Binance/Bybit are not. A USD-quoted reference (Kraken `v4`/`PF_*`, or Deribit) should be added for the USDT-vs-USD check.
2. Add OKX perp-OHLCV + mark/index endpoints (only funding + OI are wired for execute today).
3. Confirm OKX funding pagination depth for multi-year history (`before`/`after` ts paging).
4. Resolve the open-interest **history** gap (OKX gives current snapshot; Bybit history is geo-blocked here) — forward-collection may be the only free path.
5. Bind a canonical store (reuse Postgres vs parquet) — deferred from this sprint.

## 8. No-strategy / no-campaign / no-approval statement

This pilot created **no** strategy, campaign, front gate, or approval. It ran **no** factor diagnostic and inferred **no** edge. No trading, order, account, or private API was used; no API key was required or present. BTC and ETH perps only. `configs/approved_strategies.yaml` remains empty; paper/demo/live remain blocked.
