# Crypto Derivatives Backfill 001 — Result

**Sprint:** `crypto-derivatives-backfill-001`
**Date:** 2026-06-02
**Type:** Public-data backfill. No factor, campaign, strategy, approval, or edge inference.

---

## 1. Outcome

A real, validated, **USD-quoted, ~6.4-year** BTC/ETH perpetual derivatives dataset was backfilled from public endpoints. Overall validation **WARN** (not FAIL) — driven solely by minor funding gaps and the known shallow-OI gap; both are logged-not-interpolated per policy.

## 2. Commands run

```
python scripts/backfill_crypto_derivatives.py --start 2020-01-01 --execute-public-fetch
```
(dry-run is the default; the real fetch ran only behind `--execute-public-fetch`.)

## 3. Sources used

| Class | Source | Quote |
|-------|--------|-------|
| Funding (hourly realized) + index | Deribit `get_funding_rate_history` | USD |
| Perp OHLCV (H1, D1) | Deribit `get_tradingview_chart_data` | USD |
| Basis (derived) | perp close − index close | USD |
| Open interest (daily) | OKX `rubik/.../open-interest-volume` | USD notional (venue-aggregate) |

Binance (HTTP 451) and Bybit (403) remained geo-blocked; Deribit (USD inverse perps) resolved both the geo block and the USDT-vs-USD confound.

## 4. Rows fetched & validation

| Instrument | Funding (1h) | Index (1h) | OHLCV H1 | OHLCV D1 | Basis H1 | OI daily | Status |
|------------|-------------|-----------|----------|----------|----------|----------|--------|
| BTC_PERP_USD | 56,186 | 56,186 | 56,267 | 2,345 | 56,186 | 180 | WARN (funding_gap) |
| ETH_PERP_USD | 56,186 | 56,186 | 56,267 | 2,345 | 56,186 | 180 | WARN (funding_gap) |

- **Funding window:** 2020-01-01 → 2026-06-02; **hourly coverage 99.86%**; **79 gaps** each (occasional missing hours over 6.4y — logged, not interpolated).
- Perp OHLCV, index, OI all validated **PASS** (monotonic, no dupes, OHLC sane).

## 5. Sanity (informational only — NOT a signal, NO edge claimed)

| Metric | BTC | ETH |
|--------|-----|-----|
| Funding rate (1h realized) mean | +8.3e-6 | +6.2e-6 |
| Funding rate range | −6.6e-4 … +4.7e-4 | −1.35e-3 … +6.4e-4 |
| Basis median (bps) | +2.44 | +2.41 |

Mildly positive funding (longs pay shorts on average) and small positive basis (perp slightly above index) — textbook mild contango. Plausible, not interpreted as predictive.

## 6. Storage & git policy

- Normalized CSVs under `research/crypto/derivatives/backfill/<inst>/` — **gitignored** (bulky/regenerable).
- Committed: per-batch manifest (`…/manifests/backfill/<batch>.json`) + validation summary (`…/summaries/backfill_001_validation.json`). No raw payloads, no CSVs, no credentials.

## 7. Residual gaps / caveats

- **Deep per-instrument OI history** is still missing — only OKX rubik daily **aggregate** (~180d, USD-notional) is free here. Per-instrument multi-year OI needs a paid aggregator (out of scope) or forward collection. OI-dependent diagnostics (4, 5) are therefore low-power until depth accrues.
- Deribit funding is **continuous/hourly** (`funding_interval_hours = 1`); 8h-cadence diagnostics resample by summing `interest_1h`. Not pooled with 8h venues.
- OI quote = USD-notional aggregate (not per-instrument contracts); document when used.
- 79 hourly funding gaps each — declare gap tolerance in diagnostics.

## 8. Readiness verdict

| Diagnostic (design doc) | Data ready? |
|-------------------------|-------------|
| 1 Funding mean reversion | **Yes** (funding + perp OHLCV, 6.4y) |
| 2 Funding trend continuation | **Yes** |
| 3 Basis compression/expansion | **Yes** (basis_h1, 6.4y, USD) |
| 6 Cross-asset confirmation | **Yes** (BTC+ETH both) |
| 7 Regime conditioning | **Yes** (on 1–3) |
| 4 OI impulse | **Low-power** (180d OI only) |
| 5 Funding/OI interaction | **Low-power** (180d OI only) |

Plus the **frozen** `CRYPTO_DERIVATIVES_COST_MODEL_001.md`. **The Family E data-readiness gate is now met for diagnostics 1–3, 6, 7.**

## 9. No-strategy / no-campaign / no-approval statement

This sprint backfilled public data and froze a cost model. No strategy, campaign, front gate, or approval was created; no diagnostic was run; no edge inferred. No trading/private/order API; no keys. BTC/ETH only; `approved: []`; paper/demo/live blocked.
