# Crypto Derivatives Backfill 001 — Plan

**Sprint:** `crypto-derivatives-backfill-001`
**Branch:** `main`
**Date:** 2026-06-02
**Type:** Data backfill + frozen cost model ONLY. No factor, front gate, campaign, strategy, or approval.

---

## 1. Goal

Execute the recommended next step after `crypto-family-e-derivatives-data-prep-001`: backfill a real, validated, **BTC/ETH-only** derivatives dataset (funding, perp OHLCV, index, basis, open interest) and write+freeze a derivatives cost model — so the Family E exploratory diagnostics sprint's data-readiness gate can be met.

## 2. Source decision (revised for geo + depth + quote)

The prep sprint found Binance (451) and Bybit (403) geo-blocked here, and OKX `funding-rate-history` / `rubik` OI history are shallow (~months). Endpoint probing this sprint shows **Deribit** public API is the right primary:

| Class | Source | Why |
|-------|--------|-----|
| Funding (hourly, `interest_8h`/`interest_1h`) | **Deribit** `get_funding_rate_history` | USD-quoted, back to ~2019, ~744 rows/call; **includes hourly `index_price`** |
| Perp OHLCV (1H + 1D) | **Deribit** `get_tradingview_chart_data` | USD-quoted, back to ~2019, high per-call cap |
| Index price | **Deribit** (free in funding payload) | hourly, USD, aligned to funding |
| Basis | **derived** = perp_close − index_close | both USD, same venue → no USDT confound |
| Open interest (daily history) | **OKX** `rubik/.../open-interest-volume` | ~180d daily USD-notional (venue-aggregate); the residual depth gap |
| Open interest (snapshot) | Deribit `get_book_summary_by_instrument` | current OI |

**This resolves three prep-sprint problems at once:** the geo block (Deribit reachable), the USDT-vs-USD confound (Deribit perps are USD inverse), and most of the funding/price depth gap (~2019→now). Residual gap: deep per-instrument OI history (still only ~180d daily, aggregate).

Deribit funding is **continuous (hourly-realized)**; stored as hourly records (`funding_interval_hours=1`, rate = `interest_1h`, plus `interest_8h` retained). 8h resampling is a diagnostics-time step. Deribit is the canonical funding venue and is **not pooled** with 8h venues.

## 3. Scope

- Instruments: `BTC_PERP_USD`, `ETH_PERP_USD` only.
- Classes: funding (full), perp OHLCV 1H (full), perp OHLCV 1D (full), index (full, from funding), OI daily (OKX rubik ~180d), OI snapshot.
- Storage: normalized CSV under **gitignored** `research/crypto/derivatives/backfill/`; raw pages under gitignored `…/raw/`. Committed: compact per-class manifests + a compact validation summary JSON + docs.

## 4. Hard rules (unchanged from programme)

No strategy / campaign / front gate / approval. No edit to `configs/approved_strategies.yaml`. No paper/demo/live. No trading/order/account/private API; no keys. Public market-data only. Dry-run default; real fetch only behind `--execute-public-fetch`. BTC/ETH only. No factor/diagnostic run; no edge inference. No bulky raw/CSV/DB committed.

## 5. Deliverables

- `research/crypto/derivatives_backfill.py` (chunking helpers) + Deribit/OKX-rubik parsers in `derivatives_sources.py`.
- `scripts/backfill_crypto_derivatives.py` (dry-run default).
- `CRYPTO_DERIVATIVES_COST_MODEL_001.md` (FROZEN).
- Backfill manifests + `CRYPTO_DERIVATIVES_BACKFILL_001_RESULT.md` + summary.
- Tests for new parsers, chunking, cost constants.
- Updated readiness gate in the Family E next-prompt.

## 6. No-strategy / no-campaign / no-approval statement

This sprint backfills public data and freezes a cost model. It creates no strategy, campaign, front gate, or approval, runs no diagnostic, and infers no edge. BTC/ETH only; paper/demo/live blocked; `approved: []` unchanged.
