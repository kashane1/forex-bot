# Crypto Data — Source Evaluation (Phase 1)

**Sprint:** `crypto-data-design-001` · Phase 1
**Date:** 2026-05-31
**Universe:** BTC/USD, ETH/USD spot only
**Type:** Design evaluation only. No API calls made in this sprint.

---

## Evaluation criteria

| Criterion | Weight | Notes |
|-----------|--------|-------|
| Historical depth | High | ≥5y required; ≥10y desirable for BTC |
| Granularity | High | 1m base preferred; 5m minimum acceptable for v1 |
| Cost | High | Free/low-cost public endpoints preferred |
| Bid/ask availability | Medium | Required for cost realism; accept spread proxy if unavailable |
| USD denomination | Medium | True USD pairs preferred over USDT proxy |
| Reliability / licensing | Medium | Public market data; document ToS |
| Reproducibility | High | Stable API, paginated history, UTC timestamps |

---

## Exchange APIs

### Coinbase Advanced Trade / Exchange API

| Dimension | Assessment |
|-----------|------------|
| Pairs | `BTC-USD`, `ETH-USD` (true USD) |
| Granularity | 1m, 5m, 15m, 1h, 6h, 1d via `GET /products/{product_id}/candles` |
| History | BTC: ~2015+ on Coinbase; ETH: ~2016+ |
| Bid/ask in candles | **No** — candles are mid OHLCV (open/high/low/close/volume) |
| Rate limits | Public endpoints; documented per-route limits (typically low hundreds req/min per IP — verify at implementation time) |
| Auth | Public candles: no key required |
| Licensing | Exchange ToS; research use with attribution |
| Pros | True USD denomination; US-regulated venue; clean symbol mapping |
| Cons | Mid-only candles; shallower 1m history than Binance for some windows |

**Verdict:** Strong **primary candidate** for canonical USD-denominated series.

### Binance Spot REST API

| Dimension | Assessment |
|-----------|------------|
| Pairs | `BTCUSDT`, `ETHUSDT` (USDT ≈ USD with basis risk) |
| Granularity | 1s–1M via `GET /api/v3/klines`; 1m well supported |
| History | BTCUSDT since ~2017; deep 1m archive |
| Bid/ask in candles | **No** — klines are mid OHLCV + quote volume |
| Rate limits | Weight-based: `klines` weight 1–2; REQUEST_WEIGHT 6,000/min (2026 docs); max 1,000 klines/request |
| Auth | Public market data: no key required |
| Licensing | Binance ToS; geo-restrictions may apply |
| Pros | Deepest free 1m history; high liquidity; chunk-friendly pagination |
| Cons | USDT not USD; regulatory/geo access; venue-specific microstructure |

**Verdict:** Strong **secondary / depth backup** and cross-venue sanity check. Map to `BTC/USD` with documented USDT basis caveat.

### Kraken REST API

| Dimension | Assessment |
|-----------|------------|
| Pairs | `XBT/USD`, `ETH/USD` (true USD) |
| Granularity | 1, 5, 15, 30, 60, 240, 1440, 10080, 21600 minutes via `OHLC` |
| History | BTC USD: long; ETH: ~2017+ |
| Bid/ask in candles | **No** — OHLC + volume + vwap in public OHLC endpoint |
| Rate limits | Tiered by call counter (~1 req/s public tier — verify at implementation) |
| Auth | Public OHLC: no key required |
| Pros | True USD; independent venue for cross-check |
| Cons | Slower pagination; smaller 1m depth than Binance for some eras |

**Verdict:** **Cross-venue validation** source, not primary canonical.

### Gemini, Bitstamp, Crypto.com

| Dimension | Assessment |
|-----------|------------|
| Pairs | BTC/USD, ETH/USD available on each |
| History | Shorter or comparable to Coinbase for 1m |
| Bid/ask | Generally mid-only in public candle endpoints |
| Verdict | **Optional tertiary** cross-checks; not needed for v1 |

---

## Aggregator APIs

### CryptoCompare

| Dimension | Assessment |
|-----------|------------|
| Data | Multi-exchange aggregated OHLCV |
| Free tier | Limited calls/day; historical depth varies by endpoint |
| Bid/ask | Some endpoints; free tier restrictive |
| Pros | Single API for multi-venue |
| Cons | Free tier too limited for full 1m×5y×2 assets backfill; licensing for commercial use |

**Verdict:** **Not primary** for v1. Consider if exchange-direct ingestion proves unreliable.

### CoinGecko

| Dimension | Assessment |
|-----------|------------|
| Data | Market charts, OHLC on free tier |
| Granularity | Auto-granularity: daily beyond 90d; hourly/daily only for long history on free tier |
| Bid/ask | No |
| Verdict | **Insufficient** for 1m/5m research base. Useful for spot-checks only.

---

## Public datasets

| Source | Assessment |
|--------|------------|
| Kaggle crypto OHLCV bundles | Variable quality; provenance often unclear; good for smoke tests only |
| Academic (Kaiko sample, etc.) | Usually paid or sample-limited |
| Binance public data dumps | Periodic bulk files; good for one-time backfill if available for spot 1m |

**Verdict:** Bulk dumps may accelerate **authorized** ingestion sprint; not used in design sprint.

---

## Trade-off matrix (summary)

| Source | Cost | History (1m) | USD native | Bid/ask | Reliability | Recommendation |
|--------|------|--------------|------------|---------|-------------|----------------|
| Coinbase | Free | Good | Yes | No (mid) | High | **Primary canonical** |
| Binance | Free | Excellent | No (USDT) | No (mid) | High | **Secondary / depth** |
| Kraken | Free | Good | Yes | No (mid) | Medium | **Cross-venue check** |
| CryptoCompare | Free/paid | Medium | Mixed | Partial | Medium | Fallback |
| CoinGecko | Free | Poor (1m) | Mixed | No | Medium | Not for v1 |

---

## Decision (Phase 1)

### Primary canonical source

**Coinbase `BTC-USD` and `ETH-USD`** spot candles.

- True USD denomination matches programme symbol naming (`BTC/USD`, `ETH/USD`)
- Sufficient history for 5y minimum (BTC >10y)
- Clean regulatory/operational story for a conservative research programme

### Secondary source

**Binance `BTCUSDT` / `ETHUSDT`** for:

- Deeper 1m history where Coinbase gaps exist
- Cross-venue price consistency checks
- Document **USDT basis risk** when comparing to USD canonical

### Cross-venue validation source

**Kraken `XBT/USD` / `ETH/USD`** — sample-window comparison only (not dual canonical).

### Bid/ask gap mitigation

None of the free public candle endpoints provide full bid/ask OHLC. Mitigation (locked for Phase 3 cost model):

1. **Conservative half-spread proxy** applied to mid OHLC (venue-specific bps table)
2. Optional: periodic `bookTicker` / depth snapshots for spread calibration (separate lightweight fetch, not required for v1 backfill)
3. Document spread assumptions in provenance sidecar; stress at 2× spread

### Ingestion authorization gate

No bulk ingestion until:

- This document reviewed ✓
- `CRYPTO_DATA_SCHEMA.md` complete
- `CRYPTO_DATA_VALIDATION_REQUIREMENTS.md` complete (includes cost model)

---

## References

- [Binance Spot API — klines](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints)
- [Binance API limits](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/limits)
- Coinbase Advanced Trade API — product candles (verify current docs at implementation)
- Kraken REST OHLC endpoint (verify current docs at implementation)
