# Crypto Derivatives — Public Data Source Review (Family E Prep, Phase 1)

**Sprint:** `crypto-family-e-derivatives-data-prep-001` · Phase 1
**Date:** 2026-06-02
**Scope:** BTC and ETH perpetual/futures derivatives data — funding rates, open interest, mark/index price, perp OHLCV, spot/perp basis.
**Type:** Source review only. No factor, no campaign, no strategy. No private keys, no trading endpoints.

> Endpoint paths below reflect each venue's documented **public** market-data REST as of this review. Exact path/param/limit details MUST be re-confirmed against live docs at pilot time (Phase 5) before any fetch; the dry-run default and allowlist (Phase 3) are the enforcement mechanism, not this prose.

---

## 1. Hard constraints applied to every candidate

- **Public market-data only** — no authenticated, account, order, position, or leverage endpoints.
- **No API key** — any source that *requires* a key for funding/OI/mark/OHLCV is rejected for this layer.
- **Free** — no paid tiers, no paid historical archives.
- **Redistribution-safe** — we never commit bulky raw responses; only tiny derived fixtures and compact manifests. Raw is local-only/gitignored.
- **USD vs USDT honesty** — most deep-history perps are USDT-quoted (linear) or coin-margined inverse USD. Quote currency is recorded in provenance; USDT≠USD without basis adjustment.

---

## 2. Source comparison

| Source | BTC perp symbol | ETH perp symbol | Funding history | Open interest | Mark/Index | Perp OHLCV | Quote | Hist depth | Auth | Notes |
|--------|-----------------|-----------------|-----------------|---------------|------------|------------|-------|-----------|------|-------|
| **Binance USDⓈ-M** (`fapi.binance.com`) | `BTCUSDT` | `ETHUSDT` | ✓ `/fapi/v1/fundingRate` (8h), deep | Current ✓ `/fapi/v1/openInterest`; **hist ~30d only** `/futures/data/openInterestHist` | ✓ `/fapi/v1/premiumIndex`, markPriceKlines | ✓ `/fapi/v1/klines` | USDT | funding 2019→ | none | Deepest funding history; OI history shallow; **US-geo restricted** |
| **Binance COIN-M** (`dapi.binance.com`) | `BTCUSD_PERP` | `ETHUSD_PERP` | ✓ `/dapi/v1/fundingRate` | similar shallow hist | ✓ | ✓ | USD (inverse) | 2020→ | none | True USD-quoted; same geo caveat |
| **Bybit v5** (`api.bybit.com`) | `BTCUSDT` (linear), `BTCUSD` (inverse) | `ETHUSDT`/`ETHUSD` | ✓ `/v5/market/funding/history` (8h) | ✓ `/v5/market/open-interest` (5m–1d intervals, **hist available**) | ✓ tickers / mark-price-kline / index-price-kline | ✓ `/v5/market/kline` | USDT + USD | 2020/2021→ | none | Best free OI *history* coverage; clean v5 schema |
| **OKX v5** (`www.okx.com`) | `BTC-USDT-SWAP`, `BTC-USD-SWAP` | `ETH-USDT-SWAP`/`ETH-USD-SWAP` | ✓ `/api/v5/public/funding-rate-history` (8h) | ✓ `/api/v5/public/open-interest` (current) | ✓ mark-price-candles, index-candles | ✓ `/api/v5/market/candles` | USDT + USD | 2020→ | none | Good funding+candles; OI history limited |
| **Kraken Futures** (`futures.kraken.com/derivatives/api/v3`) | `PI_XBTUSD` (inverse perp) | `PI_ETHUSD` | ✓ `/historicalfundingrates` | ticker `openInterest` (current) | ✓ ticker mark/index | ✓ via charts API | USD (inverse) | 2019→ | none | **US-accessible**; true USD; thinner OI history |
| **Deribit** (`www.deribit.com/api/v2`) | `BTC-PERPETUAL` | `ETH-PERPETUAL` | ✓ `/public/get_funding_rate_history` (hourly realized) | ✓ via instrument summary | ✓ mark/index in ticker | ✓ `/public/get_tradingview_chart_data` | USD (inverse) | 2019→ | none | Continuous funding model differs (per-hour); options-centric venue |
| **Coinbase Intl / Derivatives** | (INTX perp) | (INTX perp) | partial | partial | partial | partial | USD | short | **often auth/geo-gated** | Rejected as primary — public funding/OI access unreliable |
| **CCXT** (adapter, not a venue) | unified | unified | `fetch_funding_rate_history` | `fetch_open_interest_history` | `fetch_ticker` | `fetch_ohlcv` | per-venue | per-venue | none for public | Wraps the above; adds a heavy dependency + abstraction layer |

---

## 3. Per-class availability assessment

### Funding rate history
Strong and free across Binance, Bybit, OKX, Kraken Futures, Deribit. Standard model is **8-hour discrete funding** (Binance/Bybit/OKX/Kraken); **Deribit uses a continuous/hourly-realized** model — do not pool Deribit funding with 8h venues without normalization. Binance USDⓈ-M has the deepest, most-cited funding history.

### Open interest
**This is the binding free-data gap.** Most venues expose *current* OI freely but **historical** OI is shallow:
- Binance `openInterestHist`: ~30 days rolling only (free).
- Bybit `open-interest`: best free historical OI window with selectable intervals — **preferred for OI history**.
- OKX/Kraken/Deribit: current or short history.
Deep multi-year OI history generally requires paid aggregators (Coinglass/Laevitas) — **out of scope** (paid). The honest position: OI diagnostics start *forward-collecting* from pilot date plus whatever short rolling history each venue gives. Documented as a known limitation, not papered over.

### Mark / index price
Freely available everywhere (premiumIndex / mark-price-kline / index-price-kline / ticker). Index price (spot composite) is the basis reference; mark price is the funding/liquidation reference.

### Perp OHLCV
Freely available everywhere. Note: perp OHLCV is *separate* from the existing Coinbase **spot** OHLCV already in the store.

### Spot/perp basis
Computable: `basis = perp_mark (or perp_close) − spot_index (or Coinbase spot close)`, aligned on UTC bar open. Both legs are available free. Annualized-basis and basis-bps variants documented in the data model (Phase 2).

---

## 4. Selected initial source hierarchy

| Role | Source | Rationale |
|------|--------|-----------|
| **Primary — funding + mark/index + perp OHLCV** | **Binance USDⓈ-M public REST** | Deepest free funding history, well-documented, no key, stable schema |
| **Primary — open-interest history** | **Bybit v5 public REST** | Best free historical OI window with interval selection |
| **USD-quoted cross-check (anti-USDT-bias)** | **Kraken Futures public** (`PI_XBTUSD`/`PI_ETHUSD`) | True USD inverse perps; US-accessible; sanity-checks USDT-quoted Binance |
| **Tertiary / redundancy** | OKX v5, Deribit | Funding/candles redundancy; Deribit only with funding-model normalization |
| **Rejected as primary** | Coinbase Intl/Derivatives | Public funding/OI access unreliable / auth-gated |
| **Adapter** | CCXT | **Not adopted** — see §6 |

**Canonical research series** will pin one venue per data class (Binance USDⓈ-M for funding/mark/perp-OHLCV; Bybit for OI), with the others stored as cross-venue validation samples only — mirroring the spot decision to pin Coinbase as canonical.

**Geo caveat:** Binance public endpoints may be unreachable from some networks (e.g. US). If the pilot host cannot reach Binance, the hierarchy **fails over to Bybit (funding/OHLCV) + Kraken Futures (USD reference)**, and the pilot doc records the substitution. No VPN / evasion is used.

## 5. Rejected sources and why

| Source | Reason |
|--------|--------|
| Coinglass / Laevitas / Amberdata | Paid (or key-gated) for historical OI/funding archives — violates no-paid-data rule |
| Coinbase International derivatives | Public funding/OI access unreliable, frequently auth/geo-gated |
| Any authenticated REST/WebSocket private channel | Requires keys — violates no-private-key rule |
| FTX-era archives | Defunct venue; not reproducible |

## 6. Direct HTTP vs CCXT adapter — decision

**Decision: direct HTTP (`httpx`), matching the existing repo convention.**

- The spot layer (`research/crypto/coinbase.py`) already uses direct `httpx` + `tenacity`; reusing that pattern keeps one fetch idiom and avoids a large new dependency surface.
- CCXT would unify symbols but pulls in a heavy dependency, obscures the exact public-URL being hit (harder to enforce a public-endpoint allowlist and credential-refusal guard), and complicates the "refuse non-public base URL" safety check.
- CCXT remains documented as an optional fallback if a venue's raw schema proves unstable; it is **not** adopted in this sprint.

## 7. Data rights / redistribution caveats

- Exchange market data is provided for informational use; **bulk raw responses are never committed**. Only tiny derived fixtures (synthetic-shaped or ≤ a handful of real rows) and compact manifests/validation summaries enter git.
- Raw fetched data is written under a gitignored local path only.
- Provenance records source venue, native symbol, canonical symbol, fetch time, and quote currency for every series.

## 8. No-private-key / no-trading confirmation

Every selected endpoint is a **public market-data** endpoint requiring no API key, no signature, and no account. No order, position, leverage, margin, or account endpoint appears anywhere in this layer. The Phase 3 adapter enforces this with a public-base-URL allowlist and a guard that refuses to run if an API-key-shaped env var would be required.

## 9. Outputs feeding later phases

- Canonical perp symbols → Phase 2 registry (`BTC_PERP_USD`, `ETH_PERP_USD`) with venue-native maps (`BTCUSDT`, `PI_XBTUSD`, …).
- Data-class availability + OI-history limitation → Phase 2 data model and Phase 4 validation policy.
- Source hierarchy + failover → Phase 3 sources adapter allowlist and Phase 5 pilot plan.
