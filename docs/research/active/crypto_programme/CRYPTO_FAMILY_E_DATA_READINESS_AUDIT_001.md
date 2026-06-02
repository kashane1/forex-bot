# Crypto Family E — Data Readiness Audit 001 (Phase 3)

**Sprint:** `crypto-family-e-exploratory-diagnostics-001`
**Date:** 2026-06-02
**Type:** Preflight data audit — no diagnostics executed in this phase.

Generated from `scripts/run_crypto_family_e_exploratory_diagnostics.py` (preflight mode) →
`research/crypto/family_e_diagnostics/{data_readiness.json,run_manifest.json}`.

---

## 1. Paths used

- Backfill (gitignored): `research/crypto/derivatives/backfill/<inst>/{funding,ohlcv_h1,ohlcv_d1,index_h1,basis_h1,oi_daily}.csv`
- Instruments: `BTC_PERP_USD`, `ETH_PERP_USD` (BTC/ETH-only guard enforced).
- Venue: Deribit USD inverse perps (canonical). OI from OKX rubik (venue-aggregate).

## 2. Data windows & row counts (per instrument; BTC and ETH identical)

| Series | Rows | Note |
|--------|-----:|------|
| Funding (1h realized) | 56,186 | 2020-01-01 → 2026-06-02, ~99.86% cov, 79 hourly gaps |
| 8h funding windows (complete, summed) | 6,953 | settlement-aligned 00/08/16 UTC; incomplete windows dropped |
| Perp OHLCV H1 | 56,267 | open-to-open returns |
| Index H1 | 56,186 | — |
| Basis H1 (`basis_bps`) | 56,186 | USD, perp_close − index_close |
| OI daily | 180 | **SHALLOW** — OKX aggregate USD-notional |

## 3. Gaps & skipped-window policy

No interpolation. A signal window or forward-return window crossing any missing
funding / index / OHLCV bar is **skipped and counted**. Skips scale with horizon
(longer holds touch more hours):

## 4. Eligible observations by diagnostic / horizon (machine-computed)

| Diagnostic | Horizon | BTC eligible | BTC skipped | ETH eligible | ETH skipped |
|-----------|--------:|------------:|-----------:|------------:|-----------:|
| 1 Funding mean reversion | 8h | 6,873 | 80 | 6,873 | 80 |
| 1 Funding mean reversion | 24h | 6,713 | 240 | 6,713 | 240 |
| 1 Funding mean reversion | 72h | 6,239 | 714 | 6,239 | 714 |
| 2 Continuation k=3 | 24h | 6,710 | 240 | 6,710 | 240 |
| 2 Continuation k=3 | 72h | 6,236 | 714 | 6,236 | 714 |
| 2 Continuation k=6 | 24h | 6,707 | 240 | 6,707 | 240 |
| 2 Continuation k=6 | 72h | 6,233 | 714 | 6,233 | 714 |
| 2 Continuation k=9 | 24h | 6,704 | 240 | 6,704 | 240 |
| 2 Continuation k=9 | 72h | 6,230 | 714 | 6,230 | 714 |
| 3 Basis | 4h | 55,865 | 321 | 55,865 | 321 |
| 3 Basis | 24h | 54,265 | 1,921 | 54,265 | 1,921 |

Decile cohorts (diag 1, 3) are ~20% of the eligible sample (top+bottom decile) —
all comfortably above the `MIN_COHORT = 100` evaluation floor. Persistence cohorts
(diag 2) are the same-sign subsets of the eligible windows.

## 5. OI limitation (binding gap)

| Instrument | OI rows | Low-power? |
|-----------|--------:|:----------:|
| BTC_PERP_USD | 180 | yes |
| ETH_PERP_USD | 180 | yes |

Only ~180d aggregate daily OI is freely available (OKX rubik, venue-aggregate USD
notional — not per-instrument contracts). This is the binding gap for diagnostics 4
and 5; they are **low-power by construction** and default to `blocked_low_power_oi`.

## 6. Pass / warn / fail status

| Gate | Status |
|------|--------|
| Funding (BTC+ETH) | **PASS** |
| Perp OHLCV (BTC+ETH) | **PASS** |
| Index (BTC+ETH) | **PASS** |
| Basis (BTC+ETH) | **PASS** |
| Cost model frozen & loaded | **PASS** (`CRYPTO_DERIVATIVES_COST_MODEL_001.md`) |
| OI depth | **WARN** (low-power; 180d aggregate) |

## 7. Which diagnostics may run

- **Diagnostics 1, 2, 3, 6, 7 — high-power, RUN.** Funding/basis coverage 6.4y, deep eligible samples.
- **Diagnostics 4, 5 — low-power only.** Run as explicitly-labeled `blocked_low_power_oi`; may **not** reach `candidate_for_front_gate` from this OI sample.

## 8. No-strategy / no-campaign statement

This preflight audit creates no strategy, campaign, front gate, or approval. BTC/ETH only.
`approved: []`. Paper/demo/live remain blocked.
