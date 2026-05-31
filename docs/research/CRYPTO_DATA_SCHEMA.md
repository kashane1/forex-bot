# Crypto Data — Canonical Schema (Phase 2)

**Sprint:** `crypto-data-design-001` · Phase 2
**Date:** 2026-05-31
**Universe:** BTC/USD, ETH/USD
**Type:** Schema design only. No data committed.

---

## Design principles

1. **Mirror forex provenance discipline** — same fields the programme already validates (source, batch ID, hash, UTC timestamps).
2. **Spot-first** — futures/funding/OI as nullable extension columns / separate tables, not blocking v1.
3. **Continuous market** — no session fields; UTC bar open time is the canonical key.
4. **Mid OHLCV + spread proxy** — public APIs deliver mid; bid/ask derived or proxied until optional book snapshots exist.

---

## Symbol mapping

| Programme symbol | Canonical instrument ID | Coinbase product | Binance symbol | Kraken pair |
|------------------|-------------------------|------------------|----------------|-------------|
| BTC/USD | `BTC_USD` | `BTC-USD` | `BTCUSDT`¹ | `XBT/USD` |
| ETH/USD | `ETH_USD` | `ETH-USD` | `ETHUSDT`¹ | `ETH/USD` |

¹ Binance USDT pairs stored with `quote_ccy=USDT` in provenance; not interchangeable with USD canonical without basis adjustment.

**Internal convention:** `{BASE}_{QUOTE}` underscore-separated, matching OANDA `EUR_USD` pattern for code reuse.

---

## Postgres schema (proposed)

Extend existing research schema with a crypto namespace. Two options for implementation sprint:

| Option | Description |
|--------|-------------|
| **A (preferred)** | Reuse `market_data.candles` with `asset_class='crypto'` column |
| **B** | Separate schema `crypto_market_data.candles` identical column layout |

Option A minimizes duplication; Option B isolates forex validation scripts. **Recommend A** with `asset_class` discriminator unless archive scripts break.

### Table: `instruments` (extended)

| Column | Type | Notes |
|--------|------|-------|
| instrument | TEXT PK | `BTC_USD`, `ETH_USD` |
| asset_class | TEXT | `crypto` |
| base_ccy | TEXT | `BTC`, `ETH` |
| quote_ccy | TEXT | `USD` |
| venue_symbol | TEXT | e.g. `BTC-USD` |
| venue | TEXT | `coinbase`, `binance`, `kraken` |
| tick_size | NUMERIC | venue minimum price increment |
| lot_size | NUMERIC | venue minimum quantity increment |
| source | TEXT | ingestion source label |
| updated_at_utc | TIMESTAMPTZ | |

### Table: `candles` (spot v1)

| Column | Type | Notes |
|--------|------|-------|
| instrument | TEXT | `BTC_USD` / `ETH_USD` |
| asset_class | TEXT | `crypto` |
| granularity | TEXT | `M1`, `M5`, `M15`, `H1`, `H4`, `D1` |
| time_utc | TIMESTAMPTZ | **Bar open** time, UTC |
| complete | BOOLEAN | Always true for historical; false only for live tail if ever used |
| volume | NUMERIC | Base-asset volume |
| quote_volume | NUMERIC | Optional quote-volume from exchange |
| mid_o, mid_h, mid_l, mid_c | DOUBLE PRECISION | Primary OHLC from exchange |
| bid_o … bid_c | DOUBLE PRECISION | Nullable; derived from mid − half_spread if proxied |
| ask_o … ask_c | DOUBLE PRECISION | Nullable; derived from mid + half_spread if proxied |
| spread_open … spread_close | DOUBLE PRECISION | Nullable; bps or absolute |
| half_spread_bps_assumed | DOUBLE PRECISION | Document when bid/ask proxied |
| source | TEXT | e.g. `coinbase-spot` |
| venue | TEXT | |
| fetch_batch_id | TEXT | UUID per ingestion run |
| data_hash | TEXT | SHA-256 of normalized row payload |
| fetched_at_utc | TIMESTAMPTZ | |
| PRIMARY KEY | | `(instrument, granularity, time_utc, venue)` |

**Note:** Composite PK includes `venue` when storing multi-venue raw series. Canonical research series uses `venue='coinbase'` (primary) only; others in `candles_raw` or same table with `is_canonical=false` flag.

Simpler v1: **single canonical venue per instrument** in main table; cross-venue data in `research/crypto/cross_venue/` CSV sidecars for validation only.

---

## CSV export format (parity / offline research)

Mirror Lean parity layout for adapter reuse:

| Column | Description |
|--------|-------------|
| time | ISO-8601 UTC bar open |
| mid_open, mid_high, mid_low, mid_close | |
| bid_* / ask_* | Optional; empty if proxied |
| volume | |
| half_spread_close | bps or absolute; for cost engine |

Sidecar: `{instrument}_{granularity}_crypto.provenance.json`

---

## Provenance sidecar (required fields)

```json
{
  "instrument": "BTC_USD",
  "granularity": "M1",
  "asset_class": "crypto",
  "venue": "coinbase",
  "venue_symbol": "BTC-USD",
  "source": "coinbase-advanced-trade-candles",
  "requested_from": "2020-01-01T00:00:00Z",
  "requested_to": "2026-05-31T00:00:00Z",
  "candle_count": 0,
  "first_ts": "",
  "last_ts": "",
  "data_sha256": "",
  "fetch_batch_id": "",
  "fetched_at_utc": "",
  "gap_policy": "missing_bar_logged_not_interpolated",
  "spread_policy": "half_spread_bps_assumed",
  "half_spread_bps_assumed": 5.0,
  "attribution": "Coinbase public market data; research use.",
  "note_no_api_key": "API keys read from env if needed; NEVER committed."
}
```

---

## Timezone policy

- All storage and APIs: **UTC**
- Bar timestamp = **open time** of the interval (match Binance/Coinbase convention)
- Materialization aligns to UTC boundaries (no NY-close D1 like forex D1AGG)

---

## Gap / missing-bar policy

1. **Do not interpolate** missing bars — log gap in manifest
2. Incomplete trailing bar excluded from historical backfill (`complete=true` only)
3. Gap report per instrument: `{start, end, expected_bars, actual_bars, missing_ranges[]}`
4. Research diagnostics must declare gap tolerance (Family C persistence may use higher TFs where gaps are rare)

---

## Materialized timeframe requirements

| Granularity | Source | Role |
|-------------|--------|------|
| M1 | Ingested (primary base) | Raw store; M1 persistence diagnostics |
| M5 | Materialized from M1 | Execution diagnostics |
| M15 | Materialized from M1 | Execution diagnostics |
| H1 | Materialized from M1 | Context |
| H4 | Materialized from M1 | Regime context |
| D1 | Materialized from M1 | Slow momentum / regime (Family C) |

**Aggregation rules:** reuse `m1_timeframe_materialization` logic — UTC-aligned bucket open, OHLCV standard rules, volume sum, `MATERIALIZED_SOURCE` tag in provenance.

**Config hash:** store `aggregation_config_hash` in materialization manifest (same pattern as forex M1 corpus).

Optional v1 shortcut: ingest M5+ directly from exchange for initial **5y window** while M1 backfill runs in authorized sprint — document in ingestion plan; canonical store still targets M1 base.

---

## Futures / funding / OI hooks (schema only)

### Table: `perpetual_markets` (future)

| Column | Notes |
|--------|-------|
| instrument | `BTC_USD_PERP` |
| underlying | `BTC_USD` |
| venue | `binance-futures`, etc. |
| contract_type | `perpetual` |

### Table: `funding_rates` (future — Family E)

| Column | Notes |
|--------|-------|
| instrument | perpetual ID |
| funding_time_utc | 8h typical |
| funding_rate | signed decimal |
| source, fetch_batch_id, data_hash | provenance |

### Table: `open_interest` (future — Family E)

| Column | Notes |
|--------|-------|
| instrument | |
| time_utc | |
| open_interest | contracts or USD notional |
| source | |

**v1 action:** none — document hooks only. Spot `candles` table unchanged.

---

## File layout (research artifacts)

```
research/crypto/
├── registry.py              # symbol map (future code)
├── ingest/                  # venue adapters (future)
├── manifests/               # per-batch ingestion manifests
├── cross_venue/             # validation CSVs (small samples only)
└── materialization/         # aggregation manifests
```

No files created in this sprint except documentation.

---

## Mapping to existing `CandleRecord`

Forex `CandleRecord` maps directly:

| Forex field | Crypto v1 |
|-------------|-----------|
| instrument | `BTC_USD` |
| granularity | `M1`…`D1` |
| time_utc | bar open UTC |
| complete | true |
| volume | base volume |
| mid_* | from exchange |
| bid_* / ask_* | proxied or null |
| source / fetch_batch_id / data_hash | same |

Extend `PostgresCandleStore.upsert_candles` with optional `asset_class` filter — implementation sprint only.
