# Crypto Derivatives — Canonical Data Model & Provenance (Family E Prep, Phase 2)

**Sprint:** `crypto-family-e-derivatives-data-prep-001` · Phase 2
**Date:** 2026-06-02
**Universe:** BTC and ETH derivatives only. No altcoins.
**Type:** Storage + provenance design. No factor, no campaign, no strategy. Designed **before** ingestion code.

This document extends the spot schema (`CRYPTO_DATA_SCHEMA.md`) with a derivatives layer. It does **not** modify the existing spot `candles` table or any spot diagnostic.

---

## 1. Canonical instrument registry

Spot instruments are unchanged. Derivatives add canonical perp IDs with exchange-native symbols stored **separately** (never overload the canonical ID with a venue symbol).

| Canonical ID | Kind | Underlying spot | Quote convention | Example venue-native symbols |
|--------------|------|-----------------|------------------|------------------------------|
| `BTC_USD` | spot | — | USD | `BTC-USD` (Coinbase) |
| `ETH_USD` | spot | — | USD | `ETH-USD` (Coinbase) |
| `BTC_PERP_USD` | perpetual | `BTC_USD` | USD-denominated (USDT or inverse-USD; recorded per series) | `BTCUSDT` (Binance USDM), `PI_XBTUSD` (Kraken), `BTC-PERPETUAL` (Deribit) |
| `ETH_PERP_USD` | perpetual | `ETH_USD` | USD-denominated | `ETHUSDT` (Binance USDM), `PI_ETHUSD` (Kraken), `ETH-PERPETUAL` (Deribit) |

**Rules**
- Canonical IDs match `^[A-Z]{3,4}_PERP_USD$` (perp) or the existing `^[A-Z]{3,4}_USD$` (spot). Anything else is refused.
- Only `BTC_PERP_USD` and `ETH_PERP_USD` perps are authorized. No third perp, no altcoin perp.
- The `(canonical_id, venue, venue_symbol, quote_ccy)` tuple is the provenance key. `quote_ccy ∈ {USD, USDT}` — `USDT` series are flagged non-interchangeable with `USD` without basis adjustment.

## 2. Logical datasets (tables)

All derivatives tables live in a **`crypto_derivatives` namespace** (logical), separate from spot `candles`, so spot validation/diagnostics are untouched. Implementation may realize these as Postgres tables or as parquet/CSV-backed loaders; the loader interface (Phase 3) is the contract.

### 2.1 `perp_ohlcv`
| Column | Type | Notes |
|--------|------|-------|
| canonical_id | TEXT | `BTC_PERP_USD` / `ETH_PERP_USD` |
| venue | TEXT | `binance-usdm`, `bybit`, `kraken-futures`, … |
| venue_symbol | TEXT | native |
| granularity | TEXT | `M1`,`M5`,`M15`,`H1`,`H4`,`D1` |
| time_utc | TIMESTAMPTZ | **bar open**, UTC |
| open/high/low/close | DOUBLE | perp mid/last per venue |
| volume | NUMERIC | base or contract volume (record unit) |
| quote_ccy | TEXT | `USD`/`USDT` |
| source, fetch_batch_id, data_hash, fetched_at_utc | provenance |
| PK | | `(canonical_id, venue, granularity, time_utc)` |

### 2.2 `funding_rates`
| Column | Type | Notes |
|--------|------|-------|
| canonical_id | TEXT | perp |
| venue | TEXT | |
| venue_symbol | TEXT | |
| funding_time_utc | TIMESTAMPTZ | settlement timestamp (interval **end**, see §3) |
| funding_rate | DOUBLE | signed decimal fraction per interval (e.g. `0.0001` = 1 bp) |
| funding_interval_hours | INT | `8` (Binance/Bybit/OKX/Kraken) or `1` (Deribit realized) |
| mark_price | DOUBLE | nullable; mark at settlement if provided |
| source, fetch_batch_id, data_hash, fetched_at_utc | provenance |
| PK | | `(canonical_id, venue, funding_time_utc)` |

### 2.3 `open_interest`
| Column | Type | Notes |
|--------|------|-------|
| canonical_id | TEXT | perp |
| venue | TEXT | |
| time_utc | TIMESTAMPTZ | snapshot timestamp (interval **end**) |
| interval | TEXT | `5m`,`1h`,`1d`, or `snapshot` |
| open_interest_base | DOUBLE | nullable; OI in base units (contracts→base) |
| open_interest_usd | DOUBLE | nullable; OI in USD notional if provided |
| source, fetch_batch_id, data_hash, fetched_at_utc | provenance |
| PK | | `(canonical_id, venue, interval, time_utc)` |

### 2.4 `mark_index_price`
| Column | Type | Notes |
|--------|------|-------|
| canonical_id | TEXT | perp |
| venue | TEXT | |
| granularity | TEXT | candle TF for mark/index series |
| time_utc | TIMESTAMPTZ | bar open |
| mark_close | DOUBLE | nullable |
| index_close | DOUBLE | nullable (spot composite reference) |
| source, fetch_batch_id, data_hash, fetched_at_utc | provenance |
| PK | | `(canonical_id, venue, granularity, time_utc)` |

### 2.5 `basis` (derived, not fetched)
Computed from perp vs spot; never ingested directly.
| Column | Type | Notes |
|--------|------|-------|
| canonical_id | TEXT | perp |
| spot_instrument | TEXT | `BTC_USD`/`ETH_USD` |
| perp_venue, spot_venue | TEXT | provenance of both legs |
| granularity | TEXT | aligned TF |
| time_utc | TIMESTAMPTZ | bar open |
| perp_close, spot_close | DOUBLE | inputs |
| basis_abs | DOUBLE | `perp_close − spot_close` |
| basis_bps | DOUBLE | `1e4 × (perp_close − spot_close) / spot_close` |
| compute_config_hash | TEXT | reproducibility |
| PK | | `(canonical_id, perp_venue, spot_venue, granularity, time_utc)` |

### 2.6 `provenance` / `fetch_manifests`
Per-fetch manifest (compact, committed): see §6 and Phase 4 validation policy. Records source, endpoint category, instrument, native+canonical symbol, window, rows fetched/inserted/skipped, fetch time UTC, data hash, and local raw path (path string only; the file itself is never committed).

## 3. Timestamp policy

- **UTC only**, throughout storage and APIs. No session fields (continuous market).
- **OHLCV / mark / index:** `time_utc` = **bar open**, UTC-aligned (match spot convention).
- **Funding:** `funding_time_utc` = **settlement timestamp** = the **end** of the funding interval the rate applies to. `funding_interval_hours` records the cadence. 8h venues settle at 00:00/08:00/16:00 UTC (venue-specific); Deribit's hourly-realized series is flagged distinct and never pooled with 8h venues without normalization.
- **Open interest:** `time_utc` = **end** of the OI sampling interval (the snapshot instant). `interval` records the cadence.
- **Basis:** inherits the OHLCV bar-open alignment of its inputs; both legs must share the same `time_utc` bucket.
- All venue epoch-millisecond timestamps are converted to timezone-aware UTC datetimes at parse time.

## 4. Data-quality policy

| Check | Rule |
|-------|------|
| Duplicate detection | No two rows share a PK; duplicates dropped, counted in manifest `skipped_duplicate` |
| Monotonic timestamps | Per `(canonical_id, venue, granularity/interval)`, `time_utc` strictly increasing after sort |
| Missing-interval classification | Expected grid from cadence; missing slots **logged, never interpolated** (mirrors spot gap policy) |
| Funding-interval consistency | Successive `funding_time_utc` deltas equal `funding_interval_hours` (within tolerance); irregular gaps flagged |
| Extreme-outlier checks | Funding outside ±0.3%/8h, OHLCV non-positive or `high<low`, basis_bps beyond a wide sanity band → WARN, retained + flagged |
| Symbol-mapping validation | Every native symbol resolves to an authorized canonical perp; unknown symbol → FAIL |
| Source-specific caveats | USDT-quote flag; Deribit funding-model flag; OI-history-depth limitation recorded per series |
| Cross-leg basis alignment | Basis only computed where both legs exist in the same UTC bucket; unmatched buckets excluded + counted |

Status levels mirror spot validation: `PASS` / `WARN` / `FAIL`.

## 5. Cost / fee placeholders (NO execution assumptions)

These are **placeholders for the future Family E diagnostics**, frozen in spirit like the spot cost model but **not** applied in this sprint (no diagnostics run).

| Item | Placeholder convention |
|------|------------------------|
| Taker fee (perp) | Document per-venue taker (e.g. Binance USDM taker ~0.04–0.05%); diagnostics use a conservative round-trip, pre-registered before any run |
| Maker fee (perp) | Recorded but diagnostics default to taker |
| **Funding cashflow direction** | **Long pays short when funding_rate > 0; short pays long when funding_rate < 0.** A long position's funding PnL over an interval = `− funding_rate × notional`; a short's = `+ funding_rate × notional`. This sign convention is the single source of truth for Phase 3 tests and Family E. |
| Spread proxy (perp) | Perp spreads are typically tighter than spot; a separate conservative perp half-spread placeholder is reserved (not the spot 5/8 bps) and pre-registered before diagnostics |
| Slippage | Fixed-bps proxy placeholder, pre-registered; no order-book simulation |
| Execution assumptions | **None in this sprint.** No fills, no PnL, no position sizing. |

The funding-direction convention above is the only cost rule this sprint *implements* (as a pure helper + test); everything else is reserved text for the diagnostics sprint.

## 6. Git policy

| Artifact | Committed? |
|----------|-----------|
| Raw fetched derivatives responses / bulk series | **No** — local-only, gitignored path |
| Local cache files, `.env`, keys, DB files | **No** |
| Compact per-fetch manifests (JSON, small) | **Yes** |
| Synthetic fixtures (funding/OI/mark/index/perp-OHLCV) | **Yes** |
| Small pilot fixtures (intentionally tiny, ≤ a handful of real rows) | **Yes, only if tiny** |
| Validation summary docs | **Yes** |

A `.gitignore` rule for `research/crypto/derivatives/raw/` (and any exports cache) is added in Phase 3/5 so raw data cannot be accidentally staged.

## 7. Loader interface (contract for Phase 3)

Minimal, storage-agnostic. The Phase 3 `derivatives_models.py` defines dataclasses (`FundingRateRecord`, `OpenInterestRecord`, `MarkIndexRecord`, `PerpOhlcvRecord`, `BasisRecord`) carrying the columns above; `derivatives_registry.py` resolves canonical↔venue symbols and enforces the BTC/ETH-only + perp-format guards; `derivatives_sources.py` parses raw venue payloads → these records and exposes the public-endpoint allowlist. No DB migration is forced this sprint — the canonical store binding (reuse Postgres vs parquet) is deferred to the backfill sprint; the dataclasses + manifests are the durable contract.

## 8. What is explicitly out of scope here

- No DB migration executed (loader/dataclass contract only).
- No funding signal, no basis signal, no OI signal — design only.
- No spot schema change.
- No altcoin / third-perp support.
- No execution/PnL modelling beyond the funding-direction sign helper.

---

## Related documents
- `CRYPTO_DATA_SCHEMA.md` (spot canonical schema)
- `CRYPTO_DERIVATIVES_PUBLIC_DATA_SOURCE_REVIEW.md` (source hierarchy)
- `CRYPTO_COST_MODEL_001.md` (frozen spot cost model — derivatives costs are a separate future freeze)
- `CRYPTO_DERIVATIVES_VALIDATION_POLICY.md` (Phase 4)
